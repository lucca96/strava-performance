# Changelog de Decisoes

## 2026-05-06

### API e cache

- Pipeline passou a usar `StravaClient` como cliente central.
- Limite padrao de API mudou para 100 chamadas por execucao.
- Cache tornou-se obrigatorio para endpoints ja baixados.
- Uso de API passou a ser logado em `data/api_usage_log.csv`.

### CLI

- `main.py` passou a exigir subcomandos.
- Sem subcomando, imprime ajuda e faz zero chamadas.
- Comandos atuais: `index`, `backfill`, `analyze`, `latest`.
- Comando `sync` adicionado para uso pelo iPhone.

### Backfill

- Backfill passou de uma atividade por execucao para lote ate consumir orcamento.
- Atividades completas nao sao chamadas novamente.
- Reports podem ser regenerados a partir do CSV sem API.

### Reports

- Reports Markdown por atividade foram criados em `data/reports/`.
- Campo RPE passou a aparecer nos reports.
- Campo `session_rpe_load` foi adicionado.
- Secao `Status` foi removida dos reports.
- Reports semanais foram adicionados em `data/weekly_reports/`.
- Padrao de nome semanal: `YYYY_semana_WW.md`, usando semana ISO-8601.

### Classificacao

- Criado campo `activity_category`.
- Regras:
  - grappling: Gi, NoGi, Wrestling, Luta Livre, Quimono;
  - preparacao_fisica: Preparacao Fisica, CDPD e variacoes;
  - outros: restante.

### Produto

- Objetivo definido: relatorio Markdown para AI e preparador fisico.
- Agregacao historica desejada: semanal.
- Esporte alvo: grappling.
- Fluxo recomendado para iPhone: iOS Shortcuts dispara GitHub Actions, que roda `python -B main.py sync`.
