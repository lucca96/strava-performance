# Especificacao dos Reports Markdown

## Objetivo

Os reports Markdown devem ser legiveis por humano e faceis de enviar para uma AI. A prioridade e clareza, estrutura estavel e dados suficientes para avaliar performance.

## Reports atuais por atividade

Pasta: `data/reports/`

Nome: `{activity_id}.md`

Secoes atuais:

- titulo da atividade;
- `Resumo`;
- `Frequencia cardiaca`;
- `Pace`, somente quando existe pace;
- `Dados faltantes`, somente quando existe dado faltante;
- `Insights`, somente quando existe insight.

Nao incluir:

- secao `Status`, porque reports completos nao precisam mostrar isso.

## Campos no resumo

- Activity ID
- Tipo Strava
- Categoria do projeto
- Data
- Distancia
- Tempo em movimento
- RPE
- Carga sRPE
- Suffer score

## Campos de frequencia cardiaca

- FC media
- FC maxima
- Cardiac drift
- Tempo e percentual em Z1-Z5

## Campos de pace

Somente para atividades com pace relevante:

- pace medio;
- consistencia;
- drift de pace.

## Relatorio semanal

Pasta: `data/weekly_reports/`

Nome: `YYYY_semana_WW.md`

O ano e a semana seguem ISO-8601.

Formato atual:

- semana de referencia;
- total de sessoes;
- total de minutos;
- carga sRPE total;
- carga por categoria;
- distribuicao de zonas;
- maiores cargas da semana;
- alertas de fadiga;
- tendencias vs semanas anteriores;
- insights para preparador fisico;
- prompt final para AI analisar.

## Estilo para AI

Usar:

- headings curtos;
- bullets com uma metrica por linha;
- nomes de campos estaveis;
- unidades explicitas;
- texto sem decoracao visual excessiva.
