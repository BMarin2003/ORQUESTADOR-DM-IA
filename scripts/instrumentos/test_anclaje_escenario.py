"""
Pruebas de anclaje_escenario.py (CR-2b). Escritas ANTES que el módulo.

    PYTHONUTF8=1 py -m pytest scripts/instrumentos/test_anclaje_escenario.py -q -p no:cacheprovider
"""
import math
import random
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "scripts" / "sensibilidad"))


@pytest.fixture(scope="module")
def ae():
    import anclaje_escenario
    return anclaje_escenario


@pytest.fixture(scope="module")
def le():
    import lemas_es
    return lemas_es


# ---- escenarios de juguete (escritos a mano)
LORE_PLAGA = ("Bruma Honda se asienta junto a una ciénaga y la niebla sube del agua cada noche. Un cansancio "
              "extraño enferma a los vecinos, que duermen agotados y pierden el apetito. Herminda Coz cuida a "
              "los enfermos en la Casa de Cuarentena, un antiguo granero.")
LORE_BARCO = ("El puerto de Sal Amarga huele a brea. El capitán Zúñiga zarpa con un barco cargado de sal mientras "
              "las olas golpean el casco y el timonel vigila el horizonte y las gaviotas.")
LORE_DRAGON = ("El Valle de los Tres Molinos paga tributo a un dragón contable. Matilde Harinosa, molinera mayor, "
               "discute con las escamas rojas del dragón sobre sacos de harina y citaciones.")

WORLD_PLAGA = {"locations": [{"key": "bruma", "name": "Bruma Honda", "description_canonical":
                              "Un pueblo en una hondonada baja junto a una ciénaga.", "kind": "settlement"},
                             {"key": "casa", "name": "La Casa de Cuarentena", "sketch_text":
                              "Un antiguo granero con catres separados por cortinas de lino."}],
               "factions": [{"key": "consejo", "name": "El Consejo Sanador", "description":
                             "Los ayudantes de Herminda sostienen un aislamiento estricto.", "seat": "casa"}],
               "quests": [{"key": "q", "title": "El cansancio que no cede", "description":
                           "Un mal desconocido se extiende por el pueblo sin remedio conocido."}],
               "clocks": [{"faction": "consejo", "agenda": "El brote crece más rápido que la cuarentena."}],
               "characters": [{"key": "pj", "name": "Garrek", "class": "clérigo 3", "hp": 24}]}
PERSONAS_PLAGA = {"_nota": "NOTA-DE-AUTORIA-NO-DEBE-APARECER",
                  "herminda": {"_arquetipo": "ARQUETIPO-OCULTO", "name": "Herminda Coz", "species": "humana",
                               "social_role": "curandera de Bruma Honda", "appearance": "Manos agrietadas y un paño al hombro.",
                               "traits": ["revisa cada catre antes de dormir"], "taboos": ["dejar entrar a un familiar"],
                               "internal_contradiction": "Sostiene el aislamiento y duda de él.",
                               "voice_notes": "VOZ-OCULTA", "secrets": ["SECRETO-OCULTO"], "knowledge": ["SABER-OCULTO"]}}


@pytest.fixture(scope="module")
def mundo(ae, le):
    """3 escenarios y un modelo idf construido con narraciones de juguete de 3 'campañas'."""
    esc = {
        "P": ae.Escenario.de_fixtures("P", LORE_PLAGA, WORLD_PLAGA, PERSONAS_PLAGA),
        "B": ae.Escenario.de_textos("B", LORE_BARCO, ["Sal Amarga", "Capitán Zúñiga"]),
        "D": ae.Escenario.de_textos("D", LORE_DRAGON, ["Tres Molinos", "Matilde Harinosa"]),
    }
    narr = {
        "P": ["La niebla cubre la ciénaga y los enfermos duermen agotados en los catres del granero.",
              "Herminda revisa cada catre con las manos agrietadas mientras el cansancio avanza.",
              "Sientes la mirada de un vecino que pierde el apetito. La sombra de la puerta se alarga."],
        "B": ["El casco cruje cuando las olas golpean el barco y el timonel aprieta el timón.",
              "El capitán ordena arriar las velas mientras el horizonte se oscurece.",
              "Sientes la mirada del marinero. La sombra del mástil se alarga sobre la cubierta."],
        "D": ["El dragón revisa los sacos de harina y discute con la molinera sobre las citaciones.",
              "Las escamas rojas brillan sobre la harina mientras el molino gira en la colina.",
              "Sientes la mirada del contable. La sombra del molino se alarga sobre el valle."],
    }
    camps = [{"nombres": esc[p].nombres_lemas, "turnos": [le.tokens(t) for t in narr[p]]} for p in "PBD"]
    modelo = ae.ModeloAnclaje.desde_campanas(camps)
    return {"esc": esc, "modelo": modelo, "narr": narr}


