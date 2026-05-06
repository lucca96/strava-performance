# AI Handoff - Strava Performance Pipeline

## One-line summary

Projeto pessoal para transformar dados do Strava em relatorios Markdown e CSV historico, voltados a suplementar o preparador fisico de um atleta de grappling.

## User context

- Usuario: atleta de grappling.
- Modalidades principais: wrestling, luta livre brasileira, jiu jitsu, NoGi, Gi/quimono.
- Objetivo: ganho de performance com suporte de dados para o preparador fisico.
- Saida principal desejada: Markdown otimizado para enviar a AI.
- Agregacao historica desejada: semanal.

## Current behavior

- Pipeline roda via `main.py`.
- Comando sem subcomando mostra ajuda e faz zero chamadas.
- API Strava passa por `src/client.py`.
- Limite padrao: `STRAVA_MAX_API_CALLS=100`.
- Cache e obrigatorio: se existe JSON local, o endpoint nao e chamado novamente.
- Backfill processa atividades com HR pendentes, respeitando limite de chamadas.
- Reports por atividade ficam em `data/reports/{activity_id}.md`.
- Reports semanais ficam em `data/weekly_reports/YYYY_semana_WW.md`.
- Reports AI-ready ficam em `data/ai_reports/YYYY_semana_WW_ai.md`.
- Historico tabular fica em `data/performance_history.csv`.
- Uso de API fica em `data/api_usage_log.csv`.
- Comando recomendado para iPhone: `python -B main.py sync`.
- Comando manual para gerar AI-ready: `python -B main.py ai-ready`.

## Current classification rules

- `grappling`: titulo contem `Gi`, `NoGi`, `Wrestling`, `Luta Livre`, `Quimono`.
- `preparacao_fisica`: titulo contem `Preparacao Fisica`, `CDPD` ou variacoes com encoding quebrado.
- `outros`: todo o restante.
- A partir de 2026-05-06, treinos futuros de preparacao fisica devem ser classificados no Strava como `WeightTraining`, mas a regra por titulo continua importante para historico.

## Current dataset status

- CSV atual contem atividades ja processadas com HR.
- Reports existentes foram regenerados sem a secao `Status`.
- Categorias atuais no historico: grappling, preparacao_fisica, outros.

## Safety constraints

- Nunca varrer automaticamente todas as atividades sem limite.
- Nunca chamar endpoint direto com `requests` no pipeline principal.
- Usar `StravaClient` para todo acesso a API.
- Manter cache obrigatorio.
- Antes de rodar chamadas reais, confirmar limite desejado ou usar padrao 100.
- Para uso pelo iPhone, preferir GitHub Actions privado disparado por iOS Shortcuts.

## Next likely work

- Adicionar insights por regra para carga, intensidade, drift, distribuicao de zonas e sRPE.
- Melhorar interpretacao especifica para grappling: carga de rounds, tolerancia a esforco, fadiga acumulada e recuperacao.
