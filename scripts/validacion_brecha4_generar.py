#!/usr/bin/env python3
"""
Validación humana, brecha 4 (OE-5/H1e, ver claude/evaluacion-kev-y-brechas-pendientes-
intervencion-humana-2026-09-23.md, Brecha 4): ¿la narración trata a un PNJ que ya dejó de
estar activo (missing/dead/captured) como si siguiera presente/actuando, lo referencia
correctamente en retrospectiva, o simplemente no lo vuelve a mencionar?

Constructo FACTUAL (el hecho de estado ya está resuelto por Postgres -- el evaluador no
opina sobre calidad ni creatividad, solo confirma si la narración es consistente con un
hecho dado). Por eso basta con 2-4 evaluadores externos y kappa sobre una muestra chica --
no un panel de 5 DMs sobre el corpus completo (precedente: Chen, Wang, Yu & Zhang 2023,
AAAI, Fleiss' Kappa=0.671, 4 evaluadores, escala 1-3, consistencia de persona -- ya en la
bibliografía del proyecto).

Los 3 candidatos que esta muestra valida A LA VEZ (mismo formulario, mismos casos, una sola
convocatoria -- nunca se le muestra al evaluador el veredicto de ninguno, para no anclar su
juicio, mismo principio que scripts/etiquetado_persona2.py):
  - Jericho recall (jericho_qa_recall(), orquestador/reporte_validacion.py) -- léxico.
  - cl2_pnj_inactivo_actua refinado (pnj_inactivo_refinado(), misma sección 9 del archivo
    de arriba) -- sintáctico (spaCy, sujeto gramatical).
  - Kev con prompt de glosario (fuera de este script -- se corre aparte sobre los mismos
    casos exportados en brecha4_clave.csv).

Dos estratos de casos, TODOS reutilizando funciones reales, nunca reimplementadas:
  - 'flagged': turnos con cl2_pnj_inactivo_actua=true en turn_validation (columna en vivo,
    calculada durante la generación con el estado histórico correcto en ese momento exacto --
    algo que este script post-hoc no podría reconstruir con la misma fidelidad). Se
    sub-estratifican con pnj_inactivo_refinado() en 'actuando' (sujeto gramatical -- el
    refinamiento dice "sí es error") vs 'solo_referenciado' (el refinamiento dice "no es
    error, es retrospectivo") SOLO para armar una muestra balanceada entre las dos clases --
    esa etiqueta nunca llega al evaluador.
  - 'silencio': deltas de npc.status con vocabulario distintivo (dead/missing/captured, ver
    _KEYWORDS_NPC_STATUS) donde jericho_qa_recall() no reconoció nada en la ventana inmediata
    Y el PNJ tampoco aparece después en ningún turno cl2_pnj_inactivo_actua=true de esa
    campaña -- casos "control" (el PNJ simplemente no se vuelve a mencionar), mismo papel que
    los 4 controles del piloto manual de Kev (2026-09-23).

Salidas en validacion/:
  brecha4_clave.csv    NO abrir -- clasificación real de los 3 candidatos por caso, para
                        precisión/recall/kappa después.
  brecha4_casos.json   ciego -- lo que ve el formulario.
  validacion_brecha4_<evaluador>.html  x N  -- autónomos, autoguardan en localStorage,
                        exportan CSV (evaluador,id_caso,veredicto,nota,segundos).

Uso: python scripts/validacion_brecha4_generar.py [--n-flagged 40] [--n-silencio 20]
                                                    [--seed 20260924] [--evaluadores E1,E2,E3]

Requiere (igual que validacion_generar.py / etiquetado_persona2.py): psycopg, y spaCy +
es_core_news_sm para el sub-estrato 'actuando'/'solo_referenciado' -- si spaCy no está
instalado, el script sigue funcionando pero solo con muestreo aleatorio dentro de 'flagged'
(se avisa por consola).
"""
import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ / "scripts" / "reporte_v2"))
import db  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402
from validacion_generar import prosa, jugador  # noqa: E402
from reporte_validacion import (  # noqa: E402
    jericho_qa_recall, pnj_inactivo_refinado, _KEYWORDS_NPC_STATUS, _modelo_grafo,
)
import pares as _pares  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_GLOSA_ESTADO = {
    "dead": "falleció / fue dado por muerto",
    "missing": "desapareció / su paradero es desconocido",
    "captured": "fue capturado / está preso",
}


