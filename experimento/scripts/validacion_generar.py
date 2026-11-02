#!/usr/bin/env python3
"""
Validación humana, paso 1: muestreo estratificado + material CIEGO + formulario de evaluación.

Unidad = (par, ventana de K turnos consecutivos): dos textos, A y B, con el mismo par (mismo lore y
mismo PJ) y el mismo tramo de turnos, uno de G1 y otro de G2, con el orden al azar. El evaluador califica
cada texto de 1 a 5 en las 6 subdimensiones de la rúbrica (docs/planificacion/plan_validacion.md) y adivina cuál es el
multiagente (comprobación del ciego).

Ciego: G1 escribe con etiquetas «narrativa/mecanica/presion» y una línea de tirada («Percepción: Éxito…»)
en ~100 % de los turnos y G2 nunca, lo que delataría la arquitectura. Se quitan las etiquetas y el bloque
«mecanica» en G1; el resto (narrativa + presión) se muestra como prosa. Se excluyen las ventanas con
JSON crudo, meta-comentario `[..]` o alfabetos no latinos (delatarían o confundirían).

Salidas en datos/validacion/:  clave_secreta.json (NO abrir los evaluadores), unidades.json (ciego),
evaluador_<id>_piloto.html y evaluador_<id>_principal.html (autónomos; guardan en el navegador y exportan CSV).

Uso: python experimento/scripts/validacion_generar.py [--k 8] [--n-por-posicion 8] [--piloto 4] [--seed 20260920]
                                          [--evaluadores E1,E2]
"""
import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "motor" / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
POSICIONES = {"temprano": (20, 180), "medio": (600, 780), "tardio": (1200, 1380)}
ETIQ = re.compile(r"^(narrativa|mecanica|presion)\s*$", re.M)
SUCIO = re.compile(r'^\s*[\{\[]|[぀-ヿ一-鿿가-힯Ѐ-ӿ]')
DIMS = [("CR1", "Fluidez y sentido lógico de la respuesta",
         "¿La respuesta del DM tiene sentido como reacción inmediata a lo que hizo el jugador, es fluida y no se contradice dentro del propio turno?",
         "1 incoherente / no responde a la acción · 3 responde pero con fallos de lógica o de fluidez · 5 natural, lógica y fluida"),
        ("CR2", "Arraigo contextual",
         "¿La narración se apoya en el escenario, los personajes y los hechos ya establecidos (lore y turnos previos) en lugar de inventar cosas ajenas?",
         "1 ajena al escenario · 3 mezcla lo establecido con invenciones sin relación · 5 plenamente anclada al escenario y a lo ocurrido"),
        ("CL1", "Consistencia de personajes",
         "¿Los PNJ (y el PJ) hablan y actúan de forma consistente con su personalidad, motivaciones y con lo que ya hicieron?",
         "1 actúan contra su carácter o cambian sin motivo · 3 consistentes a ratos · 5 plenamente consistentes"),
        ("CL2", "Consistencia de eventos y estado del mundo",
         "¿Lugares, objetos, heridas, quién está presente y lo que ya pasó se mantienen sin contradicciones?",
         "1 contradicciones claras · 3 alguna inconsistencia menor · 5 el estado del mundo se mantiene coherente"),
        ("QN1", "Interés, creatividad y atractivo",
         "¿Es interesante, con detalles originales y sin repetirse? ¿Dan ganas de seguir leyendo?",
         "1 monótono/genérico o repetitivo · 3 correcto pero previsible · 5 vívido, original y atractivo"),
        ("QN2", "Reactividad significativa a la agencia del jugador",
         "¿Lo que hace el jugador cambia algo perceptible y proporcionado en la ficción, o el mundo lo ignora?",
         "1 el mundo ignora sus acciones · 3 reacciona de forma superficial · 5 sus decisiones tienen consecuencias claras y proporcionadas")]


def prosa(dm, brazo):
    """Texto que ve el evaluador: idéntico formato en los dos brazos."""
    dm = (dm or "").strip()
    if brazo != "G1":
        return dm
    partes = ETIQ.split(dm)
    if len(partes) == 1:
        return dm
    tramos = [t.strip() for e, t in zip(partes[1::2], partes[2::2]) if e != "mecanica"]
    return "\n\n".join(t for t in tramos if t)


def jugador(buf):
    """Texto de la acción del jugador a partir de su buffer de entradas."""
    return "\n".join((x.get("text", "") if isinstance(x, dict) else str(x)) for x in (buf or [])).strip()


def ventana(conn, cid_g1, cid_g2, t0, k):
    """Ventana de k turnos pareados G1/G2 desde t0, con el turno previo como contexto; None si falta algún turno o hay marcas de corrida sucia (SUCIO)."""
    filas = {}
    for brazo, cid in (("G1", cid_g1), ("G2", cid_g2)):
        rs = conn.execute("SELECT turn_id, player_buffer, dm_output FROM turn_log WHERE campaign_id=%s "
                          "AND turn_id BETWEEN %s AND %s ORDER BY turn_id", (cid, t0 - 1, t0 + k - 1)).fetchall()
        if len(rs) != k + 1 or any(SUCIO.search(r["dm_output"] or "") or SUCIO.search(jugador(r["player_buffer"])) for r in rs):
            return None
        filas[brazo] = {"previo": prosa(rs[0]["dm_output"], brazo),
                        "turnos": [{"jugador": jugador(r["player_buffer"]), "dm": prosa(r["dm_output"], brazo)} for r in rs[1:]]}
    return filas


