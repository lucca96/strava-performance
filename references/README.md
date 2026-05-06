# Referencias do Projeto Strava Performance

Ultima atualizacao: 2026-05-06

Esta pasta e a memoria tecnica do projeto. Sempre que a arquitetura, os dados, as regras de classificacao, o formato dos relatorios ou o fluxo operacional mudarem, atualize estes arquivos junto com o codigo.

## Como usar com AI

Para dar contexto a uma AI, envie os arquivos nesta ordem:

1. `ai_handoff.md`
2. `project_context.md`
3. `architecture.md`
4. `data_model.md`
5. `report_spec.md`
6. `operations.md`

## Arquivos

- `ai_handoff.md`: resumo curto e direto para uma AI continuar o trabalho.
- `project_context.md`: objetivo, publico, escopo e decisoes de produto.
- `architecture.md`: desenho tecnico atual do pipeline.
- `api_cache_policy.md`: regras de seguranca para cota da API Strava.
- `data_model.md`: CSV, cache, reports e campos principais.
- `report_spec.md`: formato esperado dos relatorios Markdown.
- `operations.md`: comandos seguros e rotina de uso.
- `iphone_flow.md`: fluxo recomendado para rodar pelo iPhone.
- `changelog.md`: historico de decisoes importantes.

## Regra de manutencao

Se uma mudanca afetar qualquer um destes pontos, atualize a referencia correspondente:

- limite de API ou comportamento de cache;
- comandos da CLI;
- campos do CSV;
- classificacao de atividades;
- formato dos reports;
- metricas e insights;
- premissas esportivas para grappling/preparacao fisica.
