# AI-ready performance report 2025-W35

## Contexto fixo

- Atleta: grappling.
- Modalidades: wrestling, luta livre brasileira, jiu jitsu, NoGi e Gi/quimono.
- Objetivo: melhorar performance e suplementar a avaliacao do preparador fisico.
- Saida desejada: analise objetiva, acionavel e orientada a treino.
- Categorias do projeto: grappling, preparacao_fisica, outros.
- Carga sRPE: RPE multiplicado pelo tempo em movimento em minutos.
- Semana e ano seguem ISO-8601.

## Tarefa para AI

Analise os dados abaixo como um preparador fisico que trabalha com atleta de grappling. Priorize sinais de fadiga, distribuicao de carga, equilibrio entre luta e preparacao fisica, risco de aumento brusco de carga, e recomendacoes praticas para a proxima semana.

Responda em portugues, com:

- resumo executivo;
- principais riscos;
- o que manter;
- o que ajustar;
- perguntas para o atleta antes de mudar a carga;
- recomendacao objetiva para a proxima semana.

## Relatorio semanal consolidado

# Relatorio semanal 2025-W35

## Resumo

- Periodo observado: 2025-08-26 a 2025-08-28
- Sessoes: 2
- Tempo total: 120.4 min
- Carga sRPE total: 409.0
- RPE medio: 3.5
- FC media da semana: 118.2
- FC maxima da semana: 163.0
- Cardiac drift medio: 11.6%
- Delta carga vs semana anterior: 86.8%
- Delta minutos vs semana anterior: 119.9%

## Carga por categoria

- grappling: 0 sessoes | 0.0 min | sRPE 0.0
- preparacao_fisica: 2 sessoes | 120.4 min | sRPE 409.0
- outros: 0 sessoes | 0.0 min | sRPE 0.0

## Zonas de frequencia cardiaca

- Z1: 50.9 min (53.6%)
- Z2: 25.7 min (27.1%)
- Z3: 10.2 min (10.7%)
- Z4: 7.8 min (8.2%)
- Z5: 0.3 min (0.4%)

## Sessoes da semana

- 2025-08-26 | preparacao_fisica | Preparação Física CDPD | 72.6 min | RPE 3.0 | sRPE 217.7
- 2025-08-28 | preparacao_fisica | Preparação Fisica CDPD | 47.8 min | RPE 4.0 | sRPE 191.3

## Alertas e insights

- Cardiac drift medio elevado; pode indicar fadiga, calor, baixa recuperacao ou intensidade mal distribuida.
- Carga semanal subiu mais de 30% vs semana anterior; risco de aumento brusco de carga.

## Prompt para AI

Analise esta semana como preparador fisico de um atleta de grappling. Foque em carga semanal, distribuicao de intensidade, sinais de fadiga, relacao entre grappling e preparacao fisica, e recomendacoes praticas para melhorar performance sem aumentar risco de sobrecarga.

## Dados estruturados da semana

### 2025-08-26 - Preparação Física CDPD

- activity_id: 15598059108
- type: Workout
- category: preparacao_fisica
- moving_time_min: 72.56666666666666
- perceived_exertion: 3.0
- session_rpe_load: 217.7
- average_heartrate: 117.1
- max_heartrate: 149.0
- cardiac_drift_pct: 5.3189644345834415
- z1_min: 35.86666666666667
- z2_min: 15.316666666666666
- z3_min: 0.5833333333333334
- z4_min: 0.0
- z5_min: 0.0

### 2025-08-28 - Preparação Fisica CDPD

- activity_id: 15621564920
- type: Workout
- category: preparacao_fisica
- moving_time_min: 47.833333333333336
- perceived_exertion: 4.0
- session_rpe_load: 191.33333333333331
- average_heartrate: 119.4
- max_heartrate: 163.0
- cardiac_drift_pct: 17.787381359949546
- z1_min: 15.033333333333331
- z2_min: 10.35
- z3_min: 9.566666666666666
- z4_min: 7.816666666666666
- z5_min: 0.35

## Observacoes de interpretacao

- Dados ausentes devem ser tratados como limitacao de coleta, nao como ausencia fisiologica.
- Treinos de grappling podem aparecer como Workout no Strava; use a categoria do projeto.
- Preparacao fisica antiga pode aparecer como Workout; a classificacao por titulo corrige parte do historico.
- Nao fazer recomendacoes medicas; focar em treino, carga, recuperacao e perguntas ao atleta.
