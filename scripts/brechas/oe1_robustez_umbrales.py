"""
Robustez de la auditoría OE-1 a sus dos umbrales (solo lectura).

oe1_auditoria_nombres.py clasifica con MIN_MINUS=10 (veces en minúscula para ser «palabra común») y
MIN_TURNOS=3 (turnos distintos para ser «recurrente»). Aquí se recalculan las marcas una sola vez y se
reclasifican sobre una grilla de umbrales para ver cuánto se mueven las cifras que entran a la tesis:
  - % de turnos marcados de G2 con candidata a invención (efímero)
  - % de turnos marcados de G2 con entidad nunca registrada (recurrente o efímero)
  - comparación G1 vs G2 de la tasa de turnos con efímero (Wilcoxon bilateral)

    $env:PYTHONUTF8="1"; py scripts/brechas/oe1_robustez_umbrales.py
"""
import copy
import sys
from collections import Counter, defaultdict
from pathlib import Path

from scipy.stats import wilcoxon

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import oe1_auditoria_nombres as A   # noqa: E402

GRILLA_MINUS = [5, 10, 20, 50]
GRILLA_TURNOS = [2, 3, 5]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    conn = A.datos.abrir_conexion()
    por_camp, minus, mayus = {}, Counter(), Counter()
    for p in A._pares.todos():
        par = f"{int(p['par']):02d}"
        for brazo, cid in (("G1", p["campaign_g1"]), ("G2", p["campaign_g2"])):
            marcas, creado, lore, textos = A.marcar_campana(conn, par, brazo, cid)
            for tx in textos:
                minus.update(A.RX_PAL.findall(tx))
                mayus.update(A.RX_MAYUS.findall(tx))
            por_camp[(brazo, par)] = (marcas, creado, lore, len(textos))
        print(f"  par {par} listo", flush=True)
    L = ["# OE-1: robustez a los umbrales de clasificación", "",
         "| MIN_MINUS | MIN_TURNOS | G2 turnos marcados con efímero | G2 con entidad nunca registrada | "
         "G1 con efímero | mediana tasa efímero G1 / G2 (%) | G1<G2 | p |", "|---|---|---|---|---|---|---|---|"]
    for mm in GRILLA_MINUS:
        for mt in GRILLA_TURNOS:
            A.MIN_MINUS, A.MIN_TURNOS = mm, mt
            cuenta = defaultdict(Counter)
            tasa = {}
            for (brazo, par), (marcas, creado, lore, n) in por_camp.items():
                ms = A.clasificar(copy.deepcopy(marcas), creado, lore, minus, mayus)
                por_turno = defaultdict(set)
                for m in ms:
                    por_turno[m["turno"]].add(m["cat"])
                cuenta[brazo]["marcados"] += len(por_turno)
                cuenta[brazo]["efimero"] += sum("efimero" in c for c in por_turno.values())
                cuenta[brazo]["problema"] += sum(bool(c & A.PROBLEMA) for c in por_turno.values())
                tasa[(brazo, par)] = 100 * sum("efimero" in c for c in por_turno.values()) / n
            pares = sorted({p for _, p in tasa})
            d = [tasa[("G1", p)] - tasa[("G2", p)] for p in pares]
            g1 = sorted(tasa[("G1", p)] for p in pares)
            g2 = sorted(tasa[("G2", p)] for p in pares)
            pct = lambda b, k: 100 * cuenta[b][k] / cuenta[b]["marcados"]  # noqa: E731
            marca = " **(usado)**" if (mm, mt) == (10, 3) else ""
            L.append(f"| {mm}{marca} | {mt} | {pct('G2', 'efimero'):.1f} % | {pct('G2', 'problema'):.1f} % | "
                     f"{pct('G1', 'efimero'):.1f} % | {g1[13]:.2f} / {g2[13]:.2f} | {sum(x < 0 for x in d)}/27 | "
                     f"{wilcoxon(d).pvalue:.3g} |")
    (A.SALIDA / "oe1_robustez.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
