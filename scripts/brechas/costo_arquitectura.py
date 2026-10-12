"""
Costo por arquitectura desde las bitácoras (pares 07-27; solo lectura).

¿El MAS «gana porque gasta más»? No se registraron tokens. Lo que sí está en las bitácoras completas,
turno a turno, es la latencia de cada llamada al modelo y la prosa final. De ahí salen:
  - llamadas al modelo por turno (cada valor "N ms" dentro de una sección que llama al modelo);
  - latencia por turno (suma de esos ms), como proxy del cómputo;
  - longitud de la narración final (caracteres de las líneas "> " de DM / NARRADOR; tokens ≈ caracteres/4).
JUGADOR y EXTRACTOR son idénticos en ambos brazos: se reportan aparte («lado DM» los excluye).

Dosis-respuesta: si el cómputo por sí solo explicara la ventaja de G1 en agencia (persona2), dentro de
cada brazo las campañas con más cómputo por turno deberían usurpar menos. Spearman por brazo (27).

    $env:PYTHONUTF8="1"; py scripts/brechas/costo_arquitectura.py
"""
import csv
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

from scipy.stats import spearmanr, wilcoxon

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "docs" / "reportes" / "brechas"
RX_TURNO = re.compile(r"^## Turno (\d+)\b")
RX_SECCION = re.compile(r"^### \[\d+\] (.+)$")
RX_MS = re.compile(r"(\d+) ms\b")
# EXTRACTOR va primero: contiene «ACTOR» y si no se clasificaría como el actor de PNJ.
LLM = {"EXTRACTOR": "extractor", "JUGADOR": "jugador", "DM": "dm", "ACTOR": "actor", "MUNDO": "mundo",
       "NARRADOR": "narrador", "RBITRO": "arbitro"}
PROSA = {"dm", "narrador"}


def rol(titulo):
    t = titulo.upper()
    for clave, r in LLM.items():
        if clave in t:
            return r
    return None


def leer(ruta):
    """{turno: {"ms": {rol: [ms...]}, "chars": n}} — primera aparición de cada turno <= 1400."""
    turnos, actual, r = {}, None, None
    with open(ruta, encoding="utf-8", errors="replace") as f:
        for linea in f:
            m = RX_TURNO.match(linea)
            if m:
                t = int(m.group(1))
                actual = None if (t > 1400 or t in turnos) else turnos.setdefault(t, {"ms": defaultdict(list), "chars": 0})
                r = None
                continue
            if actual is None:
                continue
            s = RX_SECCION.match(linea)
            if s:
                r = rol(s.group(1))
                continue
            if r is None:
                continue
            if r in PROSA and linea.startswith("> "):
                actual["chars"] += len(linea) - 2
            elif not linea.startswith("> "):
                actual["ms"][r].extend(int(x) for x in RX_MS.findall(linea))
    return turnos


def tasa_persona2(par, brazo):
    with open(RAIZ / "datos_v2" / "persona2" / f"par{par}_{brazo}.csv", encoding="utf-8-sig", newline="") as f:
        filas = [r for r in csv.DictReader(f) if int(r["turn_id"]) <= 1400 and int(r["en_desarrollo"] or 0) == 0]
    return 100 * sum(float(r["primaria"] or 0) for r in filas) / len(filas)


def resumen_campana(turnos):
    dm_roles = {"dm", "actor", "mundo", "narrador", "arbitro"}
    filas = list(turnos.values())
    def media(f):
        return st.mean(f(x) for x in filas)
    return {
        "turnos": len(filas),
        "llamadas_ladodm": media(lambda x: sum(len(x["ms"][r]) for r in dm_roles)),
        "llamadas_total": media(lambda x: sum(len(v) for v in x["ms"].values())),
        "seg_dm": media(lambda x: sum(sum(x["ms"][r]) for r in dm_roles) / 1000),
        "seg_total": media(lambda x: sum(sum(v) for v in x["ms"].values()) / 1000),
        "chars_narracion": media(lambda x: x["chars"]),
        **{f"llamadas_{r}": media(lambda x, r=r: len(x["ms"][r])) for r in ("actor", "mundo", "narrador", "dm", "arbitro")},
    }


def main():
    camp = {}
    for ruta in sorted((RAIZ / "logs").rglob("*_bitacora_completa.md")):
        m = re.match(r"par(\d+)_(g[12])_", ruta.name)
        if m:
            camp[(m.group(2).upper(), m.group(1))] = resumen_campana(leer(ruta))
    pares = sorted({p for b, p in camp if ("G1", p) in camp and ("G2", p) in camp})
    claves = ["llamadas_ladodm", "llamadas_total", "seg_dm", "seg_total", "chars_narracion"]
    L = ["# Costo por arquitectura (bitácoras, pares 07–27)", "",
         f"Pares: {len(pares)}. Medias por turno dentro de cada campaña; luego mediana entre campañas. "
         "«Lado DM» excluye jugador y extractor (idénticos en ambos brazos). Tokens de salida ≈ caracteres/4.", "",
         "| Medida por turno | G1 | G2 | Razón G1/G2 | G1>G2 | p |", "|---|---|---|---|---|---|"]
    for k in claves:
        g1 = [camp[("G1", p)][k] for p in pares]
        g2 = [camp[("G2", p)][k] for p in pares]
        d = [a - b for a, b in zip(g1, g2)]
        L.append(f"| {k} | {st.median(g1):.2f} | {st.median(g2):.2f} | {st.median(g1) / st.median(g2):.2f} | "
                 f"{sum(x > 0 for x in d)}/{len(d)} | {wilcoxon(d).pvalue:.2g} |")
    L += ["", "Desglose G1 (llamadas por turno, mediana entre campañas): " + ", ".join(
        f"{r} {st.median(camp[('G1', p)][f'llamadas_{r}'] for p in pares):.2f}" for r in ("actor", "mundo", "narrador", "arbitro")),
          "", "## Dosis-respuesta: cómputo por turno frente a usurpación (persona2), dentro de cada brazo", "",
          "| Brazo | medida de cómputo | Spearman ρ | p |", "|---|---|---|---|"]
    for b in ("G1", "G2"):
        tasa = [tasa_persona2(p, b) for p in pares]
        for k in ("seg_dm", "chars_narracion", "llamadas_ladodm"):
            rho, pv = spearmanr([camp[(b, p)][k] for p in pares], tasa)
            L.append(f"| {b} | {k} | {rho:+.2f} | {pv:.2g} |")
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "costo_arquitectura.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(SALIDA / "costo_arquitectura.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        cols = list(next(iter(camp.values())))
        w.writerow(["brazo", "par"] + cols)
        for (b, p), v in sorted(camp.items()):
            w.writerow([b, p] + [round(v[c], 4) for c in cols])
    print("\n".join(L))


if __name__ == "__main__":
    main()
