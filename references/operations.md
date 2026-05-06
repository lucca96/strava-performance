# Operacao do Pipeline

## Comandos

Mostrar ajuda, sem API:

```powershell
python -B main.py
```

Indexar atividades:

```powershell
python -B main.py index
```

Backfill incremental:

```powershell
python -B main.py backfill
```

Analisar atividade especifica:

```powershell
python -B main.py analyze --activity-id 123456789
```

Analisar atividade mais recente:

```powershell
python -B main.py latest
```

Sincronizar apos cadastrar atividade no Strava:

```powershell
python -B main.py sync
```

Gerar relatorio semanal mais recente:

```powershell
python -B main.py weekly
```

Gerar uma semana especifica:

```powershell
python -B main.py weekly --year 2025 --week 2
```

Gerar todas as semanas do historico:

```powershell
python -B main.py weekly --all
```

## Limite de API

Padrao:

```powershell
$env:STRAVA_MAX_API_CALLS="100"
```

Teste conservador:

```powershell
$env:STRAVA_MAX_API_CALLS="3"
python -B main.py backfill
```

## Rotina recomendada

Durante desenvolvimento:

1. Rodar testes.
2. Rodar `python -B main.py`.
3. Se for chamar API, confirmar limite.
4. Rodar `backfill`.
5. Conferir `data/api_usage_log.csv`.
6. Conferir `data/performance_history.csv`.
7. Conferir reports em `data/reports/`.
8. Rodar `python -B main.py weekly --all` para atualizar os reports semanais.

Uso pelo iPhone:

- caminho recomendado: iOS Shortcuts disparando GitHub Actions;
- comando executado pelo workflow: `python -B main.py sync`;
- detalhes em `references/iphone_flow.md`.

## Testes

Comando:

```powershell
python -B -m unittest discover -s tests -v
```

Os testes usam dados fake e nao devem chamar API real.

## Estado atual conhecido

Em 2026-05-06:

- backfill processou atividades com HR ate nao haver pendencias locais;
- CSV possui 79 linhas;
- reports possuem 79 arquivos;
- categorias no CSV: grappling, preparacao_fisica, outros;
- reports foram regenerados sem secao `Status`.
- reports semanais usam `YYYY_semana_WW.md`, com semana ISO-8601.

## Cuidados

- Nao apagar `data/cache/` sem motivo.
- Nao expor `.env` ou token em prompts para AI.
- Nao rodar scripts antigos de exploracao sem entender limite/cache.
- `get_token.py` e utilitario de OAuth inicial, nao pipeline de coleta.
