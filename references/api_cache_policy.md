# Politica de API e Cache

## Regra principal

Nenhum codigo do pipeline deve chamar a API Strava diretamente com `requests`, exceto o cliente central `src/client.py`.

## Limite de chamadas

- Variavel: `STRAVA_MAX_API_CALLS`
- Padrao atual: `100`
- O limite vale por execucao do programa.
- Cada request real incrementa `calls_made`.
- Ao atingir o limite, o cliente deve parar com `ApiBudgetExceeded`.

## Cache obrigatorio

Se um arquivo de cache existe, o endpoint correspondente nao deve ser chamado.

Estrutura:

- `data/cache/token.json`
- `data/cache/activity_index.json`
- `data/cache/summary_pages/page_001.json`
- `data/cache/summary_pages/page_002.json`
- `data/cache/activities/{activity_id}/details.json`
- `data/cache/activities/{activity_id}/streams.json`
- `data/cache/activities/{activity_id}/laps.json`

## Endpoints usados

- `POST /oauth/token`
- `GET /athlete/activities`
- `GET /activities/{activity_id}`
- `GET /activities/{activity_id}/streams`
- `GET /activities/{activity_id}/laps`

## Log de API

Arquivo: `data/api_usage_log.csv`

Campos:

- `timestamp_utc`
- `method`
- `endpoint`
- `activity_id`
- `status_code`
- `rate_limit_limit`
- `rate_limit_usage`
- `calls_made`
- `calls_remaining`

## Praticas seguras

- Antes de rodar backfill real, conferir se o limite desejado esta claro.
- Para teste pequeno: `STRAVA_MAX_API_CALLS=3`.
- Para backfill normal: padrao 100.
- Nunca remover cache para "forcar atualizacao" sem intencao explicita.
- Nunca criar novo script que chame Strava fora do `StravaClient`.
