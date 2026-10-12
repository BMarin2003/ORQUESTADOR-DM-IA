"""
Pruebas de respuesta_accion.py (CR-2a). Escritas ANTES que el módulo.

    PYTHONUTF8=1 py -m pytest scripts/instrumentos/test_respuesta_accion.py -q -p no:cacheprovider

Casos escritos a mano en español (acciones del jugador en 1.ª persona con diálogo entre comillas y
etiqueta de tirada, respuestas del DM en 2.ª persona o formato G1).
"""
import random
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "scripts" / "sensibilidad"))


@pytest.fixture(scope="module")
def ra():
    import respuesta_accion
    return respuesta_accion


ACCION_PULSO = ('"Tranquilo, no te voy a dejar así."\n\nMe acerco al paciente más joven y le tomo el pulso, '
                'examinando sus pupilas dilatadas.\n\n{Medicina}')
RESP_PULSO = ("Al pulsar la muñeca del paciente sientes un latido débil e irregular. Sus pupilas, "
              "dilatadas y fijas, ignoran la luz de la vela.")
RESP_BARCO = ("El capitán ordena arriar las velas mientras el marinero de guardia vigila el horizonte. "
              "Las olas golpean el casco del barco con furia y el timonel aprieta el timón.")

_SUSTANTIVOS = ["puerta", "cerradura", "ventana", "escalera", "cofre", "llave", "espada", "escudo", "antorcha",
                "cuerda", "mesa", "banco", "muro", "torre", "puente", "camino", "bosque", "río", "piedra",
                "carta", "sello", "mapa", "libro", "estante", "barril", "caja", "sótano", "techo", "pared",
                "suelo", "lámpara", "cortina", "espejo", "campana", "altar", "vela", "cadena", "reja", "foso"]
_ADJ = ["viejo", "roto", "oscuro", "húmedo", "pesado", "helado", "polvoriento", "cerrado", "oxidado"]


def _pool(ra, n=120, semilla=3, largos=False):
    """Pool de acciones sintéticas (vocabulario sin 'pulso', 'pupila' ni 'paciente')."""
    rng = random.Random(semilla)
    acciones = {}
    for t in range(1, n + 1):
        s = rng.sample(_SUSTANTIVOS, 5 if largos and t % 2 else 3)
        a = rng.choice(_ADJ)
        acciones[t] = (f'"Voy a mirar."\n\nMe acerco a la {s[0]} {a} y examino el {s[1]} junto al {s[2]}'
                       + (f", la {s[3]} y el {s[4]}" if len(s) > 3 else "") + ".\n\n{Investigación}")
    return ra.PoolAcciones.desde_textos("camp-prueba", acciones)


# ---- clasificación de la acción
@pytest.mark.parametrize("texto,clase", [
    ("{Percepción}", "solo_tag"),
    ("", "solo_tag"),
    ("  {Sigilo}  ", "solo_tag"),
    ('"Tranquilos, no os dejéis llevar por el miedo."\n\n{Persuasión}', "solo_dialogo"),
    ('«Tranquilos, no os dejéis llevar por el miedo.»\n\n{Persuasión}', "solo_dialogo"),
    ("— No te preocupes, estoy aquí.\n{Persuasión}", "solo_dialogo"),
    ("Me acerco al paciente y le tomo el pulso.\n\n{Medicina}", "accion"),
    ('"Tranquilo."\n\nMe acerco al paciente y le tomo el pulso.\n\n{Medicina}', "mixta"),
])
def test_clasificar_accion(ra, texto, clase):
    assert ra.clasificar_accion(texto) == clase


def test_texto_accion_une_las_entradas_del_buffer_y_quita_las_etiquetas(ra):
    buf = [{"pc": "PJ17", "text": "Abro la puerta.\n\n{Atletismo}"}]
    assert ra.texto_accion(buf) == "Abro la puerta."
    assert ra.texto_accion("Abro la puerta.\n{Sigilo}") == "Abro la puerta."
    assert ra.texto_accion([]) == ""


def test_lemas_accion_de_una_accion_mixta_incluye_dialogo_y_prosa(ra):
    ls, clase = ra.lemas_accion(ACCION_PULSO)
    assert clase == "mixta"
    assert {"paciente", "pulso", "pupila", "dejar"} <= ls
    assert "medicina" not in ls           # la etiqueta de tirada no cuenta


