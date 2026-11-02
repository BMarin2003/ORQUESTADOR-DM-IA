"""
Pruebas de la versión a4bc-2 de la matriz (SOLO cambian magnitudes mínimas `min`, tras la corrida de
DESARROLLO con a4bc-1; ver docs/research/a4bc_diseno_instrumentos.md, apéndice 9).
Escritas ANTES que matriz_a4bc_v2.py.

    PYTHONUTF8=1 py -m pytest experimento/scripts/instrumentos/test_matriz_a4bc_v2.py -q -p no:cacheprovider
"""
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

CAMBIOS = {("cr2a_crudo", "X2_misma_campana_cercana"): 0.035,
           ("cr2b_cos_turno", "P8"): 0.003,
           ("cr2b_cos_ventana8", "W1_ventana_otro_par"): 0.007,
           ("cr2b_cos_ventana8_sn", "W1_ventana_otro_par"): 0.0025,
           ("cr2a_z_ventana8", "P9"): 0.5}


@pytest.fixture(scope="module")
def m1():
    import matriz_a4bc
    return matriz_a4bc


@pytest.fixture(scope="module")
def m2():
    import matriz_a4bc_v2
    return matriz_a4bc_v2


def test_la_v1_sigue_intacta(m1):
    assert m1.hash_matriz() == "67e6133a51c4c23001038a19bb9894e2afa7b99b5dfef91955e0ee789ec0c54e"


def test_v2_solo_cambia_las_5_magnitudes_minimas_declaradas(m1, m2):
    assert m2.VERSION == "a4bc-2"
    for instr, perts in m1.MATRIZ["celdas"].items():
        for pid, c1 in perts.items():
            c2 = m2.MATRIZ["celdas"][instr][pid]
            assert {k: v for k, v in c1.items() if k != "min"} == {k: v for k, v in c2.items() if k != "min"}, (instr, pid)
            if (instr, pid) in CAMBIOS:
                assert c2["min"] == CAMBIOS[(instr, pid)], (instr, pid)
            else:
                assert c2["min"] == c1["min"], (instr, pid)


def test_v2_tiene_hash_distinto_y_registro_de_fecha_y_hora(m1, m2):
    assert m2.hash_matriz() != m1.hash_matriz()
    assert len(m2.hash_matriz()) == 64
    assert m2.MATRIZ["registrada"] == "2026-09-20 23:39"
    assert m2.MATRIZ["deriva_de"] == {"version": "a4bc-1", "sha256": m1.hash_matriz()}


def test_v2_conserva_la_interfaz_para_el_corredor(m2):
    assert m2.esperado_arnes()["P8"]["cr2a_z"] == "baja"
    assert m2.FECHA == "2026-09-20"


def test_hash_de_la_v2_no_ha_cambiado(m2):
    assert m2.hash_matriz() == "e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744"
