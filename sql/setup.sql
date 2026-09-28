-- =====================================================================
-- setup.sql | EONET-DB | Grupo 02
-- Execute no Supabase: SQL Editor -> New query -> colar -> Run
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1) Tabela principal: eventos naturais da NASA EONET
--    1 linha por evento (chave natural = evento_id, ex.: EONET_1234)
-- ---------------------------------------------------------------------
create table if not exists public.eonet_eventos (
  id                    bigserial primary key,
  evento_id             text        not null,
  titulo                text        not null,
  descricao             text,
  link                  text,
  fechado               boolean     not null default false,
  data_fechamento       timestamptz,
  categoria_id          text,
  categoria_titulo      text,
  fonte_id              text,
  fonte_url             text,
  data_ultima_geometria timestamptz,
  latitude              double precision,
  longitude             double precision,
  magnitude_valor       double precision,
  magnitude_unidade     text,
  geometrias            jsonb,
  atualizado_em         timestamptz not null default now(),
  -- chave natural: permite upsert (on_conflict=evento_id) sem duplicatas
  constraint eonet_eventos_evento_id_key unique (evento_id)
);

create index if not exists idx_eonet_categoria on public.eonet_eventos (categoria_titulo);
create index if not exists idx_eonet_fechado   on public.eonet_eventos (fechado);
create index if not exists idx_eonet_data      on public.eonet_eventos (data_ultima_geometria desc);

-- ---------------------------------------------------------------------
-- 2) Tabela de log do pipeline: execucoes
-- ---------------------------------------------------------------------
create table if not exists public.execucoes (
  id                    bigserial primary key,
  iniciado_em           timestamptz not null default now(),
  finalizado_em         timestamptz,
  registros_processados integer     not null default 0,
  lotes                 integer     not null default 0,
  erros                 integer     not null default 0,
  status                text        not null
                        check (status in ('concluido', 'erro_parcial', 'erro_critico')),
  mensagem              text
);

create index if not exists idx_execucoes_iniciado on public.execucoes (iniciado_em desc);

-- ---------------------------------------------------------------------
-- 3) Row Level Security (RLS) + leitura pública
-- ---------------------------------------------------------------------
alter table public.eonet_eventos enable row level security;
alter table public.execucoes     enable row level security;

drop policy if exists "leitura publica eonet_eventos" on public.eonet_eventos;
create policy "leitura publica eonet_eventos"
  on public.eonet_eventos
  for select
  to anon, authenticated
  using (true);

drop policy if exists "leitura publica execucoes" on public.execucoes;
create policy "leitura publica execucoes"
  on public.execucoes
  for select
  to anon, authenticated
  using (true);

-- ---------------------------------------------------------------------
-- 4) GRANTs explícitos
--    SELECT para anon/authenticated | ALL para service_role
-- ---------------------------------------------------------------------
grant usage on schema public to anon, authenticated, service_role;

grant select on public.eonet_eventos to anon, authenticated;
grant select on public.execucoes     to anon, authenticated;

grant all on public.eonet_eventos to service_role;
grant all on public.execucoes     to service_role;

grant usage, select on all sequences in schema public to service_role;
