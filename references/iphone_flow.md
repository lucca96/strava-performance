# Fluxo iPhone

Objetivo: rodar o pipeline logo depois de cadastrar uma atividade no Strava, com baixo custo e alta aderencia.

## Recomendacao principal

Usar iPhone Shortcuts para disparar um GitHub Actions workflow privado.

Motivos:

- nao precisa manter computador ligado;
- custo baixo para uso pessoal;
- roda Python em ambiente limpo;
- salva CSV e Markdown no repo;
- pode ser disparado manualmente logo apos cadastrar a atividade.

## Fluxo de uso

1. Cadastrar atividade no Strava.
2. Ajustar titulo e RPE.
3. Abrir um Atalho no iPhone chamado `Sync Strava`.
4. O atalho dispara o workflow `iPhone sync`.
5. O workflow roda `python -B main.py sync`.
6. O pipeline atualiza:
   - `data/performance_history.csv`;
   - `data/reports/{activity_id}.md`;
   - `data/weekly_reports/YYYY_semana_WW.md`.
7. O workflow commita os arquivos gerados.
8. O usuario abre o Markdown semanal ou manda para AI.

## Comando usado

```powershell
python -B main.py sync
```

O comando `sync`:

- atualiza a pagina 1 do Strava mesmo se ela ja estiver em cache;
- reconstrui o indice local;
- analisa a atividade com HR mais recente;
- gera o relatorio semanal mais recente.

## Secrets necessarios no GitHub

- `STRAVA_CLIENT_ID`
- `STRAVA_CLIENT_SECRET`
- `STRAVA_REFRESH_TOKEN`

Nao commitar `.env` nem `data/cache/token.json`.

## Workflow

Arquivo:

- `.github/workflows/iphone-sync.yml`

O workflow pode ser disparado manualmente pelo GitHub ou por iOS Shortcuts.

## Atalho iOS

Criar um atalho com uma chamada HTTP para a API do GitHub:

- Metodo: `POST`
- Endpoint: `https://api.github.com/repos/OWNER/REPO/actions/workflows/iphone-sync.yml/dispatches`
- Headers:
  - `Authorization: Bearer GITHUB_FINE_GRAINED_TOKEN`
  - `Accept: application/vnd.github+json`
  - `Content-Type: application/json`
- Body:

```json
{
  "ref": "main"
}
```

O token do GitHub deve ter permissao minima para disparar workflows no repo privado.

## Alternativa mais simples, mas menos autonoma

Usar app GitHub no iPhone:

1. Abrir repo.
2. Ir em Actions.
3. Selecionar `iPhone sync`.
4. Tocar em `Run workflow`.

Isso evita criar token para Shortcuts, mas exige mais cliques.

## Alternativa local

Usar iOS Shortcuts com `Run Script over SSH` para chamar um computador ligado:

```bash
cd /path/to/Strava
python -B main.py sync
```

Essa opcao e barata, mas depende do computador estar ligado e acessivel.
