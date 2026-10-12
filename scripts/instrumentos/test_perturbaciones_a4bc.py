"""
Pruebas de perturbaciones_a4bc.py (X1, X2, C1, C2, C3, S1, W1). Escritas ANTES que el módulo.

    PYTHONUTF8=1 py -m pytest scripts/instrumentos/test_perturbaciones_a4bc.py -q -p no:cacheprovider
"""
import copy
import random
import sys
import unicodedata
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "scripts" / "sensibilidad"))


@pytest.fixture(scope="module")
def pa():
    import perturbaciones_a4bc
    return perturbaciones_a4bc


@pytest.fixture(scope="module")
def cx():
    import contexto_a4bc
    return contexto_a4bc


G2 = ("Al pulsar la muñeca del paciente sientes un latido débil e irregular. Sus pupilas, dilatadas y fijas, "
      "ignoran la luz. Herminda Coz te observa desde el fondo del granero.\n\nEl aire huele a vinagre. "
      "¿Qué haces? La niebla sube desde la ciénaga.")
G1 = ("narrativa\nAl pulsar la muñeca del paciente sientes un latido débil e irregular. Sus pupilas, dilatadas y "
      "fijas, ignoran la luz. Herminda Coz te observa.\n\nmecanica\nMedicina: Éxito (17 vs CD 15). Ves un pulso débil.\n\n"
      "presion\nLa niebla sube desde la ciénaga.")


def _ctx(cx):
    return cx.crear(turno=5)


def _rng(s=1):
    return random.Random(s)


# ---- donantes de la misma campaña
def test_donante_lejano_esta_a_50_turnos_o_mas(pa):
    textos = {t: f"texto {t}" for t in range(1, 300)}
    for s in range(20):
        t = pa.elegir_donante_misma_campana(textos, 100, _rng(s), 50, None)
        assert abs(t - 100) >= 50


def test_donante_cercano_esta_entre_3_y_10_turnos(pa):
    textos = {t: f"texto {t}" for t in range(1, 300)}
    for s in range(30):
        t = pa.elegir_donante_misma_campana(textos, 100, _rng(s), 3, 10)
        assert 3 <= abs(t - 100) <= 10


def test_donante_ignora_turnos_vacios_y_es_determinista(pa):
    textos = {t: ("" if t % 2 else f"texto {t}") for t in range(1, 200)}
    a = pa.elegir_donante_misma_campana(textos, 100, _rng(7), 3, 10)
    assert textos[a] and a == pa.elegir_donante_misma_campana(textos, 100, _rng(7), 3, 10)


def test_x1_y_x2_sustituyen_por_el_donante_sin_tocar_el_contexto(pa, cx):
    ctx = _ctx(cx)
    for pid in ("X1_misma_campana_lejana", "X2_misma_campana_cercana"):
        r = pa.aplicar(pid, G2, ctx, _rng(), donante="Otra narración distinta del mismo escenario.")
        assert r.texto == "Otra narración distinta del mismo escenario." and r.ctx.turno == 5


def test_x1_exige_donante(pa, cx):
    with pytest.raises(ValueError):
        pa.aplicar("X1_misma_campana_lejana", G2, _ctx(cx), _rng())


# ---- C1 reordenar oraciones
def _oraciones(t):
    import re
    return [o.strip() for o in re.split(r"(?<=[.!?])\s+", t) if o.strip()]


def test_c1_reordena_las_oraciones_conservando_las_palabras(pa, cx):
    r = pa.aplicar("C1_reorden_oraciones", G2, _ctx(cx), _rng())
    assert r.texto != G2
    assert sorted(_oraciones(r.texto)) == sorted(_oraciones(G2))
    assert sorted(r.texto.split()) == sorted(G2.split())


def test_c1_en_g1_solo_toca_la_zona_narrativa(pa, cx):
    r = pa.aplicar("C1_reorden_oraciones", G1, _ctx(cx), _rng(3))
    assert "mecanica\nMedicina: Éxito (17 vs CD 15). Ves un pulso débil." in r.texto
    assert r.texto.startswith("narrativa\n")
    assert r.texto.endswith("presion\nLa niebla sube desde la ciénaga.")


