"""
Pruebas del léxico común de A4b/c (lemas_es.py). Escritas ANTES que el módulo.

    PYTHONUTF8=1 py -m pytest scripts/instrumentos/test_lemas_es.py -q -p no:cacheprovider
"""
import sys
from collections import Counter
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))


@pytest.fixture(scope="module")
def le():
    import lemas_es
    return lemas_es


# ---- clave de un lema
def test_clave_normaliza_minusculas_y_tildes(le):
    assert le.clave("Acción") == "accion"
    assert le.clave("PULSO") == "pulso"


def test_clave_toma_la_primera_palabra_de_un_lema_con_clitico(le):
    assert le.clave("tomar él") == "tomar"


@pytest.mark.parametrize("lema", ["", "de", "a1b", "x", "3d6", "--"])
def test_clave_descarta_lemas_cortos_o_no_alfabeticos(le, lema):
    assert le.clave(lema) is None


# ---- limpieza de formato
G1 = "narrativa\nEl paciente exhala un suspiro.\n\nmecanica\nMedicina: Éxito (17 vs CD 15).\n\npresion\nLa tinta sigue expandiéndose."


def test_limpiar_quita_etiquetas_y_bloque_mecanica_de_g1(le):
    limpio = le.limpiar(G1)
    assert "mecanica" not in limpio and "narrativa" not in limpio and "Medicina" not in limpio
    assert "suspiro" in limpio and "tinta" in limpio


def test_limpiar_es_idempotente_y_no_toca_g2(le):
    g2 = "Herminda Coz te recibe con los ojos hundidos."
    assert le.limpiar(g2) == g2
    assert le.limpiar(le.limpiar(G1)) == le.limpiar(G1)


# ---- lemas de contenido
def test_lemas_de_contenido_sin_stopwords_ni_puntuacion(le):
    ls = le.lemas("Me acerco al paciente para tomar el pulso.")
    assert {"paciente", "pulso", "acercar", "tomar"} <= ls
    assert not ls & {"el", "para", "al"}


def test_lemas_pluralizan_al_mismo_lema(le):
    assert "pupila" in le.lemas("Examina sus pupilas dilatadas.")
    assert "pupila" in le.lemas("La pupila está dilatada.")


def test_pos_por_defecto_excluye_nombres_propios(le):
    assert "herminda" not in le.lemas("Herminda observa al paciente.")
    assert "herminda" in le.lemas("Herminda observa al paciente.", pos=le.POS_CON_NOMBRES)


def test_excluir_quita_lemas_de_una_lista(le):
    ls = le.lemas("La niebla cubre la ciénaga.", excluir={"niebla"})
    assert "niebla" not in ls and "cienaga" in ls


def test_contar_cuenta_repeticiones(le):
    c = le.contar("El pulso es débil. El pulso se acelera.")
    assert isinstance(c, Counter) and c["pulso"] == 2


def test_lemas_aplica_prosa_g1_antes_de_medir(le):
    assert "medicina" not in le.lemas(G1)
    assert "suspiro" in le.lemas(G1)


def test_texto_vacio_da_conjunto_vacio(le):
    assert le.lemas("") == frozenset()
    assert le.contar("") == Counter()


def test_tokens_lote_equivale_a_tokens_uno_a_uno(le):
    textos = ["El paciente respira con dificultad.", "La niebla sube del agua.", ""]
    lote = le.tokens_lote(textos)
    assert lote == [le.tokens(t) for t in textos]


def test_es_determinista(le):
    t = "Sientes un miedo helado en el pasillo oscuro."
    assert le.lemas(t) == le.lemas(t)


# ---- caché en disco
def test_cache_reutiliza_el_resultado_y_se_invalida_si_cambian_los_textos(le, tmp_path):
    textos = ["El paciente respira.", "La niebla sube."]
    a = le.tokens_lote_cacheado("prueba", textos, directorio=tmp_path)
    assert (tmp_path / "prueba.pkl").exists()
    b = le.tokens_lote_cacheado("prueba", textos, directorio=tmp_path)
    assert a == b
    c = le.tokens_lote_cacheado("prueba", textos + ["Otro texto nuevo."], directorio=tmp_path)
    assert len(c) == 3
