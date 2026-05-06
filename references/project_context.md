# Contexto do Projeto

## Objetivo

Construir um pipeline pessoal para analise de performance esportiva a partir de dados do Strava, com foco em treinos de grappling e preparacao fisica.

O objetivo pratico e gerar dados e relatorios para o preparador fisico avaliar carga, intensidade, recuperacao e progresso ao longo do tempo.

## Publico do relatorio

- Preparador fisico.
- AI usada como assistente analitico.
- O proprio atleta, para acompanhar carga e tendencias.

## Esporte

O usuario e atleta de grappling:

- wrestling;
- luta livre brasileira;
- jiu jitsu;
- NoGi;
- Gi/quimono.

Esses treinos aparecem no Strava como `Workout`, entao a classificacao precisa usar o titulo da atividade.

## Decisoes atuais

- Relatorio historico deve ser semanal.
- Saida principal: Markdown para enviar a AI.
- CSV continua existindo como base estruturada.
- Preparacao fisica futura sera registrada como `WeightTraining` a partir de 2026-05-06.
- Historico antigo de preparacao fisica ainda deve ser detectado por titulo.

## Escopo atual

Incluido:

- Autenticacao Strava via token refresh.
- Cache local de endpoints.
- Backfill incremental.
- Historico CSV.
- Reports Markdown por atividade.
- Classificacao por titulo.
- Metricas de HR, zonas, drift, RPE e sRPE.

Ainda nao incluido:

- Relatorio semanal consolidado.
- Insights historicos avancados.
- Dashboard Power BI.
- Banco de dados.
- Interface Streamlit.
