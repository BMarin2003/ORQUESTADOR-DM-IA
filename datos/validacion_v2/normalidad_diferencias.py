"""Shapiro-Wilk sobre las diferencias G1 - G2 (27 pares) de cada instrumento comparativo. Fuente: docs/resultados/por_pareja_ancho.csv (persona2 v3b).
    PYTHONUTF8=1 py datos/validacion_v2/normalidad_diferencias.py -> datos/validacion_v2/normalidad_diferencias.csv
"""
import csv
from pathlib import Path
from scipy.stats import shapiro

RAIZ = Path(__file__).resolve().parent.parent.parent
INS = [("CR-2", "Respuesta a la acción específica (z)", "cr2a_z", "Confirmatorio"),
       ("CR-2", "Solapamiento con la acción (crudo)", "cr2a_crudo", "Descriptivo"),
       ("CR-2", "Anclaje al escenario (coseno, ventana de 8)", "cr2b_cos_v8", "Exploratorio"),
       ("CR-2", "Anclaje sin nombres propios", "cr2b_cos_v8_sn", "Exploratorio"),
       ("CL-1", "Papalampidi C: coherencia de entidad", "papalampidi_C", "Exploratorio"),
       ("CL-1", "Papalampidi V: consistencia de atributos", "papalampidi_V", "Exploratorio"),
       ("CL-2", "Jericho-QA: recuerdo de cambios de estado", "jericho_recall", "Exploratorio"),
       ("CL-2", "PNJ inactivo mencionado", "cl2_pnj_inactivo_actua", "Exploratorio"),
       ("CL-2", "PNJ inactivo como sujeto (refinado)", "pnj_refinado", "Exploratorio"),
       ("QN-1", "TTR a 100 palabras", "ttr100", "Exploratorio"),
       ("QN-1", "Bigramas a 100 palabras", "ngram100", "Exploratorio"),
       ("QN-1", "MTLD", "mtld_campana", "Exploratorio"),
       ("QN-1", "MATTR", "mattr_campana", "Exploratorio"),
       ("QN-2", "Usurpación de la agencia del PJ (persona2)", "p2_primaria", "Confirmatorio condicionado")]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    with open(RAIZ / "docs" / "resultados" / "por_pareja_ancho.csv", newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    out = []
    for ind, nom, col, uso in INS:
        d = [num(r[col + "__G1"]) - num(r[col + "__G2"]) for r in filas if num(r[col + "__G1"]) is not None and num(r[col + "__G2"]) is not None]
        w, p = shapiro(d)
        out.append({"ind": ind, "instrumento": nom, "uso": uso, "n": len(d), "W": f"{w:.3f}", "p": f"{p:.4f}" if p >= 0.0001 else "<0.0001",
                    "normal": "sí" if p >= 0.05 else "no"})
        print(out[-1])
    with open(Path(__file__).parent / "normalidad_diferencias.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
