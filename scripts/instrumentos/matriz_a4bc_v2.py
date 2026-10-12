"""
Matriz de expectativas A4b/c, versión a4bc-2.

Deriva de matriz_a4bc.py (a4bc-1, congelada; hash en docs/research/a4bc_diseno_instrumentos.md) y cambia
SOLO cinco magnitudes mínimas `min`, según el protocolo del documento (§5, paso 3): la corrida de
DESARROLLO con a4bc-1 (docs/reportes/sensibilidad_a4bc_desarrollo_a4bc-1.md) mostró que en G2 el efecto
de esas celdas es menor que el estimado con el borrador agrupado de ambos brazos, y la regla
«min <= 0,5 x |mediana del efecto en desarrollo|» (aplicada con el brazo de menor efecto) no se cumplía.
Direcciones, controles, celdas exactas/descriptivas, justificaciones y criterios NO cambian.
Registrada el 2026-09-20 23:39, ANTES de correr la evaluación.
"""
import copy
import hashlib
import json

import matriz_a4bc as _v1

VERSION = "a4bc-2"
FECHA = "2026-09-20"

CAMBIOS_MIN = {   # (instrumento, perturbación): (min a4bc-1, min a4bc-2, efecto de desarrollo del brazo de menor efecto)
    ("cr2a_crudo", "X2_misma_campana_cercana"): (0.04, 0.035, 0.0770),
    ("cr2b_cos_turno", "P8"): (0.005, 0.003, 0.0064),
    ("cr2b_cos_ventana8", "W1_ventana_otro_par"): (0.01, 0.007, 0.0144),
    ("cr2b_cos_ventana8_sn", "W1_ventana_otro_par"): (0.003, 0.0025, 0.0054),
    ("cr2a_z_ventana8", "P9"): (1.0, 0.5, 1.373),
}


def _construir():
    """Copia la matriz a4bc-1 y cambia solo los cinco `min` de CAMBIOS_MIN, verificando antes el valor previo; guarda versión, fecha y hash de la matriz de origen."""
    m = copy.deepcopy(_v1._MATRIZ_INICIAL)
    m["version"], m["fecha"] = VERSION, FECHA
    m["registrada"] = "2026-09-20 23:39"
    m["deriva_de"] = {"version": _v1.VERSION, "sha256": _v1.hash_matriz()}
    for (instr, pid), (antes, ahora, _) in CAMBIOS_MIN.items():
        assert m["celdas"][instr][pid]["min"] == antes
        m["celdas"][instr][pid]["min"] = ahora
    return m


MATRIZ = _construir()
_MATRIZ_INICIAL = copy.deepcopy(MATRIZ)


def hash_matriz(matriz=None):
    """SHA-256 canónico (JSON ordenado) de la matriz; sin argumento, de la copia inicial sin alterar, para detectar ediciones posteriores."""
    m = _MATRIZ_INICIAL if matriz is None else matriz
    return hashlib.sha256(json.dumps(m, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def esperado_arnes():
    """Mapa {perturbación: {instrumento: dirección}} en el formato del arnés; omite las celdas descriptivas."""
    out = {}
    for instr, perts in MATRIZ["celdas"].items():
        for pid, cel in perts.items():
            if cel["descriptivo"]:
                continue
            out.setdefault(pid, {})[instr] = cel["dir"]
    return out
