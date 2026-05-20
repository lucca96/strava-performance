# AI-ready performance report 2026-W21

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

# Relatorio semanal 2026-W21

## Resumo

- Periodo observado: 2026-05-19 a 2026-05-19
- Sessoes: 1
- Tempo total: 99.5 min
- Carga sRPE total: 497.4
- RPE medio: 5.0
- FC media da semana: 108.9
- FC maxima da semana: 150.0
- Cardiac drift medio: 19.2%
- Delta carga vs semana anterior: 84.0%
- Delta minutos vs semana anterior: 47.2%

## Carga por categoria

- grappling: 0 sessoes | 0.0 min | sRPE 0.0
- preparacao_fisica: 1 sessoes | 99.5 min | sRPE 497.4
- outros: 0 sessoes | 0.0 min | sRPE 0.0

## Zonas de frequencia cardiaca

- Z1: 34.7 min (40.4%)
- Z2: 37.0 min (43.0%)
- Z3: 13.5 min (15.7%)
- Z4: 0.8 min (0.9%)
- Z5: 0.0 min (0.0%)

## Sessoes da semana

- 2026-05-19 | preparacao_fisica | Preparação Física CDPD | 99.5 min | RPE 5.0 | sRPE 497.4

## Alertas e insights

- Cardiac drift medio elevado; pode indicar fadiga, calor, baixa recuperacao ou intensidade mal distribuida.
- Carga semanal subiu mais de 30% vs semana anterior; risco de aumento brusco de carga.

## Prompt para AI

Analise esta semana como preparador fisico de um atleta de grappling. Foque em carga semanal, distribuicao de intensidade, sinais de fadiga, relacao entre grappling e preparacao fisica, e recomendacoes praticas para melhorar performance sem aumentar risco de sobrecarga.

## Dados estruturados da semana

### 2026-05-19 - Preparação Física CDPD

- activity_id: 18575051904
- type: WeightTraining
- category: preparacao_fisica
- moving_time_min: 99.48333333333332
- perceived_exertion: 5.0
- session_rpe_load: 497.4166666666667
- average_heartrate: 108.9
- hr_initial_5min: 82.26842105263158
- max_heartrate: 150.0
- hr_final_5min: 110.37974683544304
- cardiac_drift_pct: 19.19421261896667
- z1_min: 34.733333333333334
- z2_min: 37.0
- z3_min: 13.533333333333331
- z4_min: 0.75
- z5_min: 0.0

## Observacoes de interpretacao

- Dados ausentes devem ser tratados como limitacao de coleta, nao como ausencia fisiologica.
- Treinos de grappling podem aparecer como Workout no Strava; use a categoria do projeto.
- Preparacao fisica antiga pode aparecer como Workout; a classificacao por titulo corrige parte do historico.
- Nao fazer recomendacoes medicas; focar em treino, carga, recuperacao e perguntas ao atleta.
