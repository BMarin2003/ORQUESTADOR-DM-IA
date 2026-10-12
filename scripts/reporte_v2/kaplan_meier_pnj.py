"""
Brecha C: Kaplan-Meier sobre `t_pnj` (turno de la primera mención narrada de un PNJ no vivo;
`cl2_pnj_inactivo_actua` v2 -- ver scripts/reporte_v2/medidas_cierre.py) -- OE-6 punto 3 de
docs/cierre_brechas.md: "PARCIAL... Qué falta: Kaplan-Meier o similar si se decide". El Anexo B de
ese documento ya muestra incidencia cruda por umbral de turno; esto formaliza lo mismo como curva
de supervivencia con censura y una prueba de significancia (log-rank), sin tocar ningún dato:
lee `datos_v2/cierre/por_campana.csv` (ya calculado por medidas_cierre.py), no corre SQL ni LLM.

Evento = turno de la primera mención de un PNJ no vivo (columna `t_pnj`, vacía = censurado en
turno 1400 -- el mismo límite HASTA=1400 que usa todo el consolidado v2, incluido Par02 G2 que
tiene más turnos en la base). "Sobrevivir" = la campaña aún NO ha narrado a un PNJ no vivo como si
actuara: sobrevivir MÁS tiempo es mejor (menos degradación del linaje causal), lo mismo que ya dice
la fila cl2_pnj_inactivo_actua del consolidado (sentido ↓, menos es mejor para el evento).

Dos comparaciones G1 vs G2 (log-rank, Mantel-Haenszel, bilateral):
  1. Agrupada: las 27 parejas juntas (n=27 por brazo). Primaria.
  2. Por lote (robustez, mismo criterio que consolidar.py): Par01-17 (motor sin avance de reloj)
     vs Par18-27 (con reloj determinista, dados de combate y guardia de metamensajes) -- el motor
     cambió a mitad de la generación del corpus, así que si el signo se invierte entre lotes la
     diferencia agregada no es estable (mismo criterio que el resto del consolidado v2).

Salida: docs/reportes/kaplan_meier_pnj.md, .csv (tabla de la curva punto a punto) y .png (curvas).
    PYTHONUTF8=1 py scripts/reporte_v2/kaplan_meier_pnj.py
"""
import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
ENTRADA = RAIZ / "datos_v2" / "cierre" / "por_campana.csv"
SALIDA = RAIZ / "docs" / "reportes" / "kaplan_meier_pnj"
HASTA = 1400          # mismo límite que medidas_cierre.py y el resto del consolidado v2


def cargar():
    """Lee `por_campana.csv` y devuelve, por brazo, observaciones {par, tiempo, evento}.

    `t_pnj` vacío significa censura en el turno `HASTA` (1400): evento=False.
    """
    filas = list(csv.DictReader(ENTRADA.open(encoding="utf-8")))
    out = {"G1": [], "G2": []}
    for r in filas:
        t = r["t_pnj"].strip()
        tiempo = int(t) if t else HASTA
        evento = bool(t)             # evento=True si hubo mención antes de HASTA; False=censurado en HASTA
        out[r["brazo"]].append({"par": r["par"], "tiempo": tiempo, "evento": evento})
    return out


# ---------------------------------------------------------------- estimador producto-límite
def kaplan_meier(obs):
    """obs: lista de {tiempo, evento}. Devuelve lista de puntos (t, S, n_riesgo, d_eventos,
    c_censurados) en cada tiempo de evento único, S = estimador producto-límite de Kaplan-Meier."""
    tiempos_evento = sorted({o["tiempo"] for o in obs if o["evento"]})
    n = len(obs)
    S = 1.0
    puntos = [(0, 1.0, n, 0, 0)]
    for t in tiempos_evento:
        en_riesgo = sum(1 for o in obs if o["tiempo"] >= t)
        d = sum(1 for o in obs if o["tiempo"] == t and o["evento"])
        c = sum(1 for o in obs if o["tiempo"] == t and not o["evento"])
        S *= (1 - d / en_riesgo) if en_riesgo else 1.0
        puntos.append((t, S, en_riesgo, d, c))
    return puntos


def mediana(puntos):
    """Primer turno en que S(t) <= 0.5; None si la curva nunca baja de 0.5 (evento poco frecuente)."""
    for t, S, *_ in puntos:
        if S <= 0.5:
            return t
    return None


