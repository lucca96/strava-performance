# Strava Performance Analytics

Projeto pessoal de engenharia e análise de dados esportivos desenvolvido para transformar atividades do Strava em métricas de desempenho, carga de treino e relatórios semanais.

## Objetivo

O projeto foi criado para organizar dados de treino e gerar uma visão mais estruturada da evolução esportiva, combinando informações como:

* duração e distância das atividades;
* frequência cardíaca e zonas de intensidade;
* percepção de esforço (RPE);
* carga de treino por sessão;
* consistência e variação de ritmo;
* relatórios semanais de desempenho;
* análises preparadas para uso com modelos de IA.

## Arquitetura

Fluxo principal do projeto:

Strava API
↓
Coleta e cache local
↓
Processamento das atividades
↓
Histórico estruturado
Relatórios por atividade
Relatórios semanais
Relatórios preparados para análise por IA

## Estrutura

* `main.py`
* `explore_strava.py`
* `get_token.py`
* `requirements.txt`
* `src/`
* `tests/`
* `iphone_app/`
* `references/`
* `.env.example`

## Principais componentes

* `main.py`: orquestra coleta, processamento e geração de relatórios.
* `src/client.py`: integração com a API do Strava e controle de chamadas.
* `src/analysis.py`: classificação e análise das atividades.
* `src/weekly_report.py`: consolidação semanal.
* `src/ai_ready_report.py`: geração de relatórios estruturados para análise assistida por IA.
* `tests/`: testes do pipeline e das regras de análise.

## Privacidade

A versão pública deste repositório contém somente código e estrutura do projeto.

Dados reais de atividades, horários, locais de treino, métricas fisiológicas e credenciais foram deliberadamente removidos do repositório e do histórico Git.

Arquivos gerados localmente ficam protegidos pelo `.gitignore`.

## Tecnologias

* Python
* Strava API
* CSV e JSON
* automação de relatórios
* testes automatizados
* APIs REST

## Contexto

Este projeto começou como uma ferramenta pessoal para acompanhamento de performance esportiva e evoluiu para um pequeno pipeline de dados com coleta, transformação, persistência, análise e geração de relatórios.

A integração original com a API do Strava depende de credenciais e disponibilidade da API. O objetivo deste repositório público é demonstrar a arquitetura, o processamento e as decisões de engenharia do projeto, sem expor dados pessoais.

