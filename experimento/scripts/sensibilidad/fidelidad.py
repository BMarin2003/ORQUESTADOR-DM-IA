"""
PRUEBA DE FIDELIDAD: el recálculo de los instrumentos sobre TEXTO (instrumentos_texto.py,
con el Contexto reconstruido por datos.py) debe reproducir lo que el motor guardó en
`turn_validation` al generar cada turno.

  * Numéricos (qn1_ttr, qn1_ngram_repeticion, qn1_legibilidad_fh,
    cl2_lugar_jaccard_similarity, cr2_entidad_grafo_densidad): coincidencia a los
    decimales de la columna (3; qn1_legibilidad_fh es numeric(6,2), así que 2).
  * Booleanos y cr2_nombres_no_reconocidos: igualdad exacta. Se añaden turnos con
    marca positiva guardada (los positivos son raros y una muestra aleatoria casi no
    los contiene).
  * Diferencias legítimas conocidas (no son un fallo del recálculo): el estado de PNJ
    se reconstruye desde state_deltas; el HP del PJ es el actual (no se guarda su
    historia); los objetos con portador se leen tal como están hoy; las tiradas se
    recalculan con motor/jugador/dados.py de HOY (el de Par 07-17 aún no tenía tiradas de
    combate: {Ataque}/{Iniciativa}).
"""
import random
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import datos            # noqa: E402
import instrumentos_texto as it   # noqa: E402

NUMERICOS = {"qn1_ttr": 3, "qn1_ngram_repeticion": 3, "qn1_legibilidad_fh": 2,
             "cl2_lugar_jaccard_similarity": 3, "cr2_entidad_grafo_densidad": 3}
BOOLEANOS = ["qn2_pj_piensa_narrado", "cl2_pnj_inactivo_actua", "cr1_veredicto_contradice_narracion",
             "cl2_pc_hp_contradice_narracion", "qn2_pj_accion_revisar"]
RAW_FLAGS = ["meta_comentario", "comenta_reglas"]


def coincide(nuevo, guardado, decimales):
    """Compara dos valores redondeados a `decimales` (columna numeric); coinciden dos None."""
    if nuevo is None or guardado is None:
        return nuevo is None and guardado is None
    return round(float(nuevo), decimales) == round(float(guardado), decimales)


def comparar_turno(dc, t, fila):
    """Recalcula un turno y lo compara con su fila de turn_validation."""
    texto, ctx = dc.texto(t), dc.contexto(t)
    calc = it.calcular(texto, ctx, nombres=set(NUMERICOS) | set(BOOLEANOS) | set(RAW_FLAGS)
                       | {"cr2_nombres_no_reconocidos"})
    base = {"campaign_id": dc.campaign_id, "brazo": dc.brazo, "par": dc.par, "turn": t}
    out = []
    for col, dec in NUMERICOS.items():
        out.append(dict(base, columna=col, recalculado=calc[col], guardado=fila[col],
                        ok=coincide(calc[col], fila[col], dec)))
    for col in BOOLEANOS:
        out.append(dict(base, columna=col, recalculado=bool(calc[col]), guardado=bool(fila[col]),
                        ok=bool(calc[col]) == bool(fila[col])))
    nombres = it.nombres_no_reconocidos(texto, ctx)
    out.append(dict(base, columna="cr2_nombres_no_reconocidos", recalculado=nombres,
                    guardado=list(fila["cr2_nombres_no_reconocidos"] or []),
                    ok=nombres == list(fila["cr2_nombres_no_reconocidos"] or [])))
    raw = fila["raw_flags"] or {}
    for col in RAW_FLAGS:
        out.append(dict(base, columna=col, recalculado=bool(calc[col]), guardado=bool(raw.get(col)),
                        ok=bool(calc[col]) == bool(raw.get(col))))
    return out


def resumir(filas):
    """Cuenta por columna las comparaciones que coinciden y las discrepancias."""
    r = {}
    for f in filas:
        x = r.setdefault(f["columna"], {"n": 0, "ok": 0, "discrepancias": 0})
        x["n"] += 1
        x["ok" if f["ok"] else "discrepancias"] += 1
    return r


