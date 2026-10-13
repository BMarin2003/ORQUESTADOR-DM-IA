"""Pruebas de szigriszt_pazos (instrumentos_texto.py). Uso: PYTHONUTF8=1 py -m pytest -q experimento/scripts/sensibilidad/test_legibilidad_sz.py"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instrumentos_texto as it  # noqa: E402

T = "El guardia cierra la puerta. Nadie dice una palabra durante un largo rato."


def _partes(t):
    pal = re.findall(r"[a-záéíóúñü]+", t.lower())
    fr = [f for f in re.split(r"[.!?]+", t) if f.strip()]
    return sum(it._vs.contar_silabas_es(p) for p in pal), len(pal), len(fr)


def test_formula_a_mano():
    s, p, f = _partes(T)
    assert it.szigriszt_pazos(T) == round(206.835 - 62.3 * s / p - p / f, 2)


def test_relacion_con_fernandez_huerta():
    """Misma familia: SZ - FH = -0.005 - 2.3*(s/p) + 0.02*(p/f), salvo el redondeo de cada uno a 2 decimales."""
    for t in (T, "Corres. Saltas. Caes.", "Tras cruzar el umbral, percibes de inmediato que la estructura entera del lugar responde a una lógica antigua y deliberada."):
        s, p, f = _partes(t)
        esperado = -0.005 - 2.3 * s / p + 0.02 * p / f
        assert abs((it.szigriszt_pazos(t) - it._vs.fernandez_huerta(t)) - esperado) < 0.02, t


def test_borde():
    assert it.szigriszt_pazos("") is None and it.szigriszt_pazos("...") is None and it.szigriszt_pazos("123 456.") is None


def test_wrapper_y_registro():
    assert it.INSTRUMENTOS["qn1_legibilidad_sz"].ambito == "turno"
    assert it.calcular(T, None, nombres={"qn1_legibilidad_sz"})["qn1_legibilidad_sz"] == it.szigriszt_pazos(T)
