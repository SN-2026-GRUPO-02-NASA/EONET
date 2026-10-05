# EONET — Pipeline de Dados da NASA

Pipeline de dados completo a partir da API aberta **EONET** (Earth Observatory
Natural Event Tracker) da NASA, que rastreia eventos naturais em curso no
planeta — incêndios florestais, tempestades severas, erupções vulcânicas,
gelo marinho e lacustre, entre outros.

**Grupo 02** · Integrantes: Antonela, Brenda e Ikaro

## Arquitetura

```
EONET API  -->  GitHub Actions (cron diário)  -->  Supabase (PostgreSQL)  -->  GitHub Pages (index.html)
```

1. **Coleta** — `scripts/fetch_nasa.py` consulta `eonet.gsfc.nasa.gov/api/v3/events`,
   normaliza os campos e deduplica os registros.
2. **Armazenamento** — os dados são gravados via upsert (em lotes) na API REST
   do Supabase, num projeto PostgreSQL com RLS ativo.
3. **Automação** — `.github/workflows/update-data.yml` executa o script todos
   os dias (cron) e também sob demanda (`workflow_dispatch`).
4. **Publicação** — `index.html`, hospedado no GitHub Pages, consulta a API
   REST do Supabase diretamente no navegador (somente leitura, com a chave
   anon) e exibe os eventos com filtros.

## Links

- Painel: `https://SN-2026-GRUPO-02-NASA.github.io/EONET/`
- Repositório: `https://github.com/SN-2026-GRUPO-02-NASA/EONET`
- API usada: https://eonet.gsfc.nasa.gov/api/v3/events (não exige chave)

## Estrutura do repositório

```
EONET/
├── index.html                       # painel (GitHub Pages)
├── README.md
├── scripts/
│   └── fetch_nasa.py                # coleta, deduplicação e upsert
├── sql/
│   └── setup.sql                    # tabelas, constraint, RLS e GRANTs
├── .github/workflows/
│   └── update-data.yml              # agendamento do pipeline
└── docs/
    ├── tutorial.pdf
    ├── ai-interaction.md
    ├── reflexao.md
    └── apresentacao.pdf
```

## Como reproduzir o projeto

1. Crie um projeto no Supabase (região South America) e rode `sql/setup.sql`
   no SQL Editor para criar as tabelas `eonet_eventos` e `execucoes`.
2. No GitHub, cadastre os Secrets `SUPABASE_URL` e `SUPABASE_SERVICE_KEY`
   (Settings → Secrets and variables → Actions).
3. Em `index.html`, preencha `SUPABASE_URL` e `SUPABASE_ANON_KEY` com a URL
   e a publishable key do projeto (Project Settings → API).
4. Ative o GitHub Pages (Settings → Pages → branch `main`, pasta root).
5. Rode o workflow manualmente pela aba Actions (`Run workflow`) para a
   primeira carga de dados.

## Divisão de responsabilidades

| Área | Responsável |
|---|---|
| Pipeline (`fetch_nasa.py`, workflow) | _preencher_ |
| Banco de dados (`setup.sql`, modelagem) | _preencher_ |
| Painel (`index.html`) | _preencher_ |
| Documentação e apresentação | _preencher_ |

## Uso de IA generativa

_Preencher: utilizada ou não; se sim, qual trilha e ver `docs/ai-interaction.md`
e `docs/reflexao.md`._
