# Arquitetura Atual

## Entry points

Arquivo principal: `main.py`

Comandos:

- `python -B main.py index`
- `python -B main.py backfill`
- `python -B main.py analyze --activity-id ID`
- `python -B main.py latest`
- `python -B main.py sync`
- `python -B main.py weekly`
- `python -B main.py weekly --all`
- `python -B main.py ai-ready`

Rodar `python -B main.py` sem subcomando so imprime ajuda e nao chama a API.

## Modulos principais

### `src/client.py`

Responsavel por:

- centralizar todo acesso a API Strava;
- controlar limite de chamadas;
- gravar log de uso;
- ler e escrever cache;
- renovar token via OAuth;
- impedir chamadas quando o orcamento termina.

Classe principal: `StravaClient`

Erro de limite: `ApiBudgetExceeded`

### `src/analysis.py`

Responsavel por logica pura de analise:

- classificacao de atividade;
- zonas de frequencia cardiaca;
- cardiac drift;
- pace quando aplicavel;
- sRPE;
- montagem do registro para CSV;
- renderizacao do report Markdown.

Este modulo nao deve chamar API.

### `main.py`

Responsavel por orquestracao:

- CLI;
- index local;
- backfill;
- analyze por ID;
- latest;
- upsert no historico;
- escrita dos reports.
- escrita dos reports semanais.

### Wrappers legados

- `src/extract.py`
- `src/pace_analysis.py`
- `src/auth.py`

Eles existem por compatibilidade, mas devem delegar ao `StravaClient`.

## Fluxo do backfill

1. Carrega `data/cache/activity_index.json`.
2. Se indice nao existe, constroi a partir de pages cacheadas.
3. Se indice incompleto, baixa pages de summary dentro do limite.
4. Seleciona atividades com HR.
5. Pega a proxima atividade incompleta.
6. Busca `details` e `streams` usando cache obrigatorio.
7. Para Run/Walk, tambem tenta `laps`.
8. Calcula metricas.
9. Faz upsert em `data/performance_history.csv`.
10. Gera `data/reports/{activity_id}.md`.
11. Continua ate nao haver pendencias ou bater o limite.

## Fluxo do weekly

1. Le `data/performance_history.csv`.
2. Converte `start_date_local` para data.
3. Calcula ano e semana ISO-8601.
4. Gera Markdown em `data/weekly_reports/`.
5. Nomeia cada arquivo como `YYYY_semana_WW.md`.

O comando `weekly` nao chama a API.

## Fluxo do sync

1. Forca refresh somente de `summary_pages/page_001.json`.
2. Reconstrui `activity_index.json`.
3. Seleciona a atividade com HR mais recente.
4. Analisa a atividade.
5. Atualiza o report individual.
6. Gera o report semanal mais recente.
7. Gera o report AI-ready mais recente.

Esse e o comando recomendado para rodar pelo iPhone apos cadastrar uma atividade.

## Fluxo do ai-ready

1. Le `data/performance_history.csv`.
2. Seleciona a semana mais recente, ou a semana informada por `--year` e `--week`.
3. Renderiza contexto fixo do atleta.
4. Inclui o relatorio semanal consolidado.
5. Inclui dados estruturados das sessoes da semana.
6. Escreve `data/ai_reports/YYYY_semana_WW_ai.md`.

O comando `ai-ready` nao chama a API.

## Definicao de completa

Uma atividade com HR e considerada completa quando:

- existe `details.json`;
- existe `streams.json`;
- se for Run/Walk, existe `laps.json`;
- existe linha no CSV;
- existe report Markdown.

Markers de indisponibilidade podem ser usados para streams/laps sem dados no Strava.
