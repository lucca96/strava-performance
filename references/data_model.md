# Modelo de Dados

## Arquivo principal

CSV historico: `data/performance_history.csv`

Uma linha por atividade.

## Reports semanais

Pasta: `data/weekly_reports/`

Padrao de nome:

- `YYYY_semana_WW.md`

Exemplo:

- `2025_semana_02.md`

O ano e a semana seguem ISO-8601.

## Campos principais

Identificacao:

- `activity_id`
- `name`
- `type`
- `activity_category`
- `start_date_local`

Volume:

- `distance_km`
- `moving_time_min`

Frequencia cardiaca:

- `average_heartrate`
- `max_heartrate`
- `hr_avg_stream`
- `hr_max_stream`
- `hr_max_estimated`
- `cardiac_drift_pct`

Zonas:

- `z1_min`, `z1_pct`
- `z2_min`, `z2_pct`
- `z3_min`, `z3_pct`
- `z4_min`, `z4_pct`
- `z5_min`, `z5_pct`

Percepcao e carga:

- `perceived_exertion`
- `session_rpe_load`
- `suffer_score`

Pace, quando aplicavel:

- `pace_summary_sec_km`
- `pace_avg_sec_km`
- `pace_avg`
- `splits_sec_km`
- `std_pace_sec`
- `consistency_score`
- `pace_drift_sec_km`
- `pace_interpretation`
- `pace_insights`

Status tecnico:

- `analysis_status`
- `missing_data`
- `completed_at`

## Classificacao de atividade

Campo: `activity_category`

Valores atuais:

- `grappling`
- `preparacao_fisica`
- `outros`

Regras:

- `grappling`: titulo contem `Gi`, `NoGi`, `Wrestling`, `Luta Livre`, `Quimono`.
- `preparacao_fisica`: titulo contem `Preparacao Fisica`, `Preparacao Fisica` com acentos, `CDPD` ou variacoes com encoding quebrado.
- `outros`: restante.

## Observacao sobre grappling

Treinos de grappling aparecem como `Workout`, entao `type` sozinho nao identifica a modalidade. Use `activity_category`.

## Observacao sobre preparacao fisica

A partir de 2026-05-06, preparacao fisica futura deve ser registrada no Strava como `WeightTraining`. Para historico antigo, continuar usando regra por titulo.