# ---- coeficiente de Ochiai
def test_ochiai_valores_conocidos(ra):
    assert ra.ochiai(frozenset("abc"), frozenset("bcd")) == pytest.approx(2 / 3)
    assert ra.ochiai(frozenset("ab"), frozenset("ab")) == pytest.approx(1.0)
    assert ra.ochiai(frozenset("ab"), frozenset("cd")) == 0.0
    assert ra.ochiai(frozenset(), frozenset("ab")) == 0.0


def test_ochiai_normaliza_por_longitud(ra):
    corto = ra.ochiai(frozenset("ab"), frozenset("abcd"))
    largo = ra.ochiai(frozenset("ab"), frozenset("abcdefgh"))
    assert corto > largo


# ---- casos no computables
def test_accion_solo_tag_no_es_computable(ra):
    pool = _pool(ra)
    r = ra.medir(pool, 50, RESP_PULSO, accion="{Percepción}")
    assert r["clase"] == "solo_tag" and r["z"] is None and r["crudo"] is None


def test_accion_con_menos_de_3_lemas_es_insuficiente(ra):
    pool = _pool(ra)
    r = ra.medir(pool, 50, RESP_PULSO, accion="Abro.\n{Atletismo}")
    assert r["clase"] == "insuficiente" and r["z"] is None


def test_respuesta_con_menos_de_3_lemas_es_insuficiente(ra):
    pool = _pool(ra)
    r = ra.medir(pool, 50, "Sí.", accion=ACCION_PULSO)
    assert r["z"] is None and r["clase"] == "insuficiente"


def test_accion_solo_dialogo_se_calcula_y_se_marca(ra):
    pool = _pool(ra)
    r = ra.medir(pool, 50, RESP_PULSO, accion='"Sostén el pulso del paciente, mira sus pupilas."\n{Medicina}')
    assert r["clase"] == "solo_dialogo" and r["z"] is not None and r["z"] > 0


# ---- nulo por permutación
def test_el_nulo_excluye_el_turno_y_sus_vecinos(ra):
    pool = _pool(ra)
    cand = ra.candidatos_nulo(pool, 60, n_lemas=6)
    assert 60 not in cand and all(abs(x - 60) > 2 for x in cand)
    assert cand, "el nulo no puede quedar vacío"


def test_el_nulo_empareja_por_longitud(ra):
    pool = _pool(ra, n=200, largos=True)
    largo = next(t for t in pool.turnos if len(pool.lemas[t]) >= 9)
    cand = ra.candidatos_nulo(pool, 1, n_lemas=len(pool.lemas[largo]))
    medias = sum(len(pool.lemas[x]) for x in cand) / len(cand)
    assert abs(medias - len(pool.lemas[largo])) <= 2


def test_el_nulo_es_determinista(ra):
    pool = _pool(ra)
    assert ra.candidatos_nulo(pool, 40, n_lemas=7) == ra.candidatos_nulo(pool, 40, n_lemas=7)


# ---- puntaje
def test_la_respuesta_propia_puntua_mas_que_una_ajena(ra):
    pool = _pool(ra)
    propia = ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO)
    ajena = ra.medir(pool, 50, RESP_BARCO, accion=ACCION_PULSO)
    assert propia["z"] > 1.5 > ajena["z"]
    assert propia["crudo"] > ajena["crudo"]
    assert propia["percentil"] > 0.9


def test_p_de_permutacion_nunca_es_cero_y_sigue_la_formula(ra):
    pool = _pool(ra)
    r = ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO)
    m = r["n_nulo"]
    assert 0 < r["p_perm"] <= 1
    assert r["p_perm"] >= 1 / (1 + m)


def test_el_z_usa_un_piso_de_sd_si_el_nulo_es_degenerado(ra):
    pool = _pool(ra)
    # respuesta sin ningún lema en común con el pool: nulo todo ceros
    r = ra.medir(pool, 50, "El dragón duerme sobre montañas de oro brillante junto a esmeraldas.",
                 accion="Me acerco al dragón y admiro su tesoro dorado con asombro.\n{Percepción}")
    assert r["z"] is not None and abs(r["z"]) < 100