def _turn_log_ventana(conn, campaign_id, t0, t1):
    """turn_id, player_buffer, dm_output para [t0, t1] de una campaña -- misma tabla y
    columnas que usan validacion_generar.py/etiquetado_persona2.py, consulta directa (no hay
    método de Campaña para un rango arbitrario de turnos con player_buffer incluido)."""
    filas = conn.execute(
        "SELECT turn_id, player_buffer, dm_output FROM turn_log "
        "WHERE campaign_id=%s AND turn_id BETWEEN %s AND %s ORDER BY turn_id",
        (campaign_id, max(0, t0), t1)).fetchall()
    return {f["turn_id"]: f for f in filas}


def _fragmento(conn, campaign_id, brazo, turnos_ids):
    filas = _turn_log_ventana(conn, campaign_id, min(turnos_ids), max(turnos_ids))
    frag = []
    for t in turnos_ids:
        f = filas.get(t)
        if not f:
            continue
        frag.append({"turno": t, "jugador": jugador(f["player_buffer"]),
                     "dm": prosa(f["dm_output"], brazo)})
    return frag


def _ultimo_estado_antes(deltas_npc_status, nombre, turno_limite):
    """Última transición de npc.status con vocabulario distintivo para `nombre` en o antes de
    `turno_limite` -- el "hecho ya resuelto por Postgres" que se le muestra al evaluador."""
    candidatos = [d for d in deltas_npc_status
                  if d["entity_name"] == nombre and d["turn_id"] <= turno_limite]
    if not candidatos:
        return None
    return max(candidatos, key=lambda d: d["turn_id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-flagged", type=int, default=40)
    ap.add_argument("--n-silencio", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument("--evaluadores", default="E1,E2,E3")
    args = ap.parse_args()
    rnd = random.Random(args.seed)

    pares = _pares.todos()
    salida = RAIZ / "validacion"
    salida.mkdir(exist_ok=True)

    pool_actuando, pool_solo_ref, pool_flagged_sin_spacy, pool_silencio = [], [], [], []
    # Detectado UNA vez, de forma directa (mismo modelo cacheado que pnj_inactivo_refinado()
    # usa internamente) -- nunca inferido de si una campaña concreta tenía o no turnos
    # 'flagged' para refinar (bug real, visto en corrida 2026-09-24: la primera campaña sin
    # flagged hacía que refinado=None se leyera como "spaCy no instalado" para TODA la
    # corrida, aunque spaCy sí funcionaba en campañas posteriores).
    spacy_disponible = _modelo_grafo() is not None

    with psycopg.connect(db.DSN, row_factory=dict_row) as conn:
        for p in pares:
            for brazo, cid in (("G1", p["campaign_g1"]), ("G2", p["campaign_g2"])):
                camp = db.Campaña(cid)
                entidades = camp.entidades()
                turnos = camp.turnos_narracion()
                turnos_por_id = {t["turn_id"]: t["dm_output"] for t in turnos}
                deltas = camp.deltas_narrables()
                deltas_npc_status = [d for d in deltas if d["entity_type"] == "npc"
                                     and d["field_name"] == "status"
                                     and str(d["new_value"]).strip('"').lower()
                                     in _KEYWORDS_NPC_STATUS]

                filas_validacion = conn.execute(
                    "SELECT * FROM turn_validation WHERE campaign_id=%s ORDER BY turn_id",
                    (cid,)).fetchall()
                flagged = [f for f in filas_validacion if f.get("cl2_pnj_inactivo_actua")]

                refinado = None
                if flagged and spacy_disponible:
                    refinado = pnj_inactivo_refinado(filas_validacion, turnos_por_id, entidades)

                def _empaquetar(entrada, categoria):
                    turno = entrada["turno"]
                    nombre = entrada["pnj"]
                    d0 = _ultimo_estado_antes(deltas_npc_status, nombre, turno)
                    if d0 is None:
                        return None  # no se pudo resolver el hecho -- se descarta, no se adivina
                    estado = str(d0["new_value"]).strip('"').lower()
                    ids = [t for t in (turno - 1, turno) if t in turnos_por_id]
                    if not ids:
                        return None
                    return {
                        "id": f"f{cid}_{turno}_{nombre[:12]}".replace(" ", ""),
                        "estrato": categoria, "par": p["par"], "brazo": brazo,
                        "campaign_id": cid, "turno_evaluado": turno,
                        "pnj": nombre, "estado": estado,
                        "estado_desde_turno": d0["turn_id"],
                        "estado_glosa": _GLOSA_ESTADO[estado],
                        "fragmento": _fragmento(conn, cid, brazo, ids),
                    }

                if refinado:
                    for e in refinado["actuando"]:
                        c = _empaquetar(e, "actuando"); pool_actuando.append(c) if c else None
                    for e in refinado["solo_referenciado"]:
                        c = _empaquetar(e, "solo_referenciado"); pool_solo_ref.append(c) if c else None
                else:
                    for f in flagged:
                        # sin spaCy: no hay pnj/oracion resueltos por pnj_inactivo_refinado(),
                        # así que se arma el caso directo desde el propio turno flageado --
                        # el nombre del PNJ se resuelve buscando qué entidad inactiva aparece
                        # literalmente en el texto de ese turno.
                        texto = (turnos_por_id.get(f["turn_id"]) or "")
                        candidatos_nombre = {d["entity_name"] for d in deltas_npc_status
                                             if d["turn_id"] <= f["turn_id"]
                                             and d["entity_name"] and d["entity_name"] in texto}
                        for nombre in candidatos_nombre:
                            c = _empaquetar({"turno": f["turn_id"], "pnj": nombre},
                                            "flagged_sin_refinar")
                            if c:
                                pool_flagged_sin_spacy.append(c)

                # 'silencio': delta reconocido=False por Jericho Y el pnj nunca aparece en un
                # turno cl2_pnj_inactivo_actua=true posterior de esta misma campaña.
                turnos_flagged_ids = {f["turn_id"] for f in flagged}
                for d in deltas_npc_status:
                    r = jericho_qa_recall([d], turnos_por_id, ventana=1)
                    if r["no_reconocidos"]:
                        nombre = d["entity_name"]
                        aparece_despues = any(
                            t > d["turn_id"] and nombre and nombre in (turnos_por_id.get(t) or "")
                            for t in turnos_flagged_ids)
                        if not aparece_despues:
                            ids = [t for t in (d["turn_id"], d["turn_id"] + 1) if t in turnos_por_id]
                            if not ids:
                                continue
                            estado = str(d["new_value"]).strip('"').lower()
                            pool_silencio.append({
                                "id": f"s{cid}_{d['turn_id']}_{nombre[:12]}".replace(" ", ""),
                                "estrato": "silencio", "par": p["par"], "brazo": brazo,
                                "campaign_id": cid, "turno_evaluado": d["turn_id"],
                                "pnj": nombre, "estado": estado,
                                "estado_desde_turno": d["turn_id"],
                                "estado_glosa": _GLOSA_ESTADO[estado],
                                "fragmento": _fragmento(conn, cid, brazo, ids),
                            })

    print(f"spaCy disponible: {spacy_disponible}")
    print(f"pool actuando={len(pool_actuando)}  solo_referenciado={len(pool_solo_ref)}  "
          f"flagged_sin_refinar={len(pool_flagged_sin_spacy)}  silencio={len(pool_silencio)}")

    def _muestrear(pool, n, max_por_pareja=1):
        """Ronda-robin por (par, pnj): reparte primero 1 caso por pareja distinta (diversidad
        de pares por encima de exhaustividad dentro de un par), y solo si `max_por_pareja` > 1
        y todavía falta para llegar a `n` toma una 2ª/3ª ronda de las mismas parejas -- para
        estratos con pocas parejas distintas (ver 'actuando' más abajo: 361 casos reales mapean
        a solo 7 parejas (par, pnj) distintas en la corrida 2026-09-25 -- un puñado de PNJ con
        el mismo error de continuidad repetido muchas veces, no muchos PNJ con un error cada
        uno -- dato en sí mismo interesante para la auditoría, no un bug del muestreo)."""
        pool = pool[:]
        rnd.shuffle(pool)
        grupos = defaultdict(list)
        for c in pool:
            grupos[(c["par"], c["pnj"])].append(c)
        orden = list(grupos)
        rnd.shuffle(orden)
        elegidos = []
        for ronda in range(max_por_pareja):
            if len(elegidos) >= n:
                break
            for clave in orden:
                if len(elegidos) >= n:
                    break
                g = grupos[clave]
                if ronda < len(g):
                    elegidos.append(g[ronda])
        return elegidos

    if spacy_disponible:
        mitad = args.n_flagged // 2
        # max_por_pareja=4 solo en 'actuando' -- las otras 2 tienen pool de sobra a 1 por
        # pareja (ver conteos impresos arriba); forzar diversidad ahí no haría falta.
        casos = (_muestrear(pool_actuando, mitad, max_por_pareja=4)
                 + _muestrear(pool_solo_ref, args.n_flagged - mitad)
                 + _muestrear(pool_silencio, args.n_silencio))
    else:
        casos = (_muestrear(pool_flagged_sin_spacy, args.n_flagged)
                 + _muestrear(pool_silencio, args.n_silencio))
    rnd.shuffle(casos)

    objetivo = {"actuando": mitad if spacy_disponible else 0,
                "solo_referenciado": (args.n_flagged - mitad) if spacy_disponible else 0,
                "flagged_sin_refinar": 0 if spacy_disponible else args.n_flagged,
                "silencio": args.n_silencio}
    for estrato, n_obj in objetivo.items():
        n_real = sum(c["estrato"] == estrato for c in casos)
        if n_real < n_obj:
            print(f"  ⚠ estrato '{estrato}': solo {n_real} de {n_obj} pedidos -- el pool real "
                  f"tiene menos parejas (par, pnj) distintas de las necesarias para llegar al "
                  f"objetivo incluso con las rondas extra permitidas.")

    # clave privada (no mostrar a los evaluadores) -- para precisión/recall/kappa después.
    with (salida / "brecha4_clave.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "estrato", "par", "brazo", "campaign_id",
                                           "turno_evaluado", "pnj", "estado",
                                           "estado_desde_turno"])
        w.writeheader()
        for c in casos:
            w.writerow({k: c[k] for k in w.fieldnames})

    # material ciego para el formulario -- sin 'estrato' (evita anclar).
    casos_ciegos = [{k: v for k, v in c.items() if k != "estrato"} for c in casos]
    (salida / "brecha4_casos.json").write_text(
        json.dumps(casos_ciegos, ensure_ascii=False, indent=1), encoding="utf-8")

    plantilla = (RAIZ / "scripts" / "validacion_brecha4_formulario.html").read_text(encoding="utf-8")
    for ev in args.evaluadores.split(","):
        cs = casos_ciegos[:]
        random.Random(f"{args.seed}|{ev}|orden").shuffle(cs)
        datos = json.dumps({"evaluador": ev, "casos": cs}, ensure_ascii=False).replace("</", "<\\/")
        (salida / f"validacion_brecha4_{ev}.html").write_text(
            plantilla.replace("__DATOS__", datos), encoding="utf-8")

    print(f"\n{len(casos)} casos totales -> validacion/validacion_brecha4_<evaluador>.html "
          f"({args.evaluadores})")
    print("  por estrato:", {e: sum(c['estrato'] == e for c in casos)
                             for e in ("actuando", "solo_referenciado", "flagged_sin_refinar",
                                       "silencio")})
    print("  pares distintos en la muestra:", len({c["par"] for c in casos}))
    print("  estimado ~1-2 min/caso ->", round(len(casos) * 1.5 / 60, 1), "h por evaluador")


if __name__ == "__main__":
    main()
