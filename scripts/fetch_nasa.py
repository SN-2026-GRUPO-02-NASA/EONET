#!/usr/bin/env python3
"""
fetch_nasa.py | Pipeline EONET (NASA) -> Supabase | Grupo 02

Fluxo:
  1. Consulta a API EONET v3 (não exige chave)
  2. Normaliza os campos (1 linha por evento)
  3. Deduplica por evento_id (evita o erro PostgreSQL 21000)
  4. Faz upsert no Supabase em lotes
  5. Registra a execução na tabela `execucoes`
  6. Termina com sys.exit(1) se houve erro (visível no GitHub Actions)

Variáveis de ambiente (Secrets no GitHub Actions):
  SUPABASE_URL          -> URL do projeto
  SUPABASE_SERVICE_KEY  -> secret key (service_role)
Opcionais:
  EONET_STATUS (all|open|closed, padrão: all)
  EONET_DAYS   (janela em dias, padrão: 365)
  BATCH_SIZE   (tamanho do lote, padrão: 200)
"""

import os
import sys
import time
from datetime import datetime, timezone

import requests

EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
TABELA = "eonet_eventos"

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
EONET_STATUS = os.environ.get("EONET_STATUS", "all")
EONET_DAYS = os.environ.get("EONET_DAYS", "365")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "200"))


def agora_iso():
    return datetime.now(timezone.utc).isoformat()


def headers_supabase(extra=None):
    """Cabeçalhos para a API REST do Supabase."""
    h = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    # Chaves no formato antigo (JWT) também vão em Authorization;
    # as novas (sb_secret_...) usam somente o cabeçalho apikey.
    if not SUPABASE_KEY.startswith("sb_"):
        h["Authorization"] = f"Bearer {SUPABASE_KEY}"
    if extra:
        h.update(extra)
    return h


# ---------------------------------------------------------------------
# 1) Coleta
# ---------------------------------------------------------------------
def buscar_eventos():
    params = {"status": EONET_STATUS, "days": EONET_DAYS}
    ultimo_erro = None
    for tentativa in range(1, 4):
        try:
            resp = requests.get(EONET_URL, params=params, timeout=60)
            resp.raise_for_status()
            eventos = resp.json().get("events", [])
            print(f"[API] {len(eventos)} eventos recebidos (tentativa {tentativa})")
            return eventos
        except (requests.RequestException, ValueError) as e:
            ultimo_erro = e
            print(f"[API] falha na tentativa {tentativa}: {e}")
            time.sleep(5 * tentativa)
    raise RuntimeError(f"API EONET indisponível: {ultimo_erro}")


# ---------------------------------------------------------------------
# 2) Normalização
# ---------------------------------------------------------------------
def normalizar(evento):
    geometrias = evento.get("geometry") or []
    # geometria mais recente (pela data)
    ultima = max(geometrias, key=lambda g: g.get("date") or "") if geometrias else {}

    lat = lon = None
    coords = ultima.get("coordinates")
    if ultima.get("type") == "Point" and isinstance(coords, list) and len(coords) >= 2:
        lon, lat = coords[0], coords[1]  # EONET usa [longitude, latitude]

    categoria = (evento.get("categories") or [{}])[0]
    fonte = (evento.get("sources") or [{}])[0]

    return {
        "evento_id": evento.get("id"),
        "titulo": evento.get("title") or "(sem título)",
        "descricao": evento.get("description"),
        "link": evento.get("link"),
        "fechado": evento.get("closed") is not None,
        "data_fechamento": evento.get("closed"),
        "categoria_id": categoria.get("id"),
        "categoria_titulo": categoria.get("title"),
        "fonte_id": fonte.get("id"),
        "fonte_url": fonte.get("url"),
        "data_ultima_geometria": ultima.get("date"),
        "latitude": lat,
        "longitude": lon,
        "magnitude_valor": ultima.get("magnitudeValue"),
        "magnitude_unidade": ultima.get("magnitudeUnit"),
        "geometrias": geometrias,
        "atualizado_em": agora_iso(),
    }


# ---------------------------------------------------------------------
# 3) Deduplicação (mantém a última ocorrência de cada evento_id)
# ---------------------------------------------------------------------
def deduplicar(linhas):
    unicos = {}
    for linha in linhas:
        if linha["evento_id"]:
            unicos[linha["evento_id"]] = linha
    print(f"[DEDUP] {len(linhas)} -> {len(unicos)} registros únicos")
    return list(unicos.values())


# ---------------------------------------------------------------------
# 4) Upsert em lotes
# ---------------------------------------------------------------------
def upsert_lote(lote):
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}?on_conflict=evento_id"
    h = headers_supabase({"Prefer": "resolution=merge-duplicates,return=minimal"})
    resp = requests.post(url, headers=h, json=lote, timeout=60)
    if resp.status_code not in (200, 201, 204):
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")


def enviar_em_lotes(linhas):
    total_lotes = 0
    lotes_ok = 0
    erros = 0
    processados = 0
    for i in range(0, len(linhas), BATCH_SIZE):
        lote = linhas[i : i + BATCH_SIZE]
        total_lotes += 1
        try:
            upsert_lote(lote)
            lotes_ok += 1
            processados += len(lote)
            print(f"[LOTE {total_lotes}] {len(lote)} registros gravados")
        except Exception as e:  # noqa: BLE001
            erros += 1
            print(f"[LOTE {total_lotes}] ERRO: {e}", file=sys.stderr)
    return processados, total_lotes, lotes_ok, erros


# ---------------------------------------------------------------------
# 5) Log da execução
# ---------------------------------------------------------------------
def registrar_execucao(inicio, processados, lotes, erros, status, mensagem=None):
    corpo = {
        "iniciado_em": inicio,
        "finalizado_em": agora_iso(),
        "registros_processados": processados,
        "lotes": lotes,
        "erros": erros,
        "status": status,
        "mensagem": mensagem,
    }
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/execucoes",
            headers=headers_supabase({"Prefer": "return=minimal"}),
            json=corpo,
            timeout=30,
        )
        if resp.status_code not in (200, 201, 204):
            print(f"[LOG] falha ao registrar execução: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"[LOG] falha ao registrar execução: {e}", file=sys.stderr)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERRO: defina SUPABASE_URL e SUPABASE_SERVICE_KEY.", file=sys.stderr)
        sys.exit(1)

    inicio = agora_iso()

    try:
        eventos = buscar_eventos()
        linhas = deduplicar([normalizar(e) for e in eventos])
        if not linhas:
            raise RuntimeError("Nenhum evento retornado pela API.")
    except Exception as e:  # noqa: BLE001
        print(f"ERRO CRÍTICO: {e}", file=sys.stderr)
        registrar_execucao(inicio, 0, 0, 1, "erro_critico", str(e)[:500])
        sys.exit(1)

    processados, lotes, lotes_ok, erros = enviar_em_lotes(linhas)

    if erros == 0:
        status = "concluido"
    elif lotes_ok > 0:
        status = "erro_parcial"
    else:
        status = "erro_critico"

    registrar_execucao(inicio, processados, lotes, erros, status)
    print(f"[FIM] status={status} processados={processados} lotes={lotes} erros={erros}")

    if status != "concluido":
        sys.exit(1)


if __name__ == "__main__":
    main()
