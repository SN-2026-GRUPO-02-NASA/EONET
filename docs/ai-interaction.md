# Histórico de Interação com IA — Grupo 02 (EONET)

Ferramenta utilizada: **Claude** (Anthropic). A IA foi usada como apoio para
estruturar o pipeline (script de coleta, SQL, workflow e painel), com revisão
e testes feitos pelo grupo em cada etapa.

---

## 1. Planejamento geral do projeto

**Objetivo do prompt:** entender o passo a passo completo da atividade
(estrutura de pastas, ordem das etapas, nomenclaturas exigidas) a partir do
PDF da atividade avaliativa, específico para o Grupo 02 / API EONET.

**Resposta da IA:** um roteiro em 11 passos cobrindo criação de organização e
repositório, configuração do Supabase, script de coleta, workflow, painel,
documentação e entrega.

**Acertos:** organizou corretamente a ordem das dependências (banco antes do
script, secrets antes do workflow).

---

## 2. Criação do banco de dados (`sql/setup.sql`)

**Objetivo do prompt:** gerar o script SQL com a tabela principal de eventos
EONET, a tabela de log `execucoes`, constraint `UNIQUE` para permitir upsert,
RLS e GRANTs conforme exigido no edital.

**Resposta da IA:** script com tabela `eonet_eventos` (chave natural
`evento_id`), tabela `execucoes` com `status` restrito por `check`, RLS
habilitado com política de leitura pública, e GRANTs separados para
`anon`/`authenticated` (SELECT) e `service_role` (ALL).

**Acertos:** evitou duplicação de dados ao definir `evento_id` como chave
única; já veio com índices para os filtros do painel.

**Erros / limitações:** o script assume que a geometria mais recente de cada
evento é um ponto; eventos com geometria em polígono precisam de tratamento
à parte (ficam só no campo `geometrias`, sem latitude/longitude).

**Outras informações:** o SQL foi testado no editor do SupaBase e as tabelas foram verificada no Table Editor.

---

## 3. Script de coleta (`scripts/fetch_nasa.py`)

**Objetivo do prompt:** criar um script Python que consulte a API EONET,
normalize os dados, deduplique antes do upsert (para evitar o erro
PostgreSQL 21000) e registre cada execução na tabela `execucoes`.

**Resposta da IA:** script com três tentativas de requisição à API, função de
normalização por evento, deduplicação por `evento_id`, envio em lotes
(`BATCH_SIZE`) via upsert (`on_conflict=evento_id`) e log final com status
`concluido`, `erro_parcial` ou `erro_critico`, encerrando com `sys.exit(1)`
em caso de falha.

**Acertos:** separar deduplicação do envio evitou o erro de chave duplicada
já conhecido de atividades anteriores.

---

## 4. Workflow do GitHub Actions (`update-data.yml`)

**Objetivo do prompt:** configurar execução automática (cron) e manual
(`workflow_dispatch`) do script, seguindo as boas práticas obrigatórias
(`permissions`, `concurrency`, `timeout-minutes`).

**Resposta da IA:** workflow com cron diário às 09h UTC, permissões restritas
a leitura do repositório, grupo de concorrência único e timeout de 10
minutos.

**Erros / limitações:** primeira tentativa do grupo salvou o arquivo SQL com
nome incorreto (`sql/sql.setup`); foi necessário renomear para
`sql/setup.sql` antes do workflow funcionar.

---

## 5. Painel (`index.html`)

**Objetivo do prompt:** criar um painel estático para o GitHub Pages que
consuma a API REST do Supabase, com filtro interativo, exibição da última
atualização (lida da tabela `execucoes`) e sanitização de dados externos.

**Resposta da IA:** página HTML/CSS/JS autônoma, com cards de eventos
coloridos por categoria, filtros por categoria e status, e função
`escapeHtml()` aplicada a todo valor vindo do banco antes de inserir no DOM.

**Outras informações:** a URL e a chave anos do SupaBase foram preenchidas.

---

## 6. Documentação (README e esta página)

**Objetivo do prompt:** gerar o `README.md` com arquitetura, links e
instruções de reprodução, e este histórico de interação com IA.

**Resposta da IA:** README estruturado conforme exigido na Tabela 05 do
edital (descrição, arquitetura, links, como configurar).
