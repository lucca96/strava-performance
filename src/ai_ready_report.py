from pathlib import Path

from src.weekly_report import available_weeks, load_history, render_weekly_report


def ai_ready_filename(iso_year, iso_week):
    return f"{int(iso_year)}_semana_{int(iso_week):02d}_ai.md"


def render_ai_ready_report(df, iso_year, iso_week):
    weekly = render_weekly_report(df, iso_year, iso_week)
    if weekly is None:
        return None

    week_df = df[(df["iso_year"] == int(iso_year)) & (df["iso_week"] == int(iso_week))].copy()

    lines = [
        f"# AI-ready performance report {int(iso_year)}-W{int(iso_week):02d}",
        "",
        "## Contexto fixo",
        "",
        "- Atleta: grappling.",
        "- Modalidades: wrestling, luta livre brasileira, jiu jitsu, NoGi e Gi/quimono.",
        "- Objetivo: melhorar performance e suplementar a avaliacao do preparador fisico.",
        "- Saida desejada: analise objetiva, acionavel e orientada a treino.",
        "- Categorias do projeto: grappling, preparacao_fisica, outros.",
        "- Carga sRPE: RPE multiplicado pelo tempo em movimento em minutos.",
        "- Semana e ano seguem ISO-8601.",
        "",
        "## Tarefa para AI",
        "",
        "Analise os dados abaixo como um preparador fisico que trabalha com atleta de grappling. "
        "Priorize sinais de fadiga, distribuicao de carga, equilibrio entre luta e preparacao fisica, "
        "risco de aumento brusco de carga, e recomendacoes praticas para a proxima semana.",
        "",
        "Responda em portugues, com:",
        "",
        "- resumo executivo;",
        "- principais riscos;",
        "- o que manter;",
        "- o que ajustar;",
        "- perguntas para o atleta antes de mudar a carga;",
        "- recomendacao objetiva para a proxima semana.",
        "",
        "## Relatorio semanal consolidado",
        "",
        weekly.strip(),
        "",
        "## Dados estruturados da semana",
        "",
    ]

    for row in week_df.sort_values("start_dt").itertuples():
        lines.extend(
            [
                f"### {row.start_dt.date().isoformat()} - {getattr(row, 'name', '')}",
                "",
                f"- activity_id: {getattr(row, 'activity_id', '')}",
                f"- type: {getattr(row, 'type', '')}",
                f"- category: {getattr(row, 'activity_category', '')}",
                f"- moving_time_min: {fmt_raw(getattr(row, 'moving_time_min', None))}",
                f"- perceived_exertion: {fmt_raw(getattr(row, 'perceived_exertion', None))}",
                f"- session_rpe_load: {fmt_raw(getattr(row, 'session_rpe_load', None))}",
                f"- average_heartrate: {fmt_raw(getattr(row, 'average_heartrate', None))}",
                f"- max_heartrate: {fmt_raw(getattr(row, 'max_heartrate', None))}",
                f"- cardiac_drift_pct: {fmt_raw(getattr(row, 'cardiac_drift_pct', None))}",
                f"- z1_min: {fmt_raw(getattr(row, 'z1_min', None))}",
                f"- z2_min: {fmt_raw(getattr(row, 'z2_min', None))}",
                f"- z3_min: {fmt_raw(getattr(row, 'z3_min', None))}",
                f"- z4_min: {fmt_raw(getattr(row, 'z4_min', None))}",
                f"- z5_min: {fmt_raw(getattr(row, 'z5_min', None))}",
                "",
            ]
        )

    lines.extend(
        [
            "## Observacoes de interpretacao",
            "",
            "- Dados ausentes devem ser tratados como limitacao de coleta, nao como ausencia fisiologica.",
            "- Treinos de grappling podem aparecer como Workout no Strava; use a categoria do projeto.",
            "- Preparacao fisica antiga pode aparecer como Workout; a classificacao por titulo corrige parte do historico.",
            "- Nao fazer recomendacoes medicas; focar em treino, carga, recuperacao e perguntas ao atleta.",
        ]
    )

    return "\n".join(lines) + "\n"


def write_ai_ready_report(history_path, output_dir, iso_year=None, iso_week=None):
    df = load_history(history_path)
    weeks = available_weeks(df)
    if not weeks:
        return None

    if iso_year is None or iso_week is None:
        iso_year, iso_week = weeks[-1]

    report = render_ai_ready_report(df, iso_year, iso_week)
    if report is None:
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / ai_ready_filename(iso_year, iso_week)
    with open(path, "w", encoding="utf-8") as file:
        file.write(report)
    return path


def fmt_raw(value):
    if value is None:
        return ""
    try:
        if value != value:
            return ""
    except TypeError:
        pass
    return str(value)
