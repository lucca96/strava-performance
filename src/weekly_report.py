from pathlib import Path

import pandas as pd


ZONE_COLUMNS = ["z1_min", "z2_min", "z3_min", "z4_min", "z5_min"]
CATEGORIES = ["grappling", "preparacao_fisica", "outros"]


def weekly_filename(iso_year, iso_week):
    return f"{int(iso_year)}_semana_{int(iso_week):02d}.md"


def load_history(history_path):
    df = pd.read_csv(history_path)
    if df.empty:
        return df

    df["start_dt"] = pd.to_datetime(df["start_date_local"], errors="coerce", utc=True)
    df = df.dropna(subset=["start_dt"]).copy()
    iso = df["start_dt"].dt.isocalendar()
    df["iso_year"] = iso.year.astype(int)
    df["iso_week"] = iso.week.astype(int)

    for column in numeric_columns(df):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if "activity_category" not in df.columns:
        df["activity_category"] = "outros"

    return df


def numeric_columns(df):
    candidates = [
        "distance_km",
        "moving_time_min",
        "average_heartrate",
        "max_heartrate",
        "cardiac_drift_pct",
        "perceived_exertion",
        "session_rpe_load",
        "z1_min",
        "z2_min",
        "z3_min",
        "z4_min",
        "z5_min",
        "z1_pct",
        "z2_pct",
        "z3_pct",
        "z4_pct",
        "z5_pct",
    ]
    return [column for column in candidates if column in df.columns]


def available_weeks(df):
    if df.empty:
        return []
    weeks = df[["iso_year", "iso_week"]].drop_duplicates().sort_values(["iso_year", "iso_week"])
    return [(int(row.iso_year), int(row.iso_week)) for row in weeks.itertuples()]


def render_weekly_report(df, iso_year, iso_week):
    week_df = df[(df["iso_year"] == int(iso_year)) & (df["iso_week"] == int(iso_week))].copy()
    if week_df.empty:
        return None

    previous = previous_week_df(df, iso_year, iso_week)
    start_date = week_df["start_dt"].min().date().isoformat()
    end_date = week_df["start_dt"].max().date().isoformat()

    total_sessions = len(week_df)
    total_minutes = safe_sum(week_df, "moving_time_min")
    total_load = safe_sum(week_df, "session_rpe_load")
    avg_rpe = safe_mean(week_df, "perceived_exertion")
    avg_hr = safe_mean(week_df, "average_heartrate")
    max_hr = safe_max(week_df, "max_heartrate")
    avg_drift = safe_mean(week_df, "cardiac_drift_pct")

    prev_load = safe_sum(previous, "session_rpe_load") if previous is not None else None
    prev_minutes = safe_sum(previous, "moving_time_min") if previous is not None else None

    lines = [
        f"# Relatorio semanal {int(iso_year)}-W{int(iso_week):02d}",
        "",
        "## Resumo",
        "",
        f"- Periodo observado: {start_date} a {end_date}",
        f"- Sessoes: {total_sessions}",
        f"- Tempo total: {fmt_value(total_minutes, 1, suffix=' min')}",
        f"- Carga sRPE total: {fmt_value(total_load, 1)}",
        f"- RPE medio: {fmt_value(avg_rpe, 1)}",
        f"- FC media da semana: {fmt_value(avg_hr, 1)}",
        f"- FC maxima da semana: {fmt_value(max_hr, 1)}",
        f"- Cardiac drift medio: {fmt_value(avg_drift, 1, suffix='%')}",
    ]

    load_delta = delta_pct(total_load, prev_load)
    minutes_delta = delta_pct(total_minutes, prev_minutes)
    if load_delta is not None:
        lines.append(f"- Delta carga vs semana anterior: {fmt(load_delta, 1)}%")
    if minutes_delta is not None:
        lines.append(f"- Delta minutos vs semana anterior: {fmt(minutes_delta, 1)}%")

    lines.extend(["", "## Carga por categoria", ""])
    for category in CATEGORIES:
        category_df = week_df[week_df["activity_category"].fillna("outros") == category]
        lines.append(
            f"- {category}: {len(category_df)} sessoes | {fmt(safe_sum(category_df, 'moving_time_min') or 0, 1)} min | "
            f"sRPE {fmt(safe_sum(category_df, 'session_rpe_load') or 0, 1)}"
        )

    lines.extend(["", "## Zonas de frequencia cardiaca", ""])
    zone_total = sum((safe_sum(week_df, column) or 0) for column in ZONE_COLUMNS if column in week_df.columns)
    if zone_total:
        for zone, column in zip(["Z1", "Z2", "Z3", "Z4", "Z5"], ZONE_COLUMNS):
            minutes = safe_sum(week_df, column) or 0
            pct = minutes / zone_total * 100
            lines.append(f"- {zone}: {fmt(minutes, 1)} min ({fmt(pct, 1)}%)")
    else:
        lines.append("- Sem dados de zonas de frequencia cardiaca nesta semana.")

    lines.extend(["", "## Sessoes da semana", ""])
    for row in week_df.sort_values("start_dt").itertuples():
        lines.append(
            f"- {row.start_dt.date().isoformat()} | {getattr(row, 'activity_category', '')} | "
            f"{getattr(row, 'name', '')} | {fmt_value(getattr(row, 'moving_time_min', None), 1, suffix=' min')} | "
            f"RPE {fmt_value(getattr(row, 'perceived_exertion', None), 1)} | "
            f"sRPE {fmt_value(getattr(row, 'session_rpe_load', None), 1)}"
        )

    lines.extend(["", "## Alertas e insights", ""])
    for insight in build_insights(week_df, total_load, total_minutes, avg_drift, prev_load):
        lines.append(f"- {insight}")

    lines.extend(
        [
            "",
            "## Prompt para AI",
            "",
            "Analise esta semana como preparador fisico de um atleta de grappling. Foque em carga semanal, "
            "distribuicao de intensidade, sinais de fadiga, relacao entre grappling e preparacao fisica, "
            "e recomendacoes praticas para melhorar performance sem aumentar risco de sobrecarga.",
        ]
    )

    return "\n".join(lines) + "\n"


