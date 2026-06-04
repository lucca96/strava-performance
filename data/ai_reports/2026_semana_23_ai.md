# AI-ready performance report 2026-W23

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

# Relatorio semanal 2026-W23

## Resumo

- Periodo observado: 2026-06-02 a 2026-06-03
- Sessoes: 2
- Tempo total: 202.3 min
- Carga sRPE total: 1145.5
- RPE medio: 5.5
- FC media da semana: 143.6
- FC maxima da semana: 184.0
- Cardiac drift medio: 10.8%
- Delta carga vs semana anterior: 130.3%
- Delta minutos vs semana anterior: 103.4%

## Carga por categoria

- grappling: 1 sessoes | 134.0 min | sRPE 803.9
- preparacao_fisica: 1 sessoes | 68.3 min | sRPE 341.6
- outros: 0 sessoes | 0.0 min | sRPE 0.0

## Zonas de frequencia cardiaca

- Z1: 14.7 min (11.5%)
- Z2: 16.8 min (13.1%)
- Z3: 32.1 min (25.1%)
- Z4: 38.3 min (30.0%)
- Z5: 25.9 min (20.3%)

## Sessoes da semana

- 2026-06-02 | preparacao_fisica | Preparação Fisica CDPD | 68.3 min | RPE 5.0 | sRPE 341.6
- 2026-06-03 | grappling | Wrestling + Luta Livre no QG | 134.0 min | RPE 6.0 | sRPE 803.9

## Alertas e insights

- Cardiac drift medio elevado; pode indicar fadiga, calor, baixa recuperacao ou intensidade mal distribuida.
- Carga semanal subiu mais de 30% vs semana anterior; risco de aumento brusco de carga.

## Prompt para AI

Analise esta semana como preparador fisico de um atleta de grappling. Foque em carga semanal, distribuicao de intensidade, sinais de fadiga, relacao entre grappling e preparacao fisica, e recomendacoes praticas para melhorar performance sem aumentar risco de sobrecarga.

## Dados estruturados da semana

### 2026-06-02 - Preparação Fisica CDPD

- activity_id: 18762699426
- type: WeightTraining
- category: preparacao_fisica
- moving_time_min: 68.31666666666666
- perceived_exertion: 5.0
- session_rpe_load: 341.5833333333333
- average_heartrate: 137.9
- hr_initial_5min: 92.29629629629628
- max_heartrate: 178.0
- hr_final_5min: 125.6938775510204
- cardiac_drift_pct: 5.113025809350779
- z1_min: 6.883333333333334
- z2_min: 8.7
- z3_min: 13.466666666666669
- z4_min: 19.066666666666663
- z5_min: 14.45

### 2026-06-03 - Wrestling + Luta Livre no QG

- activity_id: 18777608704
- type: Workout
- category: grappling
- moving_time_min: 133.98333333333332
- perceived_exertion: 6.0
- session_rpe_load: 803.8999999999999
- average_heartrate: 149.2
- hr_initial_5min: 107.12040133779264
- max_heartrate: 184.0
- hr_final_5min: 141.13780918727915
- cardiac_drift_pct: 16.502331624248892
- z1_min: 7.85
- z2_min: 8.05
- z3_min: 18.6
- z4_min: 19.266666666666666
- z5_min: 11.466666666666669

## Observacoes de interpretacao

- Dados ausentes devem ser tratados como limitacao de coleta, nao como ausencia fisiologica.
- Treinos de grappling podem aparecer como Workout no Strava; use a categoria do projeto.
- Preparacao fisica antiga pode aparecer como Workout; a classificacao por titulo corrige parte do historico.
- Nao fazer recomendacoes medicas; focar em treino, carga, recuperacao e perguntas ao atleta.