def main():
    """Genera el material de la validación humana pareada: sortea ventanas de k turnos por posición y tono (semilla fija), con una parte piloto, clave aparte y un formulario por evaluador."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--n-por-posicion", type=int, default=8)
    ap.add_argument("--piloto", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260920)
    ap.add_argument("--evaluadores", default="E1,E2")
    args = ap.parse_args()
    rnd = random.Random(args.seed)

    pares = []
    for f in ("docs/ids_par07-17.json", "docs/ids_par18-27.json"):
        for e in json.loads((RAIZ / f).read_text(encoding="utf-8")):
            pares.append(dict(e, lote="v1" if f.endswith("07-17.json") else "v2"))
    por_tono = {}
    for p in pares:
        por_tono.setdefault(p["tono"], []).append(p)

    salida = RAIZ / "datos" / "validacion"
    salida.mkdir(exist_ok=True)
    pares_pos, ventanas, unidades, clave = set(), [], [], {}   # (par,pos,piloto) usados · (par,t0) usados
    with psycopg.connect(db.DSN, row_factory=dict_row) as conn:
        def sortear(pos, tono, piloto):
            """Sortea un par y una ventana válidos para una posición y un tono, sin repetir (par, posición, piloto) ni solapar ventanas del mismo par; aborta si no puede."""
            lo, hi = POSICIONES[pos]
            cand = por_tono[tono][:]
            rnd.shuffle(cand)
            for p in cand:
                if (p["par"], pos, piloto) in pares_pos:
                    continue
                for _ in range(60):
                    t0 = rnd.randint(lo, hi)
                    if any(pp == p["par"] and abs(t0 - u) < args.k for pp, u in ventanas):
                        continue            # ventanas de un mismo par que se solapan
                    w = ventana(conn, p["campaign_g1"], p["campaign_g2"], t0, args.k)
                    if w:
                        pares_pos.add((p["par"], pos, piloto)); ventanas.append((p["par"], t0))
                        return p, t0, w
            raise SystemExit(f"no se pudo sortear ({pos}, {tono})")

        planes = [("medio", t, True) for t in list(por_tono)[:args.piloto]]
        planes += [(pos, t, False) for pos in POSICIONES for t in por_tono for _ in range(args.n_por_posicion // len(por_tono))]
        lore = {}
        lados = ["G1", "G2"] * ((len(planes) + 1) // 2)   # mitad y mitad, en orden al azar
        rnd.shuffle(lados)
        for pos, tono, piloto in planes:
            p, t0, w = sortear(pos, tono, piloto)
            if p["par"] not in lore:
                lore[p["par"]] = conn.execute("SELECT dm_output FROM turn_log WHERE campaign_id=%s AND turn_id=0",
                                              (p["campaign_g2"],)).fetchone()["dm_output"]
            lado_a = lados.pop()
            uid = "u" + hashlib.sha1(f"{args.seed}|{p['par']}|{t0}".encode()).hexdigest()[:6]
            unidades.append({"id": uid, "piloto": piloto, "lore": lore[p["par"]],
                             "A": w[lado_a], "B": w["G2" if lado_a == "G1" else "G1"]})
            clave[uid] = {"par": p["par"], "lugar": p["lugar"], "tono": p["tono"], "registro": p.get("registro", "mixed"),
                          "lote": p["lote"], "posicion": pos, "t0": t0, "k": args.k, "lado_A": lado_a,
                          "piloto": piloto, "campaign_g1": p["campaign_g1"], "campaign_g2": p["campaign_g2"]}

    (salida / "clave_secreta.json").write_text(json.dumps(clave, indent=1, ensure_ascii=False), encoding="utf-8")
    (salida / "unidades.json").write_text(json.dumps(unidades, ensure_ascii=False), encoding="utf-8")
    plantilla = (RAIZ / "experimento" / "scripts" / "validacion_formulario.html").read_text(encoding="utf-8")
    for ev in args.evaluadores.split(","):
        for fase, es_piloto in (("piloto", True), ("principal", False)):
            us = [u for u in unidades if u["piloto"] == es_piloto]
            random.Random(f"{args.seed}|{ev}|{fase}").shuffle(us)
            datos = json.dumps({"evaluador": ev, "fase": fase, "dims": DIMS, "unidades": us}, ensure_ascii=False).replace("</", "<\\/")
            (salida / f"evaluador_{ev}_{fase}.html").write_text(plantilla.replace("__DATOS__", datos), encoding="utf-8")

    print(f"{len(unidades)} unidades ({args.piloto} de piloto), ventana de {args.k} turnos, semilla {args.seed}")
    for pos in POSICIONES:
        c = [v for v in clave.values() if v["posicion"] == pos and not v["piloto"]]
        print(f"  {pos:9}: {len(c)} · tonos {sorted(v['tono'] for v in c)} · lote v1={sum(v['lote']=='v1' for v in c)} v2={sum(v['lote']=='v2' for v in c)}")
    print("  pares distintos en la muestra principal:", len({v['par'] for v in clave.values() if not v['piloto']}))
    print("  lado A = G1 en", sum(v["lado_A"] == "G1" for v in clave.values()), "de", len(clave))


if __name__ == "__main__":
    main()