def turnos_positivos(conn, campaign_id, rng, por_bandera=3):
    """Turnos con marca positiva guardada (para que los booleanos se comprueben donde disparan)."""
    banderas = BOOLEANOS + ["cr2_nombres_no_reconocidos"]
    ids = set()
    for col in BOOLEANOS:
        rs = [r["turn_id"] for r in conn.execute(
            f"SELECT turn_id FROM turn_validation WHERE campaign_id=%s AND {col} AND turn_id > 1 ORDER BY turn_id",
            (campaign_id,)).fetchall()]
        ids.update(rng.sample(rs, min(por_bandera, len(rs))))
    rs = [r["turn_id"] for r in conn.execute(
        "SELECT turn_id FROM turn_validation WHERE campaign_id=%s AND turn_id > 1 AND raw_flags ?| %s "
        "ORDER BY turn_id", (campaign_id, RAW_FLAGS)).fetchall()]
    ids.update(rng.sample(rs, min(por_bandera, len(rs))))
    return sorted(ids)


def control_de_mutacion(conn, datos_por_campana, turnos):
    """Control de la propia prueba: rompe el contexto a propósito y comprueba que la
    comparación lo NOTA (si siguiera coincidiendo, la prueba de fidelidad sería trivial).
    turnos: [(campaign_id, turn)]."""
    res = {"escena_erronea": {"n": 0, "discrepancias": 0}, "sin_pnj_en_gazetteer": {"n": 0, "discrepancias": 0}}
    for cid, t in turnos:
        dc = datos_por_campana[cid] if cid in datos_por_campana else next(iter(datos_por_campana.values()))
        fila = datos.guardado_en_turn_validation(conn, cid, [t]).get(t)
        if fila is None:
            continue
        ctx = dc.contexto(t)
        v = it.calcular(dc.texto(t), ctx.copia(escena_anterior=dc.texto(t - 2)),
                        nombres=["cl2_lugar_jaccard_similarity"])["cl2_lugar_jaccard_similarity"]
        res["escena_erronea"]["n"] += 1
        res["escena_erronea"]["discrepancias"] += not coincide(v, fila["cl2_lugar_jaccard_similarity"], 3)
        v = it.calcular(dc.texto(t), ctx.copia(entidades=[e for e in ctx.entidades if e["tipo"] != "npc"]),
                        nombres=["cr2_entidad_grafo_densidad"])["cr2_entidad_grafo_densidad"]
        res["sin_pnj_en_gazetteer"]["n"] += 1
        res["sin_pnj_en_gazetteer"]["discrepancias"] += not coincide(v, fila["cr2_entidad_grafo_densidad"], 3)
    return res


def correr(conn, plan, datos_por_campana, semilla=20260920, por_bandera=3):
    """Compara la muestra aleatoria del plan (estrato 'muestra') y turnos con marca positiva
    (estrato 'positivos'). datos_por_campana: {campaign_id: DatosCampana}."""
    rng = random.Random(f"{semilla}|fidelidad")
    filas = []
    por_camp = {}
    for t in plan["turnos"]:
        por_camp.setdefault(t["campaign_id"], set()).add(t["turn"])
    for cid, dc in datos_por_campana.items():
        muestra = sorted(por_camp.get(cid, ()))
        positivos = [t for t in turnos_positivos(conn, cid, rng, por_bandera) if t not in muestra]
        guardadas = datos.guardado_en_turn_validation(conn, cid, muestra + positivos)
        for estrato, ids in (("muestra", muestra), ("positivos", positivos)):
            for t in ids:
                if t not in guardadas:
                    continue
                for f in comparar_turno(dc, t, guardadas[t]):
                    f["estrato"] = estrato
                    filas.append(f)
    muestra_mut = [(t["campaign_id"], t["turn"]) for t in plan["turnos"]][::5]
    return {"filas": filas,
            "mutaciones": control_de_mutacion(conn, datos_por_campana, muestra_mut),
            "resumen": {e: resumir([f for f in filas if f["estrato"] == e])
                        for e in ("muestra", "positivos")},
            "n_turnos": {e: len({(f["campaign_id"], f["turn"]) for f in filas if f["estrato"] == e})
                         for e in ("muestra", "positivos")}}