def previous_week_df(df, iso_year, iso_week):
    weeks = available_weeks(df)
    current = (int(iso_year), int(iso_week))
    if current not in weeks:
        return None
    idx = weeks.index(current)
    if idx == 0:
        return None
    prev_year, prev_week = weeks[idx - 1]
    return df[(df["iso_year"] == prev_year) & (df["iso_week"] == prev_week)]


def build_insights(week_df, total_load, total_minutes, avg_drift, prev_load):
    insights = []
    grappling_sessions = len(week_df[week_df["activity_category"] == "grappling"])
    prep_sessions = len(week_df[week_df["activity_category"] == "preparacao_fisica"])
    if "perceived_exertion" in week_df.columns:
        high_rpe = week_df[pd.to_numeric(week_df["perceived_exertion"], errors="coerce") >= 8]
    else:
        high_rpe = week_df.iloc[0:0]

    if grappling_sessions >= 3:
        insights.append("Semana com alta frequencia de grappling; monitorar recuperacao entre sessoes tecnicas intensas.")
    if prep_sessions >= 3:
        insights.append("Volume relevante de preparacao fisica; avaliar interferencia com qualidade dos treinos de luta.")
    if len(high_rpe) >= 2:
        insights.append("Duas ou mais sessoes com RPE alto; checar sono, dor muscular e queda de rendimento.")
    if avg_drift is not None and avg_drift > 8:
        insights.append("Cardiac drift medio elevado; pode indicar fadiga, calor, baixa recuperacao ou intensidade mal distribuida.")
    if total_load is not None and prev_load is not None and prev_load > 0 and total_load > prev_load * 1.3:
        insights.append("Carga semanal subiu mais de 30% vs semana anterior; risco de aumento brusco de carga.")
    if total_minutes and total_load and total_load / total_minutes >= 7:
        insights.append("Densidade de carga alta por minuto; semana provavelmente exigente mesmo sem grande volume total.")
    if not insights:
        insights.append("Semana sem alertas fortes pelas regras atuais; interpretar junto com contexto de competicao, sono e dor.")

    return insights


def write_weekly_report(history_path, output_dir, iso_year=None, iso_week=None):
    df = load_history(history_path)
    weeks = available_weeks(df)
    if not weeks:
        return None

    if iso_year is None or iso_week is None:
        iso_year, iso_week = weeks[-1]

    report = render_weekly_report(df, iso_year, iso_week)
    if report is None:
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / weekly_filename(iso_year, iso_week)
    with open(path, "w", encoding="utf-8") as file:
        file.write(report)
    return path


def write_all_weekly_reports(history_path, output_dir):
    df = load_history(history_path)
    paths = []
    for iso_year, iso_week in available_weeks(df):
        report = render_weekly_report(df, iso_year, iso_week)
        if report is None:
            continue
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / weekly_filename(iso_year, iso_week)
        with open(path, "w", encoding="utf-8") as file:
            file.write(report)
        paths.append(path)
    return paths


def safe_sum(df, column):
    if df is None or df.empty or column not in df.columns:
        return None
    value = pd.to_numeric(df[column], errors="coerce").sum(min_count=1)
    return None if pd.isna(value) else float(value)


def safe_mean(df, column):
    if df is None or df.empty or column not in df.columns:
        return None
    value = pd.to_numeric(df[column], errors="coerce").mean()
    return None if pd.isna(value) else float(value)


def safe_max(df, column):
    if df is None or df.empty or column not in df.columns:
        return None
    value = pd.to_numeric(df[column], errors="coerce").max()
    return None if pd.isna(value) else float(value)


def delta_pct(current, previous):
    if current is None or previous is None or previous == 0:
        return None
    return (current - previous) / previous * 100


def fmt(value, digits):
    if value is None or value == "":
        return ""
    try:
        if pd.isna(value):
            return ""
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return ""


def fmt_value(value, digits, suffix=""):
    formatted = fmt(value, digits)
    if not formatted:
        return "sem dados"
    return f"{formatted}{suffix}"