def test_c1_no_es_elegible_con_menos_de_3_oraciones(pa, cx):
    assert not pa.elegible("C1_reorden_oraciones", "Una sola oración.", _ctx(cx))
    assert pa.elegible("C1_reorden_oraciones", G2, _ctx(cx))


# ---- C2 minúsculas / C3 sin tildes
def test_c2_pasa_a_minusculas_solo_la_narracion(pa, cx):
    r = pa.aplicar("C2_minusculas", G1, _ctx(cx), _rng())
    assert "herminda coz" in r.texto and "Herminda" not in r.texto
    assert "Medicina: Éxito" in r.texto       # la línea mecánica no se toca


def test_c3_quita_las_tildes_pero_conserva_la_enie(pa, cx):
    t = "La ciénaga huele a año viejo; ¿qué pasó? Sí, más allá. Pingüino."
    r = pa.aplicar("C3_sin_tildes", t, _ctx(cx), _rng())
    assert r.texto == "La cienaga huele a año viejo; ¿que paso? Si, mas alla. Pinguino."
    sin_marcas = "".join(c for c in unicodedata.normalize("NFD", r.texto) if unicodedata.category(c) == "Mn")
    assert "̃" in sin_marcas          # la tilde de la ñ sigue ahí
    assert len(r.texto) == len(t)


# ---- S1 sinónimos
def test_s1_sustituye_palabras_del_diccionario_y_conserva_las_mayusculas(pa, cx):
    r = pa.aplicar("S1_sinonimos", "Ves al paciente débil. Miras el pulso. Pacientes cansados.", _ctx(cx), _rng())
    assert "enfermo" in r.texto and "frágil" in r.texto and "Observas" in r.texto
    assert "Enfermos" in r.texto                          # mayúscula inicial conservada
    assert "paciente" not in r.texto.replace("Pacientes", "")
    assert r.info["n_sustituciones"] >= 4


def test_s1_no_toca_un_texto_sin_palabras_del_diccionario(pa, cx):
    t = "Un dragón duerme sobre el oro."
    r = pa.aplicar("S1_sinonimos", t, _ctx(cx), _rng())
    assert r.texto == t and r.info["n_sustituciones"] == 0


def test_s1_respeta_las_etiquetas_de_g1(pa, cx):
    r = pa.aplicar("S1_sinonimos", G1, _ctx(cx), _rng())
    assert "mecanica\nMedicina: Éxito (17 vs CD 15). Ves un pulso débil." in r.texto


def test_el_diccionario_de_s1_no_mapea_una_palabra_a_si_misma(pa):
    assert all(k != v for k, v in pa.SINONIMOS.items())
    assert len(pa.SINONIMOS) >= 40


# ---- W1 ventana de otro par
def test_w1_sustituye_la_ventana_por_los_donantes(pa):
    textos = [f"t{i}" for i in range(8)]
    donantes = [f"d{i}" for i in range(8)]
    r = pa.perturbar_ventana_w1(textos, donantes)
    assert r.textos == donantes and r.textos is not donantes
    with pytest.raises(ValueError):
        pa.perturbar_ventana_w1(textos, donantes[:3])


# ---- generales
@pytest.mark.parametrize("pid", ["C1_reorden_oraciones", "C2_minusculas", "C3_sin_tildes", "S1_sinonimos"])
def test_determinista_y_no_muta_entradas(pa, cx, pid):
    ctx = _ctx(cx)
    copia = copy.deepcopy(ctx.turno)
    a = pa.aplicar(pid, G2, ctx, _rng(9))
    b = pa.aplicar(pid, G2, ctx, _rng(9))
    assert a.texto == b.texto and ctx.turno == copia


def test_el_despachador_usa_las_del_arnes_para_p5_p6_p8_p11(pa, cx):
    ctx = _ctx(cx)
    r = pa.aplicar("P5", G2, ctx, _rng())
    assert r.texto != G2 and "murmura el nombre" in r.texto or "Se dice" in r.texto
    r = pa.aplicar("P8", G2, ctx, _rng(), donante="Narración de otro par.")
    assert r.texto == "Narración de otro par."
    assert pa.aplicar("P11a_inyeccion", G2, cx.crear(brazo="G2"), _rng()).texto.startswith("narrativa\n")
    assert "narrativa" not in pa.aplicar("P11b_eliminacion", G1, cx.crear(brazo="G1"), _rng()).texto
