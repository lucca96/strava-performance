import argparse
import csv
import json
import sys
from pathlib import Path

from src.analysis import build_activity_record, classify_activity, estimate_hr_max, render_report, upsert_history
from src.ai_ready_report import write_ai_ready_report
from src.client import ApiBudgetExceeded, StravaClient
from src.weekly_report import write_all_weekly_reports, write_weekly_report


DATA_DIR = Path("data")
INDEX_PATH = DATA_DIR / "cache" / "activity_index.json"
HISTORY_PATH = DATA_DIR / "performance_history.csv"
REPORTS_DIR = DATA_DIR / "reports"
WEEKLY_REPORTS_DIR = DATA_DIR / "weekly_reports"
AI_REPORTS_DIR = DATA_DIR / "ai_reports"
PER_PAGE = 30

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def build_local_index_from_cache(data_dir=None):
    data_dir = data_dir or DATA_DIR
    summary_dir = data_dir / "cache" / "summary_pages"
    activities_by_id = {}
    complete = False
    cached_pages = []

    if summary_dir.exists():
        for path in sorted(summary_dir.glob("page_*.json")):
            page = int(path.stem.split("_")[1])
            cached_pages.append(page)
            page_activities = load_json(path, [])
            if not page_activities:
                complete = True
            for activity in page_activities:
                activities_by_id[str(activity["id"])] = activity

    activities = sorted(
        activities_by_id.values(),
        key=lambda activity: activity.get("start_date_local") or activity.get("start_date") or "",
    )
    return {
        "complete": complete,
        "cached_pages": cached_pages,
        "activities": activities,
    }


def save_index(index):
    write_json(INDEX_PATH, index)


def load_index():
    if INDEX_PATH.exists():
        return load_json(INDEX_PATH, {"complete": False, "cached_pages": [], "activities": []})
    index = build_local_index_from_cache()
    save_index(index)
    return index


def next_uncached_summary_page(index):
    cached_pages = set(index.get("cached_pages", []))
    page = 1
    while page in cached_pages:
        page += 1
    return page


def cmd_index(client):
    client.ensure_dirs()
    index = load_index()

    while not index.get("complete"):
        page = next_uncached_summary_page(index)
        activities = client.get_summary_page(page, per_page=PER_PAGE)
        index = build_local_index_from_cache()
        save_index(index)

        if not activities or client.calls_remaining <= 0:
            break

    print_status(client, "index", f"{len(index.get('activities', []))} atividades indexadas")
    return index


def refresh_latest_summary_page(client):
    client.get_summary_page(1, per_page=PER_PAGE, force_refresh=True)
    index = build_local_index_from_cache()
    save_index(index)
    return index


def history_activity_ids():
    if not HISTORY_PATH.exists():
        return set()
    with open(HISTORY_PATH, "r", encoding="utf-8-sig", newline="") as file:
        return {str(row.get("activity_id")) for row in csv.DictReader(file) if row.get("activity_id")}


def is_activity_complete(activity, history_ids=None):
    history_ids = history_ids or history_activity_ids()
    activity_id = str(activity["id"])
    base = DATA_DIR / "cache" / "activities" / activity_id
    if not (base / "details.json").exists() or not (base / "streams.json").exists():
        return False
    if activity.get("type") in {"Run", "Walk"} and not (base / "laps.json").exists():
        return False
    if activity_id not in history_ids:
        return False
    if not (REPORTS_DIR / f"{activity_id}.md").exists():
        return False
    return True


def find_next_hr_activity(index):
    activities = [a for a in index.get("activities", []) if a.get("has_heartrate")]
    history_ids = history_activity_ids()
    for activity in activities:
        if not is_activity_complete(activity, history_ids=history_ids):
            return activity
    return None


def get_activity_from_index(activity_id):
    index = load_index()
    for activity in index.get("activities", []):
        if str(activity.get("id")) == str(activity_id):
            return activity
    return None