def test_medir_es_determinista(ra):
    pool = _pool(ra)
    assert ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO) == ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO)


def test_el_formato_g1_no_cambia_el_puntaje(ra):
    pool = _pool(ra)
    g1 = f"narrativa\n{RESP_PULSO}\n\nmecanica\nMedicina: Éxito (17 vs CD 15).\n\npresion\n"
    a = ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO)
    b = ra.medir(pool, 50, g1, accion=ACCION_PULSO)
    assert (a["crudo"], a["z"]) == (b["crudo"], b["z"])


def test_reordenar_oraciones_no_cambia_el_crudo(ra):
    pool = _pool(ra)
    oraciones = RESP_PULSO.split(". ")
    inv = ". ".join(reversed(oraciones))
    a = ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO)["crudo"]
    b = ra.medir(pool, 50, inv, accion=ACCION_PULSO)["crudo"]
    assert a == pytest.approx(b, abs=0.05)


# ---- ventana
def test_ventana_es_la_media_de_los_z_de_sus_turnos(ra):
    pool = _pool(ra, n=60)
    pool.agregar_turno(61, ACCION_PULSO)
    z = ra.medir_ventana(pool, 61, [RESP_PULSO])
    assert z == pytest.approx(ra.medir(pool, 61, RESP_PULSO)["z"])


def test_ventana_desalineada_puntua_menos_que_alineada(ra):
    pool = _pool(ra, n=60)
    acc = {70: ('"Voy a ver."\n\nMe acerco al paciente y le tomo el pulso.\n{Medicina}', RESP_PULSO),
           71: ('"Cuidado."\n\nAbro la puerta del barco y agarro el timón con fuerza.\n{Atletismo}', RESP_BARCO)}
    for t, (a, _) in acc.items():
        pool.agregar_turno(t, a)
    alineada = ra.medir_ventana(pool, 70, [acc[70][1], acc[71][1]])
    cruzada = ra.medir_ventana(pool, 70, [acc[71][1], acc[70][1]])
    assert alineada > cruzada


def test_ventana_sin_turnos_computables_da_none(ra):
    pool = _pool(ra, n=60)
    pool.agregar_turno(80, "{Percepción}")
    assert ra.medir_ventana(pool, 80, [RESP_PULSO]) is None


# ---- enchufe al arnés
def test_registro_en_el_arnes_y_calculo_con_contexto(ra):
    import instrumentos_texto as it
    import contexto_a4bc as cx
    nuevos = ra.registrar_en_arnes()
    try:
        assert set(nuevos) == {"cr2a_z", "cr2a_crudo", "cr2a_z_ventana8"}
        assert it.INSTRUMENTOS["cr2a_z"].ambito == "turno" and it.INSTRUMENTOS["cr2a_z_ventana8"].ambito == "ventana"
        assert ra.registrar_en_arnes() == nuevos            # idempotente
        pool = _pool(ra)
        pool.agregar_turno(200, ACCION_PULSO)
        ctx = cx.crear(pool=pool, turno=200)
        v = it.calcular(RESP_PULSO, ctx, nombres=["cr2a_z", "cr2a_crudo"])
        assert v["cr2a_z"] > 1.5 and 0 < v["cr2a_crudo"] <= 1
        vv = it.calcular_ventana([RESP_PULSO], ctx, nombres=["cr2a_z_ventana8"])
        assert vv["cr2a_z_ventana8"] == pytest.approx(v["cr2a_z"])
        # la copia del contexto (como hacen las perturbaciones) conserva pool y turno
        assert ctx.copia(hp_current=3).pool is pool
    finally:
        for n in nuevos:
            it.INSTRUMENTOS.pop(n, None)


# ---- medir con tokens ya lematizados (usado por el corredor para no relematizar 58 800 turnos)
def test_medir_con_tokens_de_la_respuesta_da_lo_mismo_que_con_el_texto(ra):
    import lemas_es as le
    pool = _pool(ra)
    a = ra.medir(pool, 50, RESP_PULSO, accion=ACCION_PULSO)
    b = ra.medir(pool, 50, None, accion=ACCION_PULSO, tokens_respuesta=le.tokens(RESP_PULSO))
    assert a == b
