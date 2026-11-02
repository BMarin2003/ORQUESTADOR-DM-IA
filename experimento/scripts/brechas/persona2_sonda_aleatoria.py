"""
persona2: ¿qué tanto se le escapa al detector? Lectura de la sonda aleatoria (solo lectura).

El estrato «sonda_aleatoria» de la muestra de confirmación son turnos tomados al azar de todo el corpus
(confirmacion_persona2.py), con el veredicto real del detector en `hallazgos_detector`. Sobre esos turnos,
la proporción de usurpación según cada evaluador estima la prevalencia en el corpus, y su cruce con el
detector da una idea de la exhaustividad (recall) en la población. Se separan las usurpaciones
mentales/verbales (decisión, pensamiento, emoción, habla: lo que mide `primaria`) de la acción física.

    $env:PYTHONUTF8="1"; py experimento/scripts/brechas/persona2_sonda_aleatoria.py
"""
import csv
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
V = RAIZ / "datos" / "validacion"
MENTAL = {"decision", "pensamiento", "emocion", "habla"}
EVAL = {"E2": "etiquetas_persona2_E2.csv", "E3": "etiquetas_persona2_E3.csv",
        "E4": "etiquetas_persona2_E4.csv", "IA (515)": "etiquetas_persona2_E1_IA-asistido.csv"}


def wilson(x, n, z=1.959964):
    """Intervalo de Wilson al 95 % de una proporción x/n, formateado como porcentajes "inf-sup" con un decimal."""
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * (c - h):.1f}–{100 * (c + h):.1f}"


def main():
    """Tabla por evaluador y brazo de la sonda aleatoria de persona2: turnos al azar, marcados por el detector, usurpación confirmada y la parte mental/verbal con su IC."""
    with open(V / "confirmacion_persona2_clave.csv", encoding="utf-8-sig", newline="") as f:
        clave = {r["id_muestra"]: r for r in csv.DictReader(f)}
    L = ["# persona2: sonda aleatoria (prevalencia y lo que se le escapa al detector)", "",
         "| Evaluador | brazo | turnos al azar | detector + | usurpación (sí) | mental/verbal | % mental/verbal [IC95] |",
         "|---|---|---|---|---|---|---|"]
    for nombre, archivo in EVAL.items():
        with open(V / archivo, encoding="utf-8-sig", newline="") as f:
            et = {r["id_muestra"]: (r["veredicto"], {t for t in r["tipos"].split(";") if t}) for r in csv.DictReader(f)}
        for b in ("G1", "G2"):
            s = [i for i in et if clave[i]["estrato"] == "sonda_aleatoria" and clave[i]["brazo"] == b]
            det = sum(bool(clave[i]["hallazgos_detector"].strip()) for i in s)
            si = [i for i in s if et[i][0] == "si"]
            ment = [i for i in si if et[i][1] & MENTAL]
            L.append(f"| {nombre} | {b} | {len(s)} | {det} | {len(si)} | {len(ment)} | "
                     f"{100 * len(ment) / len(s):.1f} [{wilson(len(ment), len(s))}] |")
    out = RAIZ / "docs" / "reportes" / "brechas" / "persona2_sonda_aleatoria.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
