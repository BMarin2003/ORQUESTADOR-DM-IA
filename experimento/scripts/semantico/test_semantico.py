"""
Pruebas del instrumento EXPLORATORIO cl2_recall_semantico.

  py -m pytest experimento/scripts/semantico/test_semantico.py -q

Las pruebas unitarias no necesitan base de datos ni el modelo (usan un embedder de juguete). La prueba
de integración se activa solo si SEMANTICO_DSN_PRUEBA apunta a una base DESECHABLE con
motor/migrations/001_schema.sql cargado: siembra campañas sintéticas y corre embeber -> recall -> A2 de punta
a punta. NUNCA apuntarla a dmia_dev: la prueba crea y borra datos.
"""
import hashlib
import json
import os
import random
import re
import sys
import uuid
from pathlib import Path

import numpy as np
import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comun as C                     # noqa: E402
import sensibilidad_semantico as SS   # noqa: E402


class EmbedderJuguete:
    """Bolsa de raíces (5 letras) proyectada a 1024 dimensiones por hash, normalizada. Determinista."""

    def __call__(self, textos):
        M = np.zeros((len(textos), C.DIM), dtype=np.float32)
        for i, t in enumerate(textos):
            for w in re.findall(r"\w+", t.lower()):
                M[i, int(hashlib.md5(w[:5].encode()).hexdigest(), 16) % C.DIM] += 1
            n = np.linalg.norm(M[i])
            if n:
                M[i] /= n
        return M


# ---------------------------------------------------------------- unitarias
def test_dividir_oraciones():
    t = "Entras a la taberna. «¿Quién eres?», pregunta Yenna.\nEl fuego crepita… Sí.\n\nNadie responde a tu pregunta."
    assert C.dividir_oraciones(t) == ["Entras a la taberna.", "«¿Quién eres?», pregunta Yenna.", "El fuego crepita…",
                                      "Nadie responde a tu pregunta."]


def _deltas_variados():
    return [
        {"turn_id": 10, "entity_type": "npc", "field_name": "status", "old_value": "alive", "new_value": "dead", "entity_name": "Yenna"},
        {"turn_id": 11, "entity_type": "npc", "field_name": "status", "old_value": "dead", "new_value": "alive", "entity_name": "Yenna"},
        {"turn_id": 12, "entity_type": "npc", "field_name": "affinity", "old_value": 10, "new_value": 30, "entity_name": "Bors"},
        {"turn_id": 13, "entity_type": "npc", "field_name": "affinity", "old_value": 30, "new_value": 40, "entity_name": "Bors"},
        {"turn_id": 14, "entity_type": "npc", "field_name": "affinity", "old_value": None, "new_value": 0, "entity_name": "Bors"},
        {"turn_id": 15, "entity_type": "npc", "field_name": "affinity", "old_value": None, "new_value": -70, "entity_name": "Ilda"},
        {"turn_id": 16, "entity_type": "quest", "field_name": "status", "old_value": "active", "new_value": "completed", "entity_name": "El pozo"},
        {"turn_id": 17, "entity_type": "quest", "field_name": "status", "old_value": "unknown", "new_value": "active", "entity_name": "El pozo"},
    ]


def test_mismo_conjunto_de_eventos_que_jericho():
    ds = _deltas_variados()
    eventos = [e for e in (C.evento_desde_delta(d) for d in ds) if e]
    assert len(eventos) == C.RV.jericho_qa_recall(ds, {})["n_total"] == 4
    assert [(e["campo"], e["estado"]) for e in eventos] == [("npc.status", "dead"), ("npc.affinity", "loyal"),
                                                            ("npc.affinity", "hostile"), ("quest.status", "completed")]


def test_hay_consulta_y_parafrasis_para_cada_estado_de_jericho():
    estados = {("npc.status", k) for k in C.RV._KEYWORDS_NPC_STATUS} | {("quest.status", k) for k in C.RV._KEYWORDS_QUEST_STATUS} \
        | {("npc.affinity", k) for k in C.RV._KEYWORDS_AFINIDAD_BANDA}
    assert estados == set(C._CONSULTA) == set(SS.PARAFRASIS)


def test_oraciones_de_la_a2_no_contienen_lexemas_de_jericho():
    SS._assert_sin_lexema()


def test_vec_literal_ida_y_vuelta():
    v = np.random.default_rng(0).normal(size=C.DIM)
    w = np.array(json.loads(C.vec_literal(v)))
    assert w.shape == (C.DIM,) and np.allclose(v, w, rtol=1e-6)


def test_nulo_excluye_la_vecindad_del_evento():
    s = {u: 0.1 for u in range(1, 101)}
    s[50] = 0.9
    s[54] = 0.8                              # dentro de la exclusión: no puede entrar al nulo
    nul = C.nulo(s, 50)
    assert nul.max() == pytest.approx(0.1)
    assert len(nul) == 100 - (2 * (C.EXCLUSION + C.VENTANA) + 1)
    r = C.decidir(C.puntuacion_ventana(s, 50), nul)
    assert r["reconocido"] and r["margen"] == pytest.approx(0.8)


def test_tasa_de_azar_cercana_al_5_por_ciento():
    rng = np.random.default_rng(1)
    s = {u: float(x) for u, x in enumerate(rng.normal(size=1400), start=1)}
    tasa = np.mean([C.decidir(C.puntuacion_ventana(s, t), C.nulo(s, t))["reconocido"] for t in range(20, 1381, 7)])
    assert 0.02 <= tasa <= 0.09


