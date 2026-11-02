"""
Pruebas de la MATRIZ DE EXPECTATIVAS PRE-ESPECIFICADA de A4b/c (respuesta a la acción, CR-2a,
y anclaje al escenario, CR-2b). Este archivo se escribió ANTES que matriz_a4bc.py.

    PYTHONUTF8=1 py -m pytest experimento/scripts/instrumentos/test_matriz_a4bc.py -q -p no:cacheprovider

Guarda de integridad: el hash SHA-256 de la matriz se fijó el 2026-09-20 ANTES de correr ningún
instrumento sobre la muestra de evaluación. Si alguien edita una expectativa, el test de hash
falla; los cambios legítimos van en un apéndice «post hoc» del documento, no aquí.
"""
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

DIRS = {"sube", "baja", "sin_cambio"}
INSTRUMENTOS_ESPERADOS = {
    "cr2a_z", "cr2a_crudo", "cr2a_z_ventana8",
    "cr2b_cos_turno", "cr2b_cos_turno_sn", "cr2b_cos_ventana8", "cr2b_cos_ventana8_sn",
}


@pytest.fixture
def m():
    import matriz_a4bc
    return matriz_a4bc


def test_la_matriz_cubre_los_siete_instrumentos(m):
    assert set(m.MATRIZ["celdas"]) == INSTRUMENTOS_ESPERADOS


def test_toda_celda_tiene_direccion_magnitud_justificacion_y_criterio(m):
    for instr, perts in m.MATRIZ["celdas"].items():
        assert perts, instr
        for pid, c in perts.items():
            assert c["dir"] in DIRS, (instr, pid)
            assert isinstance(c["justificacion"], str) and len(c["justificacion"]) > 20, (instr, pid)
            assert isinstance(c["criterio"], str) and len(c["criterio"]) > 20, (instr, pid)
            assert isinstance(c["exacto"], bool)
            assert isinstance(c["descriptivo"], bool)
            if c["dir"] == "sin_cambio":
                assert c["min"] is None, (instr, pid)
            else:
                assert c["min"] is not None and c["min"] > 0, (instr, pid)


def test_los_controles_positivos_de_respuesta_accion_bajan(m):
    z = m.MATRIZ["celdas"]["cr2a_z"]
    for pid in ("X1_misma_campana_lejana", "X2_misma_campana_cercana", "P8"):
        assert z[pid]["dir"] == "baja"
    assert m.MATRIZ["celdas"]["cr2a_z_ventana8"]["P9"]["dir"] == "baja"
    assert m.MATRIZ["celdas"]["cr2a_z_ventana8"]["W1_ventana_otro_par"]["dir"] == "baja"


def test_anclaje_baja_con_otro_par_y_no_distingue_turnos_de_la_misma_campana(m):
    a = m.MATRIZ["celdas"]["cr2b_cos_turno"]
    assert a["P8"]["dir"] == "baja"
    assert a["X1_misma_campana_lejana"]["dir"] == "sin_cambio"
    assert a["X2_misma_campana_cercana"]["dir"] == "sin_cambio"
    assert m.MATRIZ["celdas"]["cr2b_cos_ventana8"]["P9"]["dir"] == "sin_cambio"
    assert m.MATRIZ["celdas"]["cr2b_cos_ventana8"]["P9"]["exacto"] is True


def test_los_controles_de_formato_son_exactos_en_todos_los_instrumentos(m):
    for instr, perts in m.MATRIZ["celdas"].items():
        if "ventana8" in instr:
            continue
        for pid in ("P11a_inyeccion", "P11b_eliminacion"):
            assert perts[pid]["dir"] == "sin_cambio" and perts[pid]["exacto"], (instr, pid)


def test_esperado_para_el_arnes_excluye_las_celdas_descriptivas(m):
    esp = m.esperado_arnes()
    assert "S1_sinonimos" not in esp or "cr2a_z" not in esp.get("S1_sinonimos", {})
    assert esp["P8"]["cr2a_z"] == "baja"
    assert m.MATRIZ["celdas"]["cr2a_z"]["S1_sinonimos"]["descriptivo"] is True


def test_hash_de_la_matriz_prespecificada_no_ha_cambiado(m):
    # Fijado el 2026-09-20 ANTES de correr los instrumentos sobre la muestra de evaluación.
    assert m.hash_matriz() == "67e6133a51c4c23001038a19bb9894e2afa7b99b5dfef91955e0ee789ec0c54e"
