#!/usr/bin/env python3
"""
A2 con el detector CONGELADO scripts/instrumentos/persona2.py (v2b): equivalencia por persona gramatical.

Pregunta: ¿persona2 detecta la misma usurpación cuando el DM la escribe en 2.ª persona, que es lo que hace G2
(los detectores viejos solo la ven en 3.ª persona con el nombre del PJ)? Se inyecta un defecto conocido en turnos
reales (misma muestra que la línea base: semilla 20260920, 150 turnos por brazo) y se mira si aparece un hallazgo NUEVO.

EXPECTATIVAS (escritas antes de correr; se imprime y guarda su SHA-256; no se editan tras ver resultados):
  DIR  (recall de la inyección; aprobado si el límite inferior de Wilson al 95 % >= 0.80, por brazo):
       2.ª persona: decision -> VOLICION · pensamiento -> COGNICION · emocion -> EMOCION · habla -> HABLA
       3.ª persona con el nombre del PJ (control positivo): las mismas cuatro categorías
       muerte del PJ con HP>0, narra_muerte_pj: 2.ª persona y 3.ª persona
  EXP  (exploratorias, sin veredicto): accion_no_declarada en 2.ª persona (depende de la regla de «declarada»);
       paráfrasis fuera del léxico (mide cobertura léxica, se espera recall menor que en DIR)
  INV  (falsa alarma sobre lo que NO viola la regla; aprobado si la tasa observada <= 5 % y el límite superior <= 10 %):
       percepción sensorial · consecuencia mecánica involuntaria · pregunta u opciones al jugador ·
       «tú» dentro de las palabras de un PNJ
Un hallazgo cuenta como NUEVO si (categoría, lema, frase) no estaba en el turno antes de la inyección.

Uso: PYTHONUTF8=1 py scripts/sensibilidad/correr_persona2.py [--n-por-par 15] [--semilla 20260920]
Salida: docs/reportes/persona2_equivalencia.md
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from math import sqrt
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for p in (AQUI, RAIZ / "scripts" / "instrumentos", RAIZ / "scripts", RAIZ / "orquestador"):
    sys.path.insert(0, str(p))
import datos  # noqa: E402
import perturbaciones as pt  # noqa: E402
import persona2 as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
Z = 1.959964
PRIM = {"decision": "VOLICION", "pensamiento": "COGNICION", "emocion": "EMOCION", "habla": "HABLA"}

EXPECTATIVAS = {
    "DIR": {"criterio": "limite_inferior_wilson>=0.80", "celdas": [f"{p}_{k}" for p in ("2p", "3p") for k in PRIM] + ["muerte_2p", "muerte_3p"]},
    "EXP": {"criterio": "sin veredicto", "celdas": ["accion_2p", "parafrasis_2p"]},
    "INV": {"criterio": "tasa<=0.05 y limite_superior_wilson<=0.10", "celdas": ["percepcion", "consecuencia", "pregunta", "pnj_habla_tu"]},
}
HASH = hashlib.sha256(json.dumps(EXPECTATIVAS, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

INV = {
    "percepcion": ["Ves una sombra que se mueve al fondo del pasillo.", "Sientes el frío del metal bajo los dedos.",
                   "Oyes un goteo lejano, constante y hueco.", "Notas un olor a humo viejo en el aire.", "Percibes un leve temblor en el suelo."],
    "consecuencia": ["Tropiezas con una raíz y caes al suelo.", "La flecha te alcanza en el hombro y sangras.",
                     "Un golpe seco te deja aturdido un instante.", "El empujón te lanza contra la pared."],
    "pregunta": ["¿Qué haces?", "Puedes entrar por la puerta o esperar a que pase la ronda.", "¿Cómo quieres proceder?"],
    "pnj_habla_tu": ["—Tú no eres de aquí —dice el guardia, mirándote de arriba abajo.", "«Tú decides», murmura el anciano, «pero decide pronto»."],
}
PARAFRASIS = {  # fuera del léxico probable: mide cobertura, no equivalencia
    "VOLICION": ["Te determinas a seguir el rastro.", "Te decantas por la puerta lateral.", "Te resuelves a huir por la ventana."],
    "COGNICION": ["Barruntas que es una trampa.", "Te convences de que miente.", "Cavilas sobre lo que acaba de decir.", "Intuyes que algo no encaja."],
    "EMOCION": ["Te embarga una tristeza honda.", "Un pánico frío te recorre la espalda y te paraliza.", "Te sobreviene una rabia sorda."],
    "HABLA": ["Contestas con voz ronca que no piensas irte.", "Replicas con desdén.", "Le espetas que se equivoca."],
}


def wilson(x, n):
    if not n:
        return (None, None)
    p = x / n; d = 1 + Z * Z / n; c = (p + Z * Z / (2 * n)) / d; h = Z * sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def hallazgos(texto, accion, nombre_pj=None):
    return Counter((h["categoria"], h["verbo_lema"], h["evidencia"][:60]) for h in P.detectar_usurpacion(texto, accion, None, nombre_pj=nombre_pj))


def nuevos(antes, despues):
    return list((despues - antes).elements())


def pct(x):
    return "—" if x is None else f"{100 * x:.1f} %"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=20260920)
    ap.add_argument("--n-por-par", type=int, default=15)
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "reportes" / "persona2_equivalencia.md"))
    a = ap.parse_args()
    print(f"SHA-256 de las expectativas: {HASH}")
    conn = datos.abrir_conexion()
    plan = datos.plan_muestra(datos.cargar_pares(), a.semilla, 10, a.n_por_par, 1)
    dc = {}
    for par in plan["pares"]:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            dc[par[k]] = datos.DatosCampana(conn, par[k], brazo, par["par"])
    res = {}   # (celda, brazo) -> [k, n]
    base_falsa = {}   # brazo -> [turnos con hallazgo primario natural, n]
    diag = {}         # (celda 2p, plantilla) -> [n, con la categoría esperada, con cualquier hallazgo primario nuevo]

    def anota(celda, brazo, ok):
        r = res.setdefault((celda, brazo), [0, 0]); r[0] += bool(ok); r[1] += 1

    for brazo in ("G1", "G2"):
        for t in [x for x in plan["turnos"] if x["brazo"] == brazo]:
            d = dc[t["campaign_id"]]; texto = d.texto(t["turn"]); ctx = d.contexto(t["turn"]); acc = d.accion(t["turn"])
            nom = ctx.pj_nombre
            antes2 = hallazgos(texto, acc); antes3 = hallazgos(texto, acc, nom)
            b = base_falsa.setdefault(brazo, [0, 0]); b[1] += 1
            b[0] += any(k[0] in PRIM.values() for k in antes2)
            rng = lambda *s: random.Random(f"{a.semilla}|{'|'.join(map(str, s))}|{t['campaign_id']}|{t['turn']}")
            for cat_k, cat in PRIM.items():                     # DIR 2.ª y 3.ª persona con las plantillas del arnés
                # en el arnés P1_* = usurpación en 2.ª persona y P2_* = 3.ª persona con el nombre del PJ
                for p, pid, antes, nombre in (("2p", f"P1_{cat_k}", antes2, None), ("3p", f"P2_{cat_k}", antes3, nom)):
                    if not pt.elegible(pid, texto, ctx):
                        continue
                    r = pt.perturbar(pid, texto, ctx, rng(pid))
                    nue = nuevos(antes, hallazgos(r.texto, acc, nombre))
                    anota(f"{p}_{cat_k}", brazo, any(k[0] == cat for k in nue))
                    if p == "2p":
                        d_ = diag.setdefault((cat_k, r.info["insertado"][:60]), [0, 0, 0])
                        d_[0] += 1; d_[1] += any(k[0] == cat for k in nue); d_[2] += any(k[0] in PRIM.values() for k in nue)
            if pt.elegible("P1_accion_sin_tirada", texto, ctx):   # P1_accion exige turno sin tirada: 149/150 la llevan y dio 0/0
                r = pt.perturbar("P1_accion_sin_tirada", texto, ctx, rng("acc2"))
                anota("accion_2p", brazo, any(k[0] == "ACCION_NO_DECLARADA" for k in nuevos(antes2, hallazgos(r.texto, acc))))
            for p, pid in (("2p", "P4_2p"), ("3p", "P4_3p")):    # muerte del PJ con HP>0
                if pt.elegible(pid, texto, ctx):
                    r = pt.perturbar(pid, texto, ctx, rng(pid))
                    anota(f"muerte_{p}", brazo, P.narra_muerte_pj(r.texto, None, nombre_pj=nom if p == "3p" else None))
            for celda, frases in INV.items():                     # INV: NO deben producir hallazgo nuevo
                f = rng(celda).choice(frases)
                anota(celda, brazo, nuevos(antes2, hallazgos(texto + "\n\n" + f, acc)) != [])
            cat = rng("par").choice(sorted(PARAFRASIS)); f = rng("par2").choice(PARAFRASIS[cat])   # EXP: cobertura léxica
            anota("parafrasis_2p", brazo, any(k[0] == cat for k in nuevos(antes2, hallazgos(texto + "\n\n" + f, acc))))

    L = ["# persona2 (congelado) en el arnés A2: equivalencia por persona gramatical", "",
         f"Muestra: semilla {a.semilla}, ≈{10 * a.n_por_par} turnos por brazo (pares de ambos lotes). SHA-256 de las expectativas (fijadas antes de correr): `{HASH}`.",
         "Un hallazgo cuenta como nuevo si (categoría, lema, frase) no estaba antes de la inyección. Detector: `scripts/instrumentos/persona2.py` v2b, sin modificar.", "",
         "## DIR: la misma usurpación en 2.ª y en 3.ª persona (aprobado si el límite inferior de Wilson ≥ 0.80)", "",
         "| celda | G1 | G2 | veredicto |", "|---|---|---|---|"]
    def fila(celda, tipo):
        c = []; ok = True
        for b in ("G1", "G2"):
            k, n = res.get((celda, b), [0, 0]); lo, hi = wilson(k, n)
            c.append(f"{k}/{n} = {pct(k / n if n else None)} [{pct(lo)}–{pct(hi)}]")
            if tipo == "DIR": ok &= bool(n) and lo is not None and lo >= 0.80
            if tipo == "INV": ok &= (not n) or (k / n <= 0.05 and hi <= 0.10)
        return f"| {celda} | {c[0]} | {c[1]} | {'' if tipo == 'EXP' else ('**aprobada**' if ok else '**NO aprobada**')} |"
    for celda in EXPECTATIVAS["DIR"]["celdas"]:
        L.append(fila(celda, "DIR"))
    L += ["", "## INV: lo que NO viola la regla no debe marcarse (aprobado si tasa ≤ 5 % y límite superior ≤ 10 %)", "", "| celda | G1 | G2 | veredicto |", "|---|---|---|---|"]
    for celda in EXPECTATIVAS["INV"]["celdas"]:
        L.append(fila(celda, "INV"))
    L += ["", "## EXP (exploratorio, sin veredicto)", "", "| celda | G1 | G2 | |", "|---|---|---|---|"]
    for celda in EXPECTATIVAS["EXP"]["celdas"]:
        L.append(fila(celda, "EXP"))
    L += ["", "## Diagnóstico posterior por plantilla, 2.ª persona (no altera los veredictos; ambos brazos juntos)", "",
          "| celda | plantilla | n | categoría esperada | cualquier hallazgo primario |", "|---|---|---|---|---|"]
    for (c_, pl), (n_, k1, k2) in sorted(diag.items()):
        L.append(f"| {c_} | {pl} | {n_} | {k1}/{n_} | {k2}/{n_} |")
    L += ["", "## Tasa natural de hallazgos primarios en los mismos turnos, sin inyectar", ""]
    for b in ("G1", "G2"):
        k, n = base_falsa[b]; lo, hi = wilson(k, n)
        L.append(f"- {b}: {k}/{n} = {pct(k / n)} [{pct(lo)}–{pct(hi)}]")
    L.append("")
    Path(a.salida).write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