def test_reemplazo_solo_toca_la_ventana():
    s = {u: 0.2 for u in range(1, 81)}
    ev = {"turno": 40}
    antes = C.evaluar_evento(s, ev)
    despues = C.evaluar_evento(s, ev, {40: 0.95})
    assert despues["q95"] == antes["q95"] and despues["s_real"] == 0.95


def test_sql_no_ordena_por_distancia():
    # Sin ORDER BY <distancia> LIMIT no se puede usar un índice aproximado (HNSW/IVF): búsqueda exacta.
    assert "ORDER BY" not in C.SQL_MAX_POR_TURNO.upper() and "LIMIT" not in C.SQL_MAX_POR_TURNO.upper()


# ---------------------------------------------------------------- integración (solo con base desechable)
DSN = os.environ.get("SEMANTICO_DSN_PRUEBA")
RELLENO = ["El viento sopla entre las casas.", "Una campana suena a lo lejos.", "Los mercaderes recogen sus puestos.",
           "La lluvia golpea los tejados de pizarra.", "Un perro ladra en el callejón.", "Las antorchas iluminan la muralla."]


def _sembrar(conn, rng, arquitectura, n_turnos=80):
    tenant = conn.execute("INSERT INTO tenants (name) VALUES ('prueba-semantico') RETURNING id").fetchone()[0]
    user = conn.execute("INSERT INTO users (tenant_id, email, display_name) VALUES (%s, %s, 'p') RETURNING id",
                        (tenant, f"{uuid.uuid4()}@x")).fetchone()[0]
    cid = conn.execute("INSERT INTO campaigns (tenant_id, owner_id, title, architecture) VALUES (%s,%s,'p',%s) RETURNING id",
                       (tenant, user, arquitectura)).fetchone()[0]
    npc = conn.execute("INSERT INTO npcs (tenant_id, campaign_id, name) VALUES (%s,%s,'Yenna Roldós') RETURNING id", (tenant, cid)).fetchone()[0]
    eventos = {20: "Yenna Roldós cae al suelo y muere ante tus ojos.", 50: "Yenna Roldós ha desaparecido sin dejar rastro."}
    for t in range(0, n_turnos + 1):
        texto = " ".join(rng.sample(RELLENO, 3)) + (" " + eventos[t] if t in eventos else "")
        conn.execute("INSERT INTO turn_log (tenant_id, campaign_id, turn_id, player_buffer, dm_output) VALUES (%s,%s,%s,'[]'::jsonb,%s)",
                     (tenant, cid, t, texto))
    for t, nuevo, viejo in ((20, "dead", "alive"), (50, "missing", "dead")):
        conn.execute("INSERT INTO state_deltas (tenant_id, campaign_id, turn_id, entity_type, entity_id, field_name, old_value, new_value, source, evidence) "
                     "VALUES (%s,%s,%s,'npc',%s,'status',%s,%s,'extracted','cita')",
                     (tenant, cid, t, npc, json.dumps(viejo), json.dumps(nuevo)))
    return str(cid)


@pytest.mark.skipif(not DSN, reason="sin SEMANTICO_DSN_PRUEBA (base desechable)")
def test_de_punta_a_punta(tmp_path, monkeypatch):
    import psycopg
    import db as bd
    import embeber_corpus as EC
    import recall_semantico as RS
    monkeypatch.setattr(bd, "DSN", DSN)
    monkeypatch.setattr(C, "SALIDA_DATOS", tmp_path / "datos")
    monkeypatch.setattr(C, "SALIDA_DOCS", tmp_path / "docs")
    monkeypatch.setattr(C, "MANIFIESTO", tmp_path / "docs" / "manifiesto_embeddings.json")
    rng = random.Random(7)
    with psycopg.connect(DSN, autocommit=True) as conn:
        pares = [{"par": f"{i:02d}", "campaign_g1": _sembrar(conn, rng, "mas"), "campaign_g2": _sembrar(conn, rng, "monolithic")}
                 for i in (1, 2, 3)]
    import pares as _pares
    monkeypatch.setattr(_pares, "todos", lambda: pares)
    monkeypatch.setattr(C, "HASTA", 80)
    emb = EmbedderJuguete()
    EC.main(["--revision", "prueba"], embedder=emb)
    with psycopg.connect(DSN) as conn:
        n = conn.execute(f"SELECT count(*) FROM {C.TABLA} WHERE campaign_id = %s", (pares[0]["campaign_g1"],)).fetchone()[0]
        assert n >= 80 * 3
        plan = "\n".join(r[0] for r in conn.execute("EXPLAIN " + C.SQL_MAX_POR_TURNO, (C.vec_literal(np.ones(C.DIM)), pares[0]["campaign_g1"], 1, 80)))
        assert "hnsw" not in plan.lower()
    EC.main(["--revision", "prueba"], embedder=emb)             # reanudar: no duplica
    with psycopg.connect(DSN) as conn:
        assert conn.execute(f"SELECT count(*) FROM {C.TABLA} WHERE campaign_id = %s", (pares[0]["campaign_g1"],)).fetchone()[0] == n
    todos, por_campana, comp, ac = RS.main([], embedder=emb)
    assert len(todos) == 12                                      # 2 eventos x 6 campañas
    assert all(f["reconocido"] == 1 for f in todos)              # la ventana real contiene la oración del evento
    assert (tmp_path / "docs" / "cl2_recall_semantico.md").exists()
    filas, res = SS.main(["--n", "4"], embedder=emb)
    assert set(res) == {"SQ1", "SQ2", "SC1", "SC2"}
    assert all(f["margen_despues"] < f["margen_antes"] for f in filas if f["perturbacion"] == "SQ2")
    assert (tmp_path / "docs" / "sensibilidad_semantico.md").exists()