def analyze_activity(client, activity):
    activity_id = activity["id"]
    details = client.get_activity_details(activity_id)
    streams = client.get_activity_streams(activity_id)
    laps = None

    if (activity.get("type") or details.get("type")) in {"Run", "Walk"}:
        laps = client.get_activity_laps(activity_id)

    index = load_index()
    hr_max = estimate_hr_max(index.get("activities", []))
    if not hr_max:
        hr_max = details.get("max_heartrate")

    record = build_activity_record(activity, details, streams=streams, laps=laps, hr_max=hr_max)
    upsert_history(record, HISTORY_PATH)
    write_report(record)
    return record


def write_report(record):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{record['activity_id']}.md"
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(render_report(record))
    return report_path


def regenerate_reports_from_history():
    if not HISTORY_PATH.exists():
        return 0

    count = 0
    rows = []
    fieldnames = []
    with open(HISTORY_PATH, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = list(reader.fieldnames or [])
        for record in reader:
            if not record.get("activity_id"):
                continue
            if not record.get("activity_category"):
                record["activity_category"] = classify_activity(record.get("name"))
            write_report(record)
            rows.append(record)
            count += 1

    if rows:
        for column in ["activity_category"]:
            if column not in fieldnames:
                fieldnames.append(column)
        with open(HISTORY_PATH, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    return count


def cmd_backfill(client):
    index = load_index()
    if not index.get("complete"):
        index = cmd_index(client)
        if client.calls_remaining <= 0:
            print("Orcamento consumido durante indexacao. Rode backfill novamente depois.")
            return None

    processed = []

    while client.calls_remaining > 0:
        activity = find_next_hr_activity(index)
        if not activity:
            break

        try:
            record = analyze_activity(client, activity)
        except ApiBudgetExceeded:
            break

        processed.append(record)
        index = load_index()

    if not processed:
        reports_count = regenerate_reports_from_history()
        print_status(client, "backfill", "nenhuma atividade com HR pendente")
        print(f"Relatorios regenerados: {reports_count}")
        return None

    reports_count = regenerate_reports_from_history()
    print_status(client, "backfill", f"{len(processed)} atividades processadas")
    print(f"Relatorios regenerados: {reports_count}")
    return processed


def cmd_analyze(client, activity_id):
    activity = get_activity_from_index(activity_id)
    if activity is None:
        details = client.get_activity_details(activity_id)
        activity = {
            "id": details.get("id") or int(activity_id),
            "name": details.get("name"),
            "type": details.get("type"),
            "start_date_local": details.get("start_date_local"),
            "has_heartrate": bool(details.get("average_heartrate") or details.get("max_heartrate")),
            "distance": details.get("distance"),
            "moving_time": details.get("moving_time"),
        }

    record = analyze_activity(client, activity)
    print_status(client, "analyze", f"processada {record['activity_id']} - {record['analysis_status']}")
    return record


def cmd_latest(client):
    index = load_index()
    if not index.get("activities"):
        page = client.get_summary_page(1, per_page=PER_PAGE)
        index = build_local_index_from_cache()
        save_index(index)
        if not page:
            print_status(client, "latest", "nenhuma atividade encontrada")
            return None

    activities = sorted(
        index.get("activities", []),
        key=lambda activity: activity.get("start_date_local") or activity.get("start_date") or "",
        reverse=True,
    )
    activity = next((a for a in activities if a.get("has_heartrate")), activities[0] if activities else None)
    if not activity:
        print_status(client, "latest", "nenhuma atividade encontrada")
        return None

    record = analyze_activity(client, activity)
    print_status(client, "latest", f"processada {record['activity_id']} - {record['analysis_status']}")
    return record


def cmd_sync(client):
    index = refresh_latest_summary_page(client)
    activities = sorted(
        index.get("activities", []),
        key=lambda activity: activity.get("start_date_local") or activity.get("start_date") or "",
        reverse=True,
    )
    activity = next((a for a in activities if a.get("has_heartrate")), activities[0] if activities else None)
    if not activity:
        print_status(client, "sync", "nenhuma atividade encontrada")
        return None

    record = analyze_activity(client, activity)
    weekly_path = write_weekly_report(HISTORY_PATH, WEEKLY_REPORTS_DIR)
    ai_ready_path = write_ai_ready_report(HISTORY_PATH, AI_REPORTS_DIR)
    print_status(client, "sync", f"atividade {record['activity_id']} processada")
    if weekly_path:
        print(f"Relatorio semanal: {weekly_path}")
    if ai_ready_path:
        print(f"Relatorio AI-ready: {ai_ready_path}")
    return record


def cmd_weekly(args):
    if (args.year is None) != (args.week is None):
        print("Use --year e --week juntos, ou omita ambos para gerar a semana mais recente.")
        return None

    if args.all:
        paths = write_all_weekly_reports(HISTORY_PATH, WEEKLY_REPORTS_DIR)
        print(f"Relatorios semanais gerados: {len(paths)}")
        print(f"Pasta: {WEEKLY_REPORTS_DIR}")
        return paths

    path = write_weekly_report(HISTORY_PATH, WEEKLY_REPORTS_DIR, iso_year=args.year, iso_week=args.week)
    if path is None:
        print("Nenhum relatorio semanal gerado. Verifique se o CSV historico existe e tem datas validas.")
        return None

    print(f"Relatorio semanal gerado: {path}")
    return path


def cmd_ai_ready(args):
    if (args.year is None) != (args.week is None):
        print("Use --year e --week juntos, ou omita ambos para gerar a semana mais recente.")
        return None

    path = write_ai_ready_report(HISTORY_PATH, AI_REPORTS_DIR, iso_year=args.year, iso_week=args.week)
    if path is None:
        print("Nenhum relatorio AI-ready gerado. Verifique se o CSV historico existe e tem datas validas.")
        return None

    print(f"Relatorio AI-ready gerado: {path}")
    return path


def print_status(client, command, message):
    print(f"Comando: {command}")
    print(f"Status: {message}")
    print(f"Chamadas API usadas: {client.calls_made}/{client.max_calls}")
    print(f"Cache hits: {client.cache_hits}")
    print(f"CSV: {HISTORY_PATH}")


def build_parser():
    parser = argparse.ArgumentParser(description="Pipeline Strava seguro por cota")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("index", help="Baixa paginas de summary dentro do orcamento")
    subparsers.add_parser("backfill", help="Processa a proxima atividade com HR pendente")
    subparsers.add_parser("latest", help="Analisa a atividade mais recente")
    subparsers.add_parser("sync", help="Atualiza page 1, analisa a atividade mais recente e gera weekly")

    analyze_parser = subparsers.add_parser("analyze", help="Analisa uma atividade especifica")
    analyze_parser.add_argument("--activity-id", required=True)

    weekly_parser = subparsers.add_parser("weekly", help="Gera relatorio semanal Markdown para AI")
    weekly_parser.add_argument("--all", action="store_true", help="Gera todas as semanas do historico")
    weekly_parser.add_argument("--year", type=int, help="Ano ISO-8601")
    weekly_parser.add_argument("--week", type=int, help="Semana ISO-8601")

    ai_parser = subparsers.add_parser("ai-ready", help="Gera Markdown unico pronto para enviar a AI")
    ai_parser.add_argument("--year", type=int, help="Ano ISO-8601")
    ai_parser.add_argument("--week", type=int, help="Semana ISO-8601")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    client = StravaClient()

    try:
        if args.command == "index":
            cmd_index(client)
        elif args.command == "backfill":
            cmd_backfill(client)
        elif args.command == "analyze":
            cmd_analyze(client, args.activity_id)
        elif args.command == "latest":
            cmd_latest(client)
        elif args.command == "sync":
            cmd_sync(client)
        elif args.command == "weekly":
            cmd_weekly(args)
        elif args.command == "ai-ready":
            cmd_ai_ready(args)
    except ApiBudgetExceeded as exc:
        print(f"Orcamento de API atingido: {exc}")
        print(f"Chamadas API usadas: {client.calls_made}/{client.max_calls}")
        print(f"Cache hits: {client.cache_hits}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
