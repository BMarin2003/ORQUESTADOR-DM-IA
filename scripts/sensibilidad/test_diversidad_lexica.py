"""Pruebas de mtld y mattr (instrumentos_texto.py). Uso: PYTHONUTF8=1 py -m pytest -q scripts/sensibilidad/test_diversidad_lexica.py"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instrumentos_texto as it  # noqa: E402


def mattr_ingenuo(p, ventana=50):
    """Definición directa (la del spec): un set por ventana."""
    n = len(p)
    if n < ventana:
        return round(len(set(p)) / n, 3) if n else None
    t = [len(set(p[i:i + ventana])) / ventana for i in range(n - ventana + 1)]
    return round(sum(t) / len(t), 3)


def test_mtld_a_mano():
    assert it.mtld(["a", "b"] * 6) == 3.0                 # a, b (TTR 1), a (2/3 <= .72): un factor cada 3 palabras, 12 / 4
    assert it.mtld(["x"] * 160) == 2.0                    # x (1), x (.5): un factor cada 2 palabras
    assert it.mtld([f"w{i}" for i in range(200)]) == 200.0   # TTR siempre 1: sin factores, devuelve la longitud


def test_mtld_borde():
    assert it.mtld([]) is None and it.mtld(list("abcdefghi")) is None     # < 10 palabras
    assert it.mtld(list("abcdefghij")) == 10.0


def test_mtld_orden_de_la_diversidad():
    rng = random.Random(3)
    variado = [f"w{rng.randrange(300)}" for _ in range(600)]
    pobre = [f"w{rng.randrange(20)}" for _ in range(600)]
    assert it.mtld(variado) > it.mtld(pobre)
    assert it.mattr(variado) > it.mattr(pobre)


def test_mattr_incremental_igual_al_ingenuo():
    rng = random.Random(7)
    for n, vocab, v in [(60, 10, 50), (400, 30, 50), (1000, 200, 50), (500, 5, 20), (120, 80, 100)]:
        p = [f"w{rng.randrange(vocab)}" for _ in range(n)]
        assert it.mattr(p, v) == mattr_ingenuo(p, v), (n, vocab, v)


def test_mattr_borde():
    assert it.mattr([]) is None
    assert it.mattr(["a", "b", "a"]) == round(2 / 3, 3)               # menos palabras que la ventana: TTR simple
    assert it.mattr(["a", "b"] * 30) == 0.04                          # cada ventana de 50 tiene 2 tipos


def test_registradas_como_ventana():
    for nombre in ("ventana_mtld", "ventana_mattr"):
        assert it.INSTRUMENTOS[nombre].ambito == "ventana"
    textos = ["El guardia mira la puerta cerrada y espera.", "Una lámpara oscila sobre la mesa de piedra."] * 10
    v = it.calcular_ventana(textos, None, nombres={"ventana_mtld", "ventana_mattr"})
    assert v["ventana_mtld"] is not None and 0 < v["ventana_mattr"] <= 1
