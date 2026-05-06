import math
import unicodedata
from datetime import datetime, timezone

import numpy as np
import pandas as pd


SPORTS_WITH_PACE = {"Run", "Walk"}
ZONES = ["Z1", "Z2", "Z3", "Z4", "Z5"]
GRAPPLING_KEYWORDS = ("gi", "nogi", "wrestling", "luta livre", "quimono")
PREP_KEYWORDS = ("preparacao fisica", "preparação física", "preparaã", "cdpd")


def format_pace(sec_per_km):
    if sec_per_km is None or sec_per_km == "" or pd.isna(sec_per_km):
        return None
    sec_per_km = float(sec_per_km)
    minutes = int(sec_per_km // 60)
    seconds = int(sec_per_km % 60)
    return f"{minutes}:{seconds:02d}/km"


def estimate_hr_max(activities):
    hr_values = [a.get("max_heartrate", 0) for a in activities if a.get("max_heartrate")]
    return max(hr_values) if hr_values else None


def classify_activity(name):
    normalized = normalize_text(name)
    if any(keyword in normalized for keyword in GRAPPLING_KEYWORDS):
        return "grappling"
    if any(keyword in normalized for keyword in PREP_KEYWORDS):
        return "preparacao_fisica"
    return "outros"


def normalize_text(value):
    text = str(value or "").casefold()
    text = unicodedata.normalize("NFKD", text)
    return "".join(char for char in text if not unicodedata.combining(char))


def get_zone(hr, hr_max):
    pct = hr / hr_max
    if pct < 0.6:
        return "Z1"
    if pct < 0.7:
        return "Z2"
    if pct < 0.8:
        return "Z3"
    if pct < 0.9:
        return "Z4"
    return "Z5"


def analyze_hr_from_streams(streams, hr_max):
    required_keys = {"time", "heartrate"}
    if not streams or not required_keys.issubset(streams.keys()) or not hr_max:
        return {}, ["streams_heartrate"]

    df = pd.DataFrame(
        {
            "time": streams["time"]["data"],
            "heartrate": streams["heartrate"]["data"],
        }
    )
    if df.empty:
        return {}, ["streams_heartrate"]

    df["zone"] = df["heartrate"].apply(lambda hr: get_zone(hr, hr_max))
    zone_time_min = (df["zone"].value_counts().sort_index() / 60).to_dict()
    zone_pct = (df["zone"].value_counts(normalize=True).sort_index() * 100).to_dict()

    half = len(df) // 2
    if half == 0:
        cardiac_drift_pct = 0
    else:
        hr_first_half = df["heartrate"][:half].mean()
        hr_second_half = df["heartrate"][half:].mean()
        cardiac_drift_pct = (hr_second_half - hr_first_half) / hr_first_half * 100

    result = {
        "hr_avg_stream": float(df["heartrate"].mean()),
        "hr_max_stream": int(df["heartrate"].max()),
        "hr_max_estimated": hr_max,
        "cardiac_drift_pct": float(cardiac_drift_pct),
    }

    for zone in ZONES:
        result[f"{zone.lower()}_min"] = float(zone_time_min.get(zone, 0))
        result[f"{zone.lower()}_pct"] = float(zone_pct.get(zone, 0))

    return result, []


def analyze_pace_from_laps(details, laps):
    if not laps:
        return {}, ["laps"]

    distance = details.get("distance") or 0
    moving_time = details.get("moving_time") or 0
    distance_km = distance / 1000 if distance else 0
    if distance_km <= 0:
        return {}, ["distance"]

    splits = []
    for lap in laps:
        lap_distance = lap.get("distance") or 0
        lap_moving_time = lap.get("moving_time") or 0
        if lap_distance > 0 and lap_moving_time > 0:
            splits.append(lap_moving_time / (lap_distance / 1000))

    if not splits:
        return {}, ["laps"]

    pace_avg = moving_time / distance_km
    std_pace = np.std(splits)
    consistency_score = max(0, 10 - (std_pace / 10))

    half = len(splits) // 2
    if half == 0:
        first_half = splits[0]
        second_half = splits[0]
    else:
        first_half = np.mean(splits[:half])
        second_half = np.mean(splits[half:])

    drift = second_half - first_half
    rpe = details.get("perceived_exertion")

    interpretation = []
    if drift > 10:
        interpretation.append("Queda relevante de desempenho ao longo do treino")
    elif drift > 3:
        interpretation.append("Leve piora de ritmo ao longo do treino")
    else:
        interpretation.append("Boa manutencao de ritmo")

    if std_pace < 10:
        interpretation.append("Ritmo consistente")
    else:
        interpretation.append("Ritmo irregular")

    insights = []
    if drift > 10:
        insights.append("Reduzir intensidade inicial para evitar quebra no final")
    if std_pace > 10:
        insights.append("Trabalhar controle de ritmo")
    if rpe and rpe < 6 and drift > 10:
        insights.append("Melhorar percepcao de esforco durante o treino")

    return (
        {
            "pace_avg_sec_km": float(pace_avg),
            "pace_avg": format_pace(pace_avg),
            "splits_sec_km": [float(p) for p in splits],
            "std_pace_sec": float(std_pace),
            "consistency_score": float(consistency_score),
            "pace_drift_sec_km": float(drift),
            "pace_interpretation": " | ".join(interpretation),
            "pace_insights": " | ".join(insights[:3]),
        },
        [],
    )


def build_activity_record(activity, details, streams=None, laps=None, hr_max=None):
    missing_data = []
    distance = details.get("distance") or activity.get("distance") or 0
    moving_time = details.get("moving_time") or activity.get("moving_time") or 0
    distance_km = distance / 1000 if distance else 0
    pace_summary_sec_km = moving_time / distance_km if distance_km else None

    name = activity.get("name") or details.get("name")
    record = {
        "activity_id": activity.get("id") or details.get("id"),
        "name": name,
        "type": activity.get("type") or details.get("type"),
        "activity_category": classify_activity(name),
        "start_date_local": activity.get("start_date_local") or details.get("start_date_local"),
        "distance_km": distance_km,
        "moving_time_min": moving_time / 60 if moving_time else 0,
        "average_heartrate": details.get("average_heartrate"),
        "max_heartrate": details.get("max_heartrate"),
        "suffer_score": details.get("suffer_score"),
        "perceived_exertion": details.get("perceived_exertion"),
        "average_cadence": details.get("average_cadence"),
        "pace_summary_sec_km": pace_summary_sec_km,
    }

    if record["perceived_exertion"] is not None and record["moving_time_min"]:
        record["session_rpe_load"] = float(record["perceived_exertion"]) * float(record["moving_time_min"])

    hr_result, hr_missing = analyze_hr_from_streams(streams, hr_max)
    record.update(hr_result)
    missing_data.extend(hr_missing)

    if record["type"] in SPORTS_WITH_PACE:
        pace_result, pace_missing = analyze_pace_from_laps(details, laps)
        record.update(pace_result)
        missing_data.extend(pace_missing)

    record["analysis_status"] = "complete" if not missing_data else "partial"
    record["missing_data"] = " | ".join(sorted(set(missing_data)))
    record["completed_at"] = datetime.now(timezone.utc).isoformat()
    return record


def upsert_history(record, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    new_df = pd.DataFrame([record]).dropna(axis=1, how="all")

    if output_path.exists() and output_path.stat().st_size > 0:
        existing_df = pd.read_csv(output_path)
        existing_df = existing_df[existing_df["activity_id"].astype(str) != str(record["activity_id"])]
        existing_df = existing_df.dropna(axis=1, how="all")
        df = pd.concat([existing_df, new_df], ignore_index=True, sort=False)
    else:
        df = new_df

    if "start_date_local" in df.columns:
        df = df.sort_values("start_date_local")

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df


def render_report(record):
    if not record.get("activity_category"):
        record["activity_category"] = classify_activity(record.get("name"))

    lines = [
        f"# {record.get('name')}",
        "",
        "## Resumo",
        "",
        f"- Activity ID: {record.get('activity_id')}",
        f"- Tipo: {record.get('type')}",
        f"- Categoria: {record.get('activity_category')}",
        f"- Data: {record.get('start_date_local')}",
        f"- Distancia: {_fmt(record.get('distance_km'), 2)} km",
        f"- Tempo em movimento: {_fmt(record.get('moving_time_min'), 1)} min",
        f"- Percepcao de esforco (RPE): {_fmt(record.get('perceived_exertion'), 1)}",
        f"- Carga sRPE: {_fmt(record.get('session_rpe_load'), 1)}",
        f"- Suffer score: {_fmt(record.get('suffer_score'), 1)}",
        "",
        "## Frequencia cardiaca",
        "",
        f"- FC media: {_fmt(record.get('average_heartrate'), 1)}",
        f"- FC maxima: {_fmt(record.get('max_heartrate'), 1)}",
        f"- Cardiac drift: {_fmt(record.get('cardiac_drift_pct'), 1)}%",
        f"- Z1: {_fmt(record.get('z1_min'), 1)} min ({_fmt(record.get('z1_pct'), 1)}%)",
        f"- Z2: {_fmt(record.get('z2_min'), 1)} min ({_fmt(record.get('z2_pct'), 1)}%)",
        f"- Z3: {_fmt(record.get('z3_min'), 1)} min ({_fmt(record.get('z3_pct'), 1)}%)",
        f"- Z4: {_fmt(record.get('z4_min'), 1)} min ({_fmt(record.get('z4_pct'), 1)}%)",
        f"- Z5: {_fmt(record.get('z5_min'), 1)} min ({_fmt(record.get('z5_pct'), 1)}%)",
    ]

    if record.get("pace_avg") or record.get("pace_summary_sec_km"):
        lines.extend(
            [
                "",
                "## Pace",
                "",
                f"- Pace medio: {record.get('pace_avg') or format_pace(record.get('pace_summary_sec_km')) or ''}",
                f"- Consistencia: {_fmt(record.get('consistency_score'), 1)}",
                f"- Drift de pace: {_fmt(record.get('pace_drift_sec_km'), 1)} seg/km",
            ]
        )

    if record.get("missing_data"):
        lines.extend(["", "## Dados faltantes"])
        lines.append(f"- Dados faltantes: {record.get('missing_data')}")
    if record.get("pace_insights"):
        lines.extend(["", "## Insights", record.get("pace_insights")])

    return "\n".join(lines) + "\n"


def _fmt(value, digits):
    if value is None or value == "":
        return ""
    try:
        if pd.isna(value) or math.isnan(value):
            return ""
    except TypeError:
        pass
    try:
        return f"{float(value):.{digits}f}"
    except ValueError:
        return ""
