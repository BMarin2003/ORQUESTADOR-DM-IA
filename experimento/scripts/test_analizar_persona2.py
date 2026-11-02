#!/usr/bin/env python3
"""Pruebas de experimento/scripts/analizar_persona2.py (fórmulas contra valores conocidos + corrida de punta a punta con etiquetas sintéticas).
Uso: PYTHONUTF8=1 py experimento/scripts/test_analizar_persona2.py"""
import csv
import sys
import tempfile
from math import isclose
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analizar_persona2 as A  # noqa: E402

# --- Wilson: 50/100 -> [0.4038, 0.5962] (valor de referencia, z = 1.959964)
lo, hi = A.wilson(50, 100)
assert isclose(lo, 0.4038, abs_tol=5e-4) and isclose(hi, 0.5962, abs_tol=5e-4), (lo, hi)
lo, hi = A.wilson(0, 30)                     # cero eventos: cota inferior 0 y superior ≈ 0.114 (Wilson)
assert lo == 0.0 and isclose(hi, 0.1135, abs_tol=2e-3), (lo, hi)
assert A.wilson(0, 0) == (None, None)

# --- Acuerdo binario, tabla 2x2 (a = ambos sí, b = 1 sí/2 no, c = 1 no/2 sí, d = ambos no)
p = A.acuerdo(40, 5, 5, 50)                  # n = 100, po = .90
assert isclose(p["po"], 0.90) and isclose(p["p_pos"], 80 / 90) and isclose(p["p_neg"], 100 / 110)
# kappa: p1_sí = .45, p2_sí = .45 -> pe = .45*.45 + .55*.55 = .505 -> kappa = (.9-.505)/(1-.505)
assert isclose(p["kappa"], (0.9 - 0.505) / (1 - 0.505), abs_tol=1e-9)
assert isclose(p["pabak"], 2 * 0.90 - 1)
# AC1 (2 evaluadores, binario): pi = .45 -> pe = 2*pi*(1-pi) = .495 -> AC1 = (.9-.495)/(1-.495)
assert isclose(p["ac1"], (0.9 - 0.495) / (1 - 0.495), abs_tol=1e-9)
perfecto = A.acuerdo(20, 0, 0, 30)
assert perfecto["kappa"] == 1.0 and perfecto["ac1"] == 1.0 and perfecto["po"] == 1.0
# Paradoja de kappa (Feinstein & Cicchetti 1990): acuerdo alto con prevalencia muy baja -> kappa bajo, AC1 alto
par = A.acuerdo(2, 3, 3, 92)                 # po = .94
assert par["po"] > 0.9 and par["kappa"] < 0.45 and par["ac1"] > 0.9, par
assert A.acuerdo(0, 0, 0, 0)["po"] is None   # sin datos no revienta

# --- de punta a punta con etiquetas sintéticas
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    clave = td / "clave.csv"
    filas = []
    for i in range(40):                                   # 40 marcas primarias de G2: 30 viola, 10 no
        filas.append({"id_muestra": f"P{i}", "campaign_id": "x", "turn_id": i, "brazo": "G2", "par": "07",
                      "estrato": "primaria:COGNICION", "categoria_asignada": "COGNICION",
                      "hallazgos_detector": "COGNICION:comprender:p2"})
    for i in range(20):                                   # sonda G2: 20 turnos, 4 violan (3 detectados por el detector)
        filas.append({"id_muestra": f"S{i}", "campaign_id": "x", "turn_id": 100 + i, "brazo": "G2", "par": "07",
                      "estrato": "sonda_aleatoria", "categoria_asignada": "",
                      "hallazgos_detector": "HABLA:decir:p2" if i < 3 else ""})
    with clave.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)

    def escribir(nombre, decide):
        ruta = td / nombre
        with ruta.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(["evaluador", "id_muestra", "veredicto", "tipos", "tras_tirada", "nota", "segundos"])
            for r in filas:
                w.writerow(["E", r["id_muestra"], decide(r), "pensamiento" if decide(r) == "si" else "", 0, "", 30])
        return ruta
    def e1(r):
        i = int(r["id_muestra"][1:]); return ("si" if i < 30 else "no") if r["id_muestra"][0] == "P" else ("si" if i in (0, 1, 2, 10) else "no")
    def e2(r):
        i = int(r["id_muestra"][1:]); return ("si" if i < 28 else "no") if r["id_muestra"][0] == "P" else e1(r)
    res = A.analizar(escribir("e1.csv", e1), clave, escribir("e2.csv", e2))
    prim = res["precision"]["primaria:COGNICION|G2"]
    assert prim["si"] == 30 and prim["n"] == 40 and isclose(prim["p"], 0.75)
    son = res["sonda"]["G2"]
    assert son["n"] == 20 and son["viola"] == 4 and son["viola_y_detectada"] == 3
    assert isclose(son["recall"], 0.75)
    assert res["acuerdo"]["n"] == 60 and res["acuerdo"]["b"] + res["acuerdo"]["c"] == 2
    md = A.reporte_md(res)
    assert "Precisión" in md and "Prevalencia" in md and "Acuerdo" in md

print("todas las pruebas de analizar_persona2 pasan")
