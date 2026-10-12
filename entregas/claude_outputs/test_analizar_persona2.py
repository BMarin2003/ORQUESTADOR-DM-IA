#!/usr/bin/env python3
"""
Verificación de fórmulas de analizar_persona2.py contra valores calculados a mano (sin scipy,
sin dependencias externas). Correr con: python scripts/test_analizar_persona2.py
Sale con código 0 si todo pasa, 1 si algo falla (imprime qué).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analizar_persona2 import cohen_binario, fleiss_kappa, wilson  # noqa: E402

fallos = []


def check(nombre, obtenido, esperado, tol=1e-6):
    if esperado is None:
        ok = obtenido is None
    elif isinstance(esperado, tuple):
        ok = obtenido == esperado
    else:
        ok = obtenido is not None and abs(obtenido - esperado) < tol
    estado = "OK" if ok else "FALLO"
    print(f"[{estado}] {nombre}: obtenido={obtenido} esperado={esperado}")
    if not ok:
        fallos.append(nombre)


# --- cohen_binario: a=10 (ambos sí), b=5 (1 sí/2 no), c=15 (1 no/2 sí), d=20 (ambos no), n=50 ---
# p1=(10+5)/50=.30  p2=(10+15)/50=.50  po=(10+20)/50=.60
# pe_kappa = .30*.50 + .70*.50 = .15+.35 = .50 -> kappa=(.60-.50)/(1-.50)=0.20
# pabak = 2*.60-1 = 0.20
# pi=(.30+.50)/2=.40  pe_gwet=2*.40*.60=.48 -> ac1=(.60-.48)/(1-.48)=0.12/0.52=0.230769...
r = cohen_binario(10, 5, 15, 20)
check("cohen_binario n", r["n"], 50)
check("cohen_binario po", r["po"], 0.60)
check("cohen_binario kappa", r["kappa"], 0.20)
check("cohen_binario pabak", r["pabak"], 0.20)
check("cohen_binario ac1", r["ac1"], 0.12 / 0.52)

# --- caso degenerado: n=0 ---
r0 = cohen_binario(0, 0, 0, 0)
check("cohen_binario n=0 -> po", r0["po"], None)
check("cohen_binario n=0 -> kappa", r0["kappa"], None)

# --- acuerdo perfecto: kappa debe ser 1.0 ---
rp = cohen_binario(30, 0, 0, 20)
check("cohen_binario acuerdo perfecto kappa", rp["kappa"], 1.0)
check("cohen_binario acuerdo perfecto ac1", rp["ac1"], 1.0)

# --- fleiss_kappa: 3 sujetos, 3 evaluadores, 2 categorías A/B ---
# sujeto1: A,A,A (3,0) | sujeto2: B,B,B (0,3) | sujeto3: A,A,B (2,1)
# p_A=(3+0+2)/9=5/9  p_B=(0+3+1)/9=4/9  Pe=(5/9)^2+(4/9)^2=41/81
# Pi: sujeto1=(9-3)/6=1.0  sujeto2=(9-3)/6=1.0  sujeto3=(5-3)/6=1/3
# P_bar=(1+1+1/3)/3=7/9  kappa=(7/9-41/81)/(1-41/81)=(63/81-41/81)/(40/81)=22/40=0.55
tabla = {1: {"A": 3, "B": 0}, 2: {"A": 0, "B": 3}, 3: {"A": 2, "B": 1}}
check("fleiss_kappa ejemplo a mano", fleiss_kappa(tabla, ["A", "B"]), 0.55)

# --- fleiss_kappa: acuerdo perfecto entre todos -> kappa=1.0 ---
tabla_perfecta = {i: {"A": 3, "B": 0} for i in range(1, 6)}
tabla_perfecta.update({i: {"A": 0, "B": 3} for i in range(6, 11)})
check("fleiss_kappa acuerdo perfecto", fleiss_kappa(tabla_perfecta, ["A", "B"]), 1.0)

# --- fleiss_kappa: caso con <2 respuestas se excluye, no debe romper ---
tabla_incompleta = dict(tabla)
tabla_incompleta[4] = {"A": 1}  # solo 1 respuesta, debe excluirse del cálculo
check("fleiss_kappa ignora filas con <2 respuestas",
      fleiss_kappa(tabla_incompleta, ["A", "B"]), 0.55)

# --- wilson: propiedades básicas (no valores exactos de tabla, para no depender de memoria) ---
lo, hi = wilson(50, 100)  # p=0.5, n=100 -> IC ancho, debe contener 0.5 y estar dentro de [0,1]
check("wilson contiene el punto (lo<=p)", lo <= 0.5, True)
check("wilson contiene el punto (p<=hi)", 0.5 <= hi, True)
lo2, hi2 = wilson(1000, 1000)  # p=1.0 con n grande -> IC angosto pegado a 1
check("wilson p=1 con n grande: hi<=1", hi2 <= 1.0, True)
check("wilson p=1 con n grande: lo cercano a 1", lo2 > 0.99, True)
check("wilson n=0 -> (None, None)", wilson(0, 0), (None, None))

print()
if fallos:
    print(f"FALLARON {len(fallos)} de las verificaciones: {fallos}")
    sys.exit(1)
print("Todas las verificaciones pasaron.")
