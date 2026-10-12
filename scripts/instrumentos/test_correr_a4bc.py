"""
Pruebas de las piezas puras de correr_a4bc.py (bloques, proxy de nombres, criterio de aprobación,
regla de calibración de `min`). Escritas ANTES que el corredor.

    PYTHONUTF8=1 py -m pytest scripts/instrumentos/test_correr_a4bc.py -q -p no:cacheprovider
"""
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "scripts" / "sensibilidad"))


@pytest.fixture(scope="module")
def cr():
    import correr_a4bc
    return correr_a4bc


def test_bloques_de_200_turnos(cr):
    b = cr.bloques(1400)
    assert len(b) == 7 and b[0] == (1, 200) and b[-1] == (1201, 1400)
    assert all(b[i][1] + 1 == b[i + 1][0] for i in range(6))


def test_el_hash_de_la_matriz_que_se_corre_es_el_congelado_a4bc_2(cr):
    import matriz_a4bc_v2 as m
    assert cr.hash_matriz_activa() == m.hash_matriz()
    assert cr.hash_matriz_activa() == "e1570cad2f6b593c1cb418ccbc2f22210cedb24c64bc66f9db7a699579078744"


def test_delta_relativo_para_la_lectura_post_hoc_de_los_controles(cr):
    assert cr.rel_dif(2.865, -0.002) == pytest.approx(-0.0007, abs=1e-4)
    assert cr.rel_dif(0.049, -0.003) == pytest.approx(-0.061, abs=1e-3)
    assert cr.rel_dif(0.0, 0.1) is None
    assert cr.despreciable(cr.rel_dif(2.865, -0.002)) and not cr.despreciable(cr.rel_dif(0.049, -0.003))


def test_proxy_de_nombres_detecta_nombre_completo_y_palabras_capitalizadas(cr):
    rx = cr.regex_nombres(["Herminda Coz", "La Casa de Cuarentena", "Bruma Honda"])
    assert cr.menciona_nombre("Herminda te observa.", rx)
    assert cr.menciona_nombre("La niebla de Bruma se espesa.", rx)
    assert cr.menciona_nombre("Entras en la Casa de Cuarentena.", rx)
    assert not cr.menciona_nombre("La niebla sube desde la ciénaga.", rx)
    assert not cr.menciona_nombre("herminda en minúscula no cuenta", rx)


def test_proxy_ignora_el_formato_g1(cr):
    rx = cr.regex_nombres(["Herminda Coz"])
    g1 = "narrativa\nLa niebla sube.\n\nmecanica\nHerminda Coz: Éxito (17 vs CD 15).\n\npresion\nNada."
    assert not cr.menciona_nombre(g1, rx)     # el nombre solo aparece en la sección «mecanica» (se elimina)


def _fila(veredicto, mediana, n=150):
    return {"veredicto": veredicto, "mediana_dif": mediana, "n": n}


CEL_BAJA = {"dir": "baja", "min": 1.0, "exacto": False, "descriptivo": False}
CEL_IGUAL = {"dir": "sin_cambio", "min": None, "exacto": False, "descriptivo": False}
CEL_EXACTA = {"dir": "sin_cambio", "min": None, "exacto": True, "descriptivo": False}
CEL_DESC = {"dir": "baja", "min": 0.1, "exacto": False, "descriptivo": True}


def test_aprobacion_baja_exige_veredicto_y_magnitud(cr):
    assert cr.aprobacion(CEL_BAJA, _fila("responde", -2.0), True) == "aprobada"
    assert cr.aprobacion(CEL_BAJA, _fila("responde", -0.5), True) == "falla"        # efecto menor que min
    assert cr.aprobacion(CEL_BAJA, _fila("no responde", -2.0), True) == "falla"
    assert cr.aprobacion(CEL_BAJA, _fila("responde", +2.0), True) == "falla"        # signo contrario


def test_aprobacion_de_control_igual_y_exacto(cr):
    assert cr.aprobacion(CEL_IGUAL, _fila("responde", 0.0), False) == "aprobada"
    assert cr.aprobacion(CEL_IGUAL, _fila("cambio inesperado", -0.3), False) == "falla"
    assert cr.aprobacion(CEL_EXACTA, _fila("responde", 0.0), True) == "aprobada"
    assert cr.aprobacion(CEL_EXACTA, _fila("responde", 0.0), False) == "falla"       # alguna diferencia != 0


def test_aprobacion_descriptiva_y_pocos_pares(cr):
    assert cr.aprobacion(CEL_DESC, _fila("responde", -1.0), False) == "descriptiva"
    assert cr.aprobacion(CEL_BAJA, _fila("no aplica", 0.0, n=3), True) == "no aplica"


def test_regla_de_calibracion_de_min_es_la_mitad_del_efecto_de_desarrollo(cr):
    assert cr.min_cumple_regla(CEL_BAJA, -2.5)          # 1.0 <= 0.5 * 2.5
    assert not cr.min_cumple_regla(CEL_BAJA, -1.5)      # 1.0 > 0.75
    assert not cr.min_cumple_regla(CEL_BAJA, +2.5)      # signo contrario
    assert cr.min_cumple_regla(CEL_IGUAL, 0.0) is None  # no aplica a controles


def test_las_celdas_calibradas_en_desarrollo_estan_en_la_matriz(cr):
    import matriz_a4bc_v2 as m
    for instr, pid in cr.CELDAS_CALIBRADAS:
        assert pid in m.MATRIZ["celdas"][instr], (instr, pid)