# ---------------------------------------------------------------- log-rank (Mantel-Haenszel, 2 grupos)
def logrank(obs_a, obs_b):
    """Prueba log-rank (Mantel-Haenszel, bilateral) entre dos grupos de observaciones censuradas.

    Returns:
        Dict con eventos observados y esperados del grupo A, chi2 (1 gl), p y nº de tiempos con evento.
        Si la varianza es 0 devuelve chi2 = 0 y p = 1.
    """
    tiempos = sorted({o["tiempo"] for o in obs_a + obs_b if o["evento"]})
    O_a = E_a = V = 0.0
    for t in tiempos:
        n_a = sum(1 for o in obs_a if o["tiempo"] >= t)
        n_b = sum(1 for o in obs_b if o["tiempo"] >= t)
        d_a = sum(1 for o in obs_a if o["tiempo"] == t and o["evento"])
        d_b = sum(1 for o in obs_b if o["tiempo"] == t and o["evento"])
        n, d = n_a + n_b, d_a + d_b
        if n <= 1 or d == 0:
            continue
        E_a += d * n_a / n
        V += d * (n_a / n) * (n_b / n) * (n - d) / (n - 1)
        O_a += d_a
    if V == 0:
        return {"O_a": O_a, "E_a": E_a, "chi2": 0.0, "p": 1.0, "n_eventos": sum(1 for t in tiempos)}
    chi2 = (O_a - E_a) ** 2 / V
    from scipy import stats
    p = 1 - stats.chi2.cdf(chi2, df=1)
    return {"O_a": O_a, "E_a": E_a, "chi2": chi2, "p": p, "n_eventos": len(tiempos)}


def resumen_grupo(obs):
    """Resumen de un brazo: n, eventos, censurados y mediana de supervivencia."""
    n = len(obs)
    eventos = sum(1 for o in obs if o["evento"])
    return {"n": n, "eventos": eventos, "censurados": n - eventos, "mediana": mediana(kaplan_meier(obs))}