# ---- referencia del escenario
def test_nombres_del_escenario_incluyen_lugares_facciones_pnj_y_pj(ae):
    n = ae.nombres_escenario(WORLD_PLAGA, PERSONAS_PLAGA)
    assert {"Bruma Honda", "La Casa de Cuarentena", "El Consejo Sanador", "Herminda Coz", "Garrek"} <= set(n)
    assert "El cansancio que no cede" not in n        # el título de una misión no es un nombre propio


def test_texto_referencia_lleva_lore_y_descripciones_pero_no_campos_ocultos(ae):
    t = ae.texto_referencia(LORE_PLAGA, WORLD_PLAGA, PERSONAS_PLAGA)
    for debe in ("ciénaga", "granero", "catres", "aislamiento estricto", "cansancio", "curandera", "Manos agrietadas",
                 "revisa cada catre", "dejar entrar", "brote crece"):
        assert debe in t, debe
    for no_debe in ("NOTA-DE-AUTORIA", "ARQUETIPO-OCULTO", "VOZ-OCULTA", "SECRETO-OCULTO", "SABER-OCULTO"):
        assert no_debe not in t, no_debe


def test_lemas_de_nombres_incluyen_las_palabras_de_los_nombres(ae):
    ls = ae.lemas_nombres(["Herminda Coz", "La Casa de Cuarentena", "Bruma Honda"])
    assert {"herminda", "coz", "casa", "cuarentena", "bruma", "honda"} <= ls


def test_fixtures_reales_se_cargan_para_los_21_pares(ae):
    for par in ("09", "20", "27"):
        w, p = ae.cargar_fixtures(par)
        assert w["locations"] and p
        assert ae.nombres_escenario(w, p)


# ---- idf
def test_idf_pesa_menos_los_terminos_comunes_a_todas_las_campanas(mundo):
    m = mundo["modelo"]
    assert m.n_docs == 3
    assert m.idf("con", "mirada") == pytest.approx(1.0)                         # aparece en las 3
    assert m.idf("con", "niebla") == pytest.approx(math.log(4 / 2) + 1)          # aparece en 1 de 3
    assert m.idf("con", "termino_inexistente") == pytest.approx(math.log(4 / 1) + 1)
    assert m.idf("con", "niebla") > m.idf("con", "mirada")


# ---- coseno
def test_coseno_de_un_texto_con_su_propia_referencia_es_mayor_que_con_las_ajenas(ae, mundo, le):
    for p in "PBD":
        toks = [le.tokens(mundo["narr"][p][0])]
        cos = {q: ae.cos_tokens(mundo["modelo"], mundo["esc"][q], toks, "con") for q in "PBD"}
        assert max(cos, key=cos.get) == p, (p, cos)


def test_identificar_devuelve_el_escenario_de_mayor_coseno(ae, mundo, le):
    toks = [le.tokens(mundo["narr"]["D"][1])]
    mejor, cos = ae.identificar(mundo["modelo"], mundo["esc"], toks, "con")
    assert mejor == "D" and cos["D"] == max(cos.values())


def test_coseno_vacio_o_sin_terminos_de_referencia_es_cero(ae, mundo, le):
    assert ae.cos_turno(mundo["modelo"], mundo["esc"]["P"], "", "con") == 0.0
    assert ae.cos_turno(mundo["modelo"], mundo["esc"]["P"], "El vuelo del avión supersónico cruza el desierto.", "con") == 0.0


def test_coseno_esta_entre_0_y_1_y_un_texto_identico_a_la_referencia_da_1(ae, mundo, le):
    toks = [le.tokens(LORE_PLAGA + " " + "Garrek llega.")]
    c = ae.cos_tokens(mundo["modelo"], mundo["esc"]["P"], [le.tokens(LORE_PLAGA)], "con")
    assert 0.0 < c <= 1.0
    e = mundo["esc"]["P"]
    assert ae.cos_tokens(mundo["modelo"], e, [e.tokens_ref], "con") == pytest.approx(1.0)


def test_el_coseno_no_depende_del_formato_g1(ae, mundo):
    t = mundo["narr"]["P"][0]
    g1 = f"narrativa\n{t}\n\nmecanica\nMedicina: Éxito (17 vs CD 15).\n\npresion\n"
    e, m = mundo["esc"]["P"], mundo["modelo"]
    assert ae.cos_turno(m, e, g1, "con") == ae.cos_turno(m, e, t, "con")
    assert ae.cos_turno(m, e, g1, "sn") == ae.cos_turno(m, e, t, "sn")


