"""
Extiende a los pares 01-06 la verificación de dados y el costo por arquitectura (solo lectura).

Las corridas de esos pares quedaron partidas en varios logs por campaña (reanudaciones), con el mismo
formato de secciones que las bitácoras completas. Se juntan todos los logs cuyo nombre contiene los 8
primeros caracteres del campaign_id (docs/ids_par01-06.json) y se toma la primera aparición de cada turno.
La cobertura de turnos se reporta: algunos tramos iniciales no tienen log.

    $env:PYTHONUTF8="1"; py experimento/scripts/brechas/extension_pares_01_06.py
"""
import json
import statistics as st
import sys
from pathlib import Path

from scipy.stats import wilcoxon

RAIZ = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(RAIZ / "experimento" / "scripts" / "verificacion"), str(RAIZ / "experimento" / "scripts" / "brechas")]
import costo_arquitectura as CA            # noqa: E402
import verificar_dados_pareados as VD      # noqa: E402

LOGS = RAIZ / "datos" / "logs"


def logs_de(cid):
    """Lista los logs (.md o .txt de más de 2000 bytes) de una campaña, identificados por los 8 primeros caracteres de su id."""
    return sorted(p for p in LOGS.rglob(f"*{cid[:8]}*") if p.suffix in (".md", ".txt") and p.stat().st_size > 2000)


def normalizado(ruta):
    """Los logs más antiguos no tienen «## Turno N»: el turno inicial va en la cabecera («- **turno:** N») y
    cada «### [1]» abre el turno siguiente. Se genera una copia temporal con las cabeceras insertadas."""
    import re
    import tempfile
    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    if any(l.startswith("## Turno ") for l in lineas):
        return ruta
    m = next((re.search(r"\*\*turno:\*\*\s*(\d+)", l) for l in lineas if "**turno:**" in l), None)
    t = int(m.group(1)) if m else 1
    out = []
    for l in lineas:
        if l.startswith("### [1] "):
            out.append(f"## Turno {t}\n")
            t += 1
        out.append(l)
    tmp = Path(tempfile.gettempdir()) / f"norm_{ruta.name}"
    tmp.write_text("".join(out), encoding="utf-8")
    return tmp


def main():
    """Extiende la verificación de dados y el costo a los pares 01-06, cuyos logs están fragmentados, y escribe el informe con el mismo formato que los pares 07-27."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ids = json.loads((RAIZ / "docs" / "ids_par01-06.json").read_text(encoding="utf-8"))
    L = ["# Pares 01–06: dados y costo (logs fragmentados)", "",
         "| Par | brazo | logs | turnos con log | tiradas | llamadas lado DM/turno | s lado DM/turno | caracteres/turno |",
         "|---|---|---|---|---|---|---|---|"]
    tot_c = tot_i = 0
    costo = {}
    for e in ids:
        par = f"{int(e['par']):02d}"
        tir, res = {}, {}
        for brazo, cid in (("G1", e["campaign_g1"]), ("G2", e["campaign_g2"])):
            fs = logs_de(cid)
            t_dados, t_costo = {}, {}
            for f in map(normalizado, fs):
                for k, v in VD.tiradas(f).items():
                    t_dados.setdefault(k, v)
                for k, v in CA.leer(f).items():
                    t_costo.setdefault(k, v)
            tir[brazo] = t_dados
            if t_costo:
                res[brazo] = CA.resumen_campana(t_costo)
                costo[(brazo, par)] = res[brazo]
            r = res.get(brazo)
            L.append(f"| {par} | {brazo} | {len(fs)} | {len(t_costo)} | {len(t_dados)} | "
                     + (f"{r['llamadas_ladodm']:.2f} | {r['seg_dm']:.1f} | {r['chars_narracion']:.0f} |" if r else "— | — | — |"))
        comunes = set(tir["G1"]) & set(tir["G2"])
        iguales = sum(tir["G1"][k] == tir["G2"][k] for k in comunes)
        tot_c += len(comunes)
        tot_i += iguales
        L.append(f"| {par} | dados | | | mismo turno+habilidad: {len(comunes)} | d20 igual: {iguales} | | |")
    L += ["", f"**Dados, pares 01–06:** {tot_i}/{tot_c} = {100 * tot_i / max(tot_c, 1):.1f} % de coincidencia (azar = 5 %)."]
    pares = sorted({p for b, p in costo if ("G1", p) in costo and ("G2", p) in costo})
    if pares:
        L += ["", f"**Costo, pares con log en ambos brazos ({len(pares)}):**", "", "| Medida | mediana G1 | mediana G2 | G1>G2 |", "|---|---|---|---|"]
        for k in ("llamadas_ladodm", "seg_dm", "chars_narracion"):
            g1 = [costo[("G1", p)][k] for p in pares]
            g2 = [costo[("G2", p)][k] for p in pares]
            L.append(f"| {k} | {st.median(g1):.2f} | {st.median(g2):.2f} | {sum(a > b for a, b in zip(g1, g2))}/{len(pares)} |")
    salida = RAIZ / "docs" / "reportes" / "brechas" / "pares_01_06.md"
    salida.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