def main():
    """Calcula Kaplan-Meier por brazo y log-rank (agrupado y por lote Par01-17 / Par18-27) sobre `t_pnj`.

    Escribe `kaplan_meier_pnj.csv` (puntos de la curva), `.png` (curvas escalonadas) y `.md` (informe con límites).
    El análisis por lote es el control de robustez: el motor cambió entre lotes.
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    datos = cargar()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    km_g1, km_g2 = kaplan_meier(datos["G1"]), kaplan_meier(datos["G2"])
    lr = logrank(datos["G1"], datos["G2"])
    r1, r2 = resumen_grupo(datos["G1"]), resumen_grupo(datos["G2"])

    # robustez por lote (mismo criterio que consolidar.py: Par01-17 motor sin reloj, Par18-27 con reloj)
    lote = {"v1": {"G1": [o for o in datos["G1"] if int(o["par"]) <= 17], "G2": [o for o in datos["G2"] if int(o["par"]) <= 17]},
            "v2": {"G1": [o for o in datos["G1"] if int(o["par"]) >= 18], "G2": [o for o in datos["G2"] if int(o["par"]) >= 18]}}
    lr_lote = {k: logrank(v["G1"], v["G2"]) for k, v in lote.items()}

    print(f"G1: n={r1['n']} eventos={r1['eventos']} censurados={r1['censurados']} mediana={r1['mediana']}")
    print(f"G2: n={r2['n']} eventos={r2['eventos']} censurados={r2['censurados']} mediana={r2['mediana']}")
    print(f"log-rank agrupado: O_G1={lr['O_a']:.1f} E_G1={lr['E_a']:.2f} chi2={lr['chi2']:.3f} p={lr['p']:.4f}")
    for k, v in lr_lote.items():
        print(f"  log-rank lote {k}: chi2={v['chi2']:.3f} p={v['p']:.4f}")

    # --- CSV: puntos de ambas curvas
    with open(f"{SALIDA}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["brazo", "turno", "S", "n_riesgo", "d_eventos", "c_censurados"])
        for brazo, puntos in (("G1", km_g1), ("G2", km_g2)):
            for t, S, n_r, d, c in puntos:
                w.writerow([brazo, t, f"{S:.6f}", n_r, d, c])

    # --- PNG: curvas escalonadas G1 vs G2
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def _escalon(puntos):
        """Convierte los puntos de la curva KM en coordenadas de escalón, extendidas hasta `HASTA`."""
        xs, ys = [0], [1.0]
        for t, S, *_ in puntos[1:]:
            xs += [t, t]; ys += [ys[-1], S]
        xs.append(HASTA); ys.append(ys[-1])
        return xs, ys

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for brazo, puntos, color in (("G1 (multiagente)", km_g1, "#4C72B0"), ("G2 (monolítico)", km_g2, "#C44E52")):
        xs, ys = _escalon(puntos)
        ax.step(xs, ys, where="post", label=brazo, color=color, linewidth=1.8)
    ax.set_xlabel("turno"); ax.set_ylabel("fracción de campañas SIN mención de PNJ no vivo")
    ax.set_title(f"Supervivencia: primera mención de un PNJ no vivo (log-rank p={lr['p']:.3f})")
    ax.set_xlim(0, HASTA); ax.set_ylim(0, 1.02); ax.legend(); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(f"{SALIDA}.png", dpi=150)

    # --- informe
    def _fila_lote(k, nombre):
        """Fila Markdown de la tabla log-rank para un lote de `lr_lote`."""
        v = lr_lote[k]
        return f"| {nombre} | {v['O_a']:.1f} | {v['E_a']:.2f} | {v['chi2']:.3f} | {v['p']:.4f} |"

    md = ["# Kaplan-Meier: primera mención narrada de un PNJ no vivo (t_pnj)", "",
          f"Evento = primer turno en que la narración menciona a un PNJ no vivo como si actuara "
          f"(`cl2_pnj_inactivo_actua` v2; columna `t_pnj` de `datos_v2/cierre/por_campana.csv`). "
          f"Censurado en el turno {HASTA} si nunca ocurre (mismo límite HASTA que el resto del consolidado v2). "
          "Sobrevivir más tiempo = menos degradación del linaje causal (mejor).", "",
          "## Resumen por brazo", "",
          "| brazo | n | eventos | censurados | mediana (turno) |", "|---|---|---|---|---|",
          f"| G1 | {r1['n']} | {r1['eventos']} | {r1['censurados']} | {r1['mediana'] if r1['mediana'] else '— (S nunca < 0.5)'} |",
          f"| G2 | {r2['n']} | {r2['eventos']} | {r2['censurados']} | {r2['mediana'] if r2['mediana'] else '— (S nunca < 0.5)'} |", "",
          "## Log-rank (Mantel-Haenszel, bilateral)", "",
          "| comparación | O(G1) | E(G1) | χ² | p |", "|---|---|---|---|---|",
          f"| las 27 parejas | {lr['O_a']:.1f} | {lr['E_a']:.2f} | {lr['chi2']:.3f} | {lr['p']:.4f} |",
          _fila_lote("v1", "Par01-17 (sin reloj)"), _fila_lote("v2", "Par18-27 (con reloj)"), "",
          "O(G1)/E(G1) = eventos observados/esperados bajo H0 (misma supervivencia) en G1, sumados sobre los turnos "
          "con al menos un evento en cualquiera de los dos brazos. p < 0.05 ⇒ las curvas difieren.", "",
          "## Curva", "", f"![curva]({SALIDA.name}.png)", "", "## Límites", "",
          "- Censura en 1400 turnos: 11/27 campañas de cada brazo nunca narran un PNJ no vivo actuando dentro de la "
          "ventana observada; el estimador KM ya lo trata como censura (no como ausencia de evento), pero la cola "
          "de la curva más allá del último evento observado no está identificada.",
          "- `t_pnj` mide MENCIÓN, no acción — la misma limitación que ya declara la fila `cl2_pnj_inactivo_actua` "
          "del consolidado (Auditar la precisión de `cl2_pnj_inactivo_actua`, fase posterior); esto no la resuelve, "
          "solo cambia la forma del análisis (curva de supervivencia en vez de proporción cruda por umbral).",
          "- No pareado: el log-rank agrupado trata las 27 parejas de cada brazo como dos muestras independientes, "
          "no aprovecha el diseño pareado por escenario que usa el resto del consolidado (HL/Wilcoxon por pareja). "
          "Un log-rank estratificado por pareja sería más consistente con esa convención pero no está implementado "
          "aquí; la comparación por lote (Par01-17 vs Par18-27) es el único control de robustez incluido.", ""]
    SALIDA.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    print(f"escrito {SALIDA}.md, .csv y .png")


if __name__ == "__main__":
    main()