# ---- variante sin nombres
def test_sn_ignora_los_nombres_del_escenario_y_los_nombres_propios(ae, mundo):
    m, e = mundo["modelo"], mundo["esc"]["P"]
    solo_nombres = "Herminda Coz espera en Bruma Honda, en la Casa de Cuarentena."
    assert ae.cos_turno(m, e, solo_nombres, "con") > 0.1
    assert ae.cos_turno(m, e, solo_nombres, "sn") < ae.cos_turno(m, e, solo_nombres, "con") * 0.5


def test_sn_sigue_reconociendo_el_lexico_del_escenario(ae, mundo):
    m, e = mundo["modelo"], mundo["esc"]["P"]
    t = "La niebla cubre la ciénaga y los enfermos duermen agotados entre los catres."
    assert ae.cos_turno(m, e, t, "sn") > 0.15


def test_un_nombre_inventado_baja_el_coseno_con_nombres_y_no_el_sn(ae, mundo):
    m, e = mundo["modelo"], mundo["esc"]["P"]
    t = "La niebla cubre la ciénaga y los enfermos duermen agotados entre los catres."
    t2 = "Al fondo alguien murmura el nombre de Zorevthek y luego el de Braxmora. " + t
    assert ae.cos_turno(m, e, t2, "con") < ae.cos_turno(m, e, t, "con")
    assert ae.cos_turno(m, e, t2, "sn") == pytest.approx(ae.cos_turno(m, e, t, "sn"), abs=0.02)


# ---- ventana de 8 turnos
def test_ventana_es_invariante_al_orden_de_los_turnos(ae, mundo):
    m, e = mundo["modelo"], mundo["esc"]["P"]
    textos = mundo["narr"]["P"] + mundo["narr"]["B"][:2]
    baraja = textos[:]
    random.Random(1).shuffle(baraja)
    assert baraja != textos
    for v in ("con", "sn"):
        assert ae.cos_ventana(m, e, textos, v) == ae.cos_ventana(m, e, baraja, v)


def test_ventana_ajena_puntua_menos_que_ventana_propia(ae, mundo):
    m, e = mundo["modelo"], mundo["esc"]["P"]
    assert ae.cos_ventana(m, e, mundo["narr"]["P"], "con") > ae.cos_ventana(m, e, mundo["narr"]["B"], "con")


def test_ventana_rodante_devuelve_un_valor_por_turno_con_8_turnos_previos(ae, mundo, le):
    toks = [le.tokens(t) for t in (mundo["narr"]["P"] * 4)]          # 12 turnos
    ser = ae.serie_rodante(mundo["modelo"], mundo["esc"]["P"], toks, "con", k=8)
    assert len(ser) == 12 - 8 + 1
    assert all(0 <= x <= 1 for x in ser)


# ---- enchufe al arnés
def test_registro_en_el_arnes_y_calculo_con_contexto(ae, mundo):
    import instrumentos_texto as it
    import contexto_a4bc as cx
    nuevos = ae.registrar_en_arnes()
    try:
        assert set(nuevos) == {"cr2b_cos_turno", "cr2b_cos_turno_sn", "cr2b_cos_ventana8", "cr2b_cos_ventana8_sn"}
        assert it.INSTRUMENTOS["cr2b_cos_ventana8"].ambito == "ventana"
        assert it.INSTRUMENTOS["cr2b_cos_turno"].ambito == "turno"
        assert ae.registrar_en_arnes() == nuevos
        ctx = cx.crear(escenario=mundo["esc"]["P"], modelo=mundo["modelo"])
        v = it.calcular(mundo["narr"]["P"][0], ctx, nombres=["cr2b_cos_turno", "cr2b_cos_turno_sn"])
        assert v["cr2b_cos_turno"] == ae.cos_turno(mundo["modelo"], mundo["esc"]["P"], mundo["narr"]["P"][0], "con")
        w = it.calcular_ventana(mundo["narr"]["P"], ctx, nombres=["cr2b_cos_ventana8"])
        assert w["cr2b_cos_ventana8"] == ae.cos_ventana(mundo["modelo"], mundo["esc"]["P"], mundo["narr"]["P"], "con")
        assert ctx.copia(hp_current=1).escenario is mundo["esc"]["P"]
    finally:
        for n in nuevos:
            it.INSTRUMENTOS.pop(n, None)
