"""
Pruebas unitarias del arnés de sensibilidad por perturbación (TDD: este
archivo se escribió ANTES que instrumentos_texto.py / perturbaciones.py /
correr_sensibilidad.py).

    PYTHONUTF8=1 py -m pytest scripts/sensibilidad/test_sensibilidad.py -q -p no:cacheprovider

Bloques:
  A. instrumentos_texto: los envoltorios reproducen la lógica de
     vertical_slice.py / reporte_validacion.py sobre texto arbitrario.
  B. perturbaciones: cada perturbación es determinista con semilla, solo
     cambia lo previsto y no muta el original.
  C. estadística de correr_sensibilidad (Wilson, McNemar, Cliff, Holm...).
"""
import ast
import copy
import inspect
import random
import re
import sys
import textwrap
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "orquestador"))
sys.path.insert(0, str(RAIZ / "scripts"))


# ======================================================================
# A. instrumentos_texto
# ======================================================================
@pytest.fixture
def it():
    import instrumentos_texto
    return instrumentos_texto


def _ctx(it, **kw):
    base = dict(
        pj_nombre="Ilvard",
        entidades=[{"tipo": "character", "nombre": "Ilvard"},
                   {"tipo": "npc", "nombre": "Kael"},
                   {"tipo": "npc", "nombre": "Sargento Brea"},
                   {"tipo": "location", "nombre": "Torre Alondra"}],
        estados_pnj={"Kael": "alive", "Sargento Brea": "alive"},
        hp_current=20, hp_max=24, tiradas=[], escena_anterior="")
    base.update(kw)
    return it.Contexto(**base)


# ---- registro ---------------------------------------------------------
def test_registrar_instrumento_y_calcularlo(it):
    it.registrar_instrumento("_prueba_longitud", lambda texto, ctx: len(texto), "num")
    try:
        r = it.calcular("hola", _ctx(it), nombres=["_prueba_longitud"])
        assert r == {"_prueba_longitud": 4}
    finally:
        it.INSTRUMENTOS.pop("_prueba_longitud", None)


def test_registrar_instrumento_rechaza_tipo_invalido_y_duplicados(it):
    with pytest.raises(ValueError):
        it.registrar_instrumento("_x", lambda t, c: 1, "texto")
    with pytest.raises(ValueError):
        it.registrar_instrumento("qn1_ttr", lambda t, c: 1, "num")   # ya existe


def test_catalogo_incluye_los_instrumentos_de_turn_validation(it):
    esperados = {"cr1_veredicto_contradice_narracion", "qn2_pj_piensa_narrado",
                 "qn2_pj_accion_revisar", "cl2_pnj_inactivo_actua",
                 "cl2_pc_hp_contradice_narracion", "cr2_nombres_no_reconocidos",
                 "meta_comentario", "comenta_reglas", "cl2_lugar_jaccard_similarity",
                 "qn1_ttr", "qn1_ngram_repeticion", "qn1_legibilidad_fh",
                 "cr2_entidad_grafo_densidad"}
    assert esperados <= set(it.INSTRUMENTOS)


# ---- booleanos ----------------------------------------------------------
def test_qn2_pj_piensa_narrado_solo_3a_persona_con_nombre(it):
    c = _ctx(it)
    assert it.calcular("Ilvard decide entregar la llave.", c)["qn2_pj_piensa_narrado"] is True
    assert it.calcular("ilvard siente miedo.", c)["qn2_pj_piensa_narrado"] is True    # re.I
    # fidelidad al detector actual: en 2.ª persona NO se dispara (el fallo que motiva el arnés)
    assert it.calcular("Decides entregar la llave. Sientes miedo.", c)["qn2_pj_piensa_narrado"] is False


def test_qn2_pj_accion_revisar_solo_sin_tiradas(it):
    assert it.calcular("Ilvard ataca al guardia.", _ctx(it))["qn2_pj_accion_revisar"] is True
    c = _ctx(it, tiradas=[{"etiqueta": "Ataque", "dado": 12, "pifia": False, "critico": False}])
    assert it.calcular("Ilvard ataca al guardia.", c)["qn2_pj_accion_revisar"] is False


def test_cl2_pnj_inactivo_actua_usa_estado_del_contexto(it):
    c_muerto = _ctx(it, estados_pnj={"Kael": "dead", "Sargento Brea": "alive"})
    assert it.calcular("Kael desenvaina la espada.", c_muerto)["cl2_pnj_inactivo_actua"] is True
    assert it.calcular("Kael desenvaina la espada.", _ctx(it))["cl2_pnj_inactivo_actua"] is False


def test_cl2_pnj_inactivo_actua_ignora_pj_y_entidades_no_npc(it):
    # el PJ nunca cuenta como PNJ inactivo, aunque figure como npc con otro estado
    c_pj = _ctx(it, estados_pnj={"Ilvard": "dead"},
                entidades=[{"tipo": "npc", "nombre": "Ilvard"}])
    assert it.calcular("Ilvard camina.", c_pj)["cl2_pnj_inactivo_actua"] is False
    c = _ctx(it, estados_pnj={"Torre Alondra": "dead"})
    assert it.calcular("Torre Alondra se alza.", c)["cl2_pnj_inactivo_actua"] is False


def test_cl2_pc_hp_contradice_solo_con_hp_mayor_que_cero(it):
    assert it.calcular("Ilvard muere en el suelo.", _ctx(it))["cl2_pc_hp_contradice_narracion"] is True
    assert it.calcular("Ilvard muere en el suelo.", _ctx(it, hp_current=0))["cl2_pc_hp_contradice_narracion"] is False
    assert it.calcular("Ilvard muere en el suelo.", _ctx(it, hp_current=None))["cl2_pc_hp_contradice_narracion"] is False
    assert it.calcular("Mueres en el suelo.", _ctx(it))["cl2_pc_hp_contradice_narracion"] is False   # 2.ª persona: ciego


def test_cr1_pifia_con_exito_narrado(it):
    pifia = {"etiqueta": "Percepción", "dado": 1, "pifia": True, "critico": False}
    normal = {"etiqueta": "Percepción", "dado": 9, "pifia": False, "critico": False}
    assert it.calcular("Logras abrir la puerta.", _ctx(it, tiradas=[pifia]))["cr1_veredicto_contradice_narracion"] is True
    assert it.calcular("Logras abrir la puerta.", _ctx(it, tiradas=[normal]))["cr1_veredicto_contradice_narracion"] is False
    assert it.calcular("La puerta no cede.", _ctx(it, tiradas=[pifia]))["cr1_veredicto_contradice_narracion"] is False


def test_meta_comentario_y_comenta_reglas(it):
    c = _ctx(it)
    assert it.calcular("Todo sigue. [Tirada de Percepción necesaria para ver esto]", c)["meta_comentario"] is True
    assert it.calcular("Todo sigue. [corto]", c)["meta_comentario"] is False
    assert it.calcular("Como DM, resuelvo la reacción.", c)["comenta_reglas"] is True
    assert it.calcular("Nada de reglas aquí.", c)["comenta_reglas"] is False


def test_cr2_nombres_no_reconocidos_reglas_de_capitalizacion(it):
    c = _ctx(it)
    assert it.nombres_no_reconocidos("Vimos llegar a Zorvanthek ayer.", c) == ["Zorvanthek"]
    assert it.nombres_no_reconocidos("Vimos llegar a Kael ayer.", c) == []            # entidad conocida
    assert it.nombres_no_reconocidos("Zorvanthek llegó ayer.", c) == []              # inicio de texto se ignora
    assert it.nombres_no_reconocidos("Se fue. Zorvanthek llegó.", c) == []           # tras punto se ignora
    assert it.nombres_no_reconocidos("Vimos a El Zorvanthek.", c) == ["Zorvanthek"]  # 'El' en STOP_MAYUS
    assert it.calcular("Vimos llegar a Zorvanthek ayer.", c)["cr2_nombres_no_reconocidos"] is True
    assert it.calcular("Vimos llegar a Kael ayer.", c)["cr2_nombres_no_reconocidos"] is False


# ---- numéricos ------------------------------------------------------------
def test_ttr_y_ngram_valores_exactos(it):
    c = _ctx(it)
    r = it.calcular("El perro y el gato", c)
    assert r["qn1_ttr"] == pytest.approx(0.8)
    assert r["qn1_ngram_repeticion"] == pytest.approx(0.0)
    r = it.calcular("la casa la casa la casa", c)
    assert r["qn1_ttr"] == pytest.approx(0.333)
    assert r["qn1_ngram_repeticion"] == pytest.approx(0.6)


def test_jaccard_contra_escena_anterior(it):
    c = _ctx(it, escena_anterior="el perro corre")
    assert it.calcular("el gato corre", c)["cl2_lugar_jaccard_similarity"] == pytest.approx(0.5)


def test_entidad_grafo_densidad_valor_exacto(it):
    c = _ctx(it)
    assert it.calcular("Kael entra. Brea sonríe. Kael sale.", c)["cr2_entidad_grafo_densidad"] == pytest.approx(0.333)
    assert it.calcular("Solo una frase.", c)["cr2_entidad_grafo_densidad"] is None


def test_fernandez_huerta_coincide_con_la_funcion_original(it):
    import vertical_slice as vs
    t = "El guardia cierra la puerta. Nadie dice una palabra durante un largo rato."
    assert it.calcular(t, _ctx(it))["qn1_legibilidad_fh"] == vs.fernandez_huerta(t)


# ---- guardas de deriva: el código replicado sigue igual que el original -----
FUENTES = [RAIZ / "orquestador" / "vertical_slice.py", RAIZ / "orquestador" / "vertical_slice_g1.py"]


@pytest.mark.parametrize("ruta", FUENTES, ids=lambda p: p.name)
def test_los_patrones_replicados_siguen_en_el_original(it, ruta):
    fuente = ruta.read_text(encoding="utf-8")
    for patron in it.PATRONES_REPLICADOS:
        assert patron in fuente, f"el patrón replicado ya no está en {ruta.name}: {patron!r}"


def test_las_funciones_importadas_son_iguales_en_g2_y_g1():
    import vertical_slice as g2
    import vertical_slice_g1 as g1

    def norm(f):
        arbol = ast.parse(textwrap.dedent(inspect.getsource(f)))
        for n in ast.walk(arbol):
            if isinstance(n, ast.FunctionDef) and ast.get_docstring(n):
                n.body = n.body[1:]
        return ast.dump(arbol)
    for nombre in ("jaccard_palabras", "contar_silabas_es", "fernandez_huerta",
                   "entidades_conocidas", "entidad_grafo_densidad"):
        assert norm(getattr(g2, nombre)) == norm(getattr(g1, nombre)), nombre


# ---- post-hoc de reporte_validacion --------------------------------------
def test_entity_coreference_por_turno_equivale_a_la_funcion_de_campana(it):
    import reporte_validacion as rv
    ents = [{"tipo": "npc", "nombre": "Kael"}, {"tipo": "npc", "nombre": "Sargento Brea"}]
    textos = ["Kael llega.", "Kael habla con Brea.", "Brea calla.", "Nadie."]
    ref = rv.entity_coreference_rate(
        [{"turn_id": i, "dm_output": t} for i, t in enumerate(textos)], ents)["por_turno"]
    previas = set()
    obtenido = []
    for i, t in enumerate(textos):
        c = _ctx(it, entidades=ents, previas=frozenset(previas))
        v = it.calcular(t, c, nombres=["entity_coreference_rate"])["entity_coreference_rate"]
        if v is not None:
            obtenido.append((i, v))
        previas |= it.entidades_mencionadas(t, ents)
    assert obtenido == [(x["turn_id"], x["tasa"]) for x in ref]


# ---- ventanas ---------------------------------------------------------------
def test_refinado_solo_ve_pnj_de_una_palabra_como_sujeto_limitacion_heredada(it):
    # reporte_validacion.pnj_inactivo_refinado compara `nombre in tok.text` (un token):
    # los nombres de varias palabras («Sargento Brea») nunca cuentan como sujeto.
    ctx = _ctx(it, estados_pnj={"Kael": "dead", "Sargento Brea": "dead"})
    assert it.calcular("Kael desenvaina la espada y avanza hacia ti.", ctx,
                       nombres=["cl2_pnj_inactivo_refinado"])["cl2_pnj_inactivo_refinado"] is True
    assert it.calcular("Sargento Brea desenvaina la espada y avanza hacia ti.", ctx,
                       nombres=["cl2_pnj_inactivo_refinado"])["cl2_pnj_inactivo_refinado"] is False
    assert it.calcular("Todo está en calma.", ctx, nombres=["cl2_pnj_inactivo_refinado"])["cl2_pnj_inactivo_refinado"] is False


def test_ventana_V_es_invariante_al_orden_y_jaccard_medio_no(it):
    ents = [{"tipo": "npc", "nombre": "Kael"}, {"tipo": "location", "nombre": "Torre Alondra"}]
    textos = ["Kael corre hacia la torre.", "Kael abre la puerta de Torre Alondra.",
              "La lluvia cae sobre Torre Alondra.", "Kael espera en silencio.",
              "Kael vigila la calle desierta."]
    c = _ctx(it, entidades=ents, escena_anterior="Kael llega a la ciudad.")
    a = it.calcular_ventana(textos, c)
    permutada = [textos[i] for i in (2, 0, 4, 1, 3)]
    b = it.calcular_ventana(permutada, c)
    assert a["ventana_consistencia_V"] == b["ventana_consistencia_V"]
    assert a["ventana_jaccard_medio"] != b["ventana_jaccard_medio"]


# ======================================================================
# B. perturbaciones
# ======================================================================
@pytest.fixture
def pt():
    import perturbaciones
    return perturbaciones


G2_TEXTO = (
    "Te acercas a la columna y clavas la vista en la moldura desplazada. El ángulo es "
    "incómodo y las sombras del techo juegan contigo.\n\n"
    "Kael, el conserje, aparece al fondo del pasillo con un manojo de llaves. No dice nada, "
    "pero su mirada se detiene en la puerta del archivo. Sargento Brea tose con fuerza.\n\n"
    "Desde el patio llega el rumor de una campana que da la hora según su humor. Nadie parece "
    "tener prisa por llegar a ninguna parte. La lluvia repica contra los cristales de la "
    "Torre Alondra y el viento arrastra hojas secas por el suelo.")

G1_TEXTO = ("narrativa\n" + G2_TEXTO + "\n\nmecanica\nPercepción: Éxito (17 vs CD 12). "
            "Notas lo suficiente.\n\npresion\nEl tiempo se acaba.")

CATEGORIAS = ["decision", "pensamiento", "emocion", "habla", "accion"]
ORACION_2P = {  # oráculo independiente, no importa perturbaciones
    "decision": r"\b(Decides|Resuelves|Eliges|Optas)\b",
    "pensamiento": r"\b(Piensas|Comprendes|Crees|Te dices|Sabes)\b",
    "emocion": r"\b(Sientes|Te invade|Te embarga|Notas cómo)\b",
    "habla": r"\b(dices|respondes|murmuras|susurras|gritas)\b",
    "accion": r"\b(Sacas|Golpeas|Saltas|Derribas|Desarmas|golpeas|derribas)\b",
}


def _rng(n=1):
    return random.Random(n)


def _quitar(nuevo, info):
    return nuevo.replace(info["insertado"], "", 1)


def test_catalogo_de_perturbaciones_completo(pt):
    ids = set(pt.CATALOGO)
    for p in ("P1", "P2"):
        assert {f"{p}_{c}" for c in CATEGORIAS} <= ids
    assert {"P3_dead_actua", "P3_dead_habla", "P3_missing_actua", "P3_missing_habla",
            "P4_2p", "P4_3p", "P5", "P6", "P7", "P8", "P9", "P10",
            "P11a_inyeccion", "P11b_eliminacion", "P12"} <= ids


def test_cada_perturbacion_tiene_direccion_esperada_prespecificada(pt, it):
    validas_bool = {"se_dispara", "sin_cambio"}
    validas_num = {"sube", "baja", "sin_cambio"}
    for pid in pt.CATALOGO:
        assert pt.ESPERADO.get(pid), f"{pid} sin ESPERADO"
        for instr, d in pt.ESPERADO[pid].items():
            assert instr in it.INSTRUMENTOS, f"{pid}: instrumento desconocido {instr}"
            tipo = it.INSTRUMENTOS[instr].tipo
            assert d in (validas_bool if tipo == "bool" else validas_num), (pid, instr, d, tipo)
    assert len(pt.hash_esperado()) == 64


def test_esperado_original_no_ha_cambiado_desde_el_humo(pt):
    # hash de la tabla pre-especificada ANTES de correr nada sobre datos reales (impreso por el humo
    # del 2026-09-20 18:29). Si alguien reescribe una expectativa, esto falla. Las variantes
    # *_accion_sin_tirada se añadieron después del humo y se declaran aparte.
    assert pt.hash_esperado(original=True) == "735308b36bf7e81e00da31e5fca53a193e4415ed7409906ff348c7eb6765a61b"
    assert pt.hash_esperado() != pt.hash_esperado(original=True)
    assert set(pt.POSTERIORES_AL_HUMO) == {"P1_accion_sin_tirada", "P2_accion_sin_tirada"}


def test_esperado_recoge_el_fallo_de_2a_persona(pt):
    # el detector viejo DEBERÍA dispararse ante usurpación en 2.ª persona
    for c in ("decision", "pensamiento", "emocion"):
        assert pt.ESPERADO[f"P1_{c}"]["qn2_pj_piensa_narrado"] == "se_dispara"
        assert pt.ESPERADO[f"P2_{c}"]["qn2_pj_piensa_narrado"] == "se_dispara"
    assert pt.ESPERADO["P1_accion"]["qn2_pj_accion_revisar"] == "se_dispara"
    assert pt.ESPERADO["P4_2p"]["cl2_pc_hp_contradice_narracion"] == "se_dispara"
    assert pt.ESPERADO["P4_3p"]["cl2_pc_hp_contradice_narracion"] == "se_dispara"


def test_registrar_esperado_permite_enchufar_detectores_nuevos(pt, it):
    it.registrar_instrumento("_nuevo_2p", lambda t, c: False, "bool")
    try:
        pt.registrar_esperado("P1_decision", "_nuevo_2p", "se_dispara")
        assert pt.ESPERADO["P1_decision"]["_nuevo_2p"] == "se_dispara"
        with pytest.raises(ValueError):
            pt.registrar_esperado("P1_decision", "_nuevo_2p", "sube")      # dirección inválida para bool
    finally:
        it.INSTRUMENTOS.pop("_nuevo_2p", None)
        pt.ESPERADO["P1_decision"].pop("_nuevo_2p", None)


# ---- P1 / P2: usurpación --------------------------------------------------
@pytest.mark.parametrize("cat", CATEGORIAS)
@pytest.mark.parametrize("texto", [G2_TEXTO, G1_TEXTO], ids=["g2", "g1"])
def test_P1_inserta_una_oracion_en_2a_persona_sin_tocar_lo_demas(pt, it, cat, texto):
    ctx = _ctx(it)
    r = pt.perturbar(f"P1_{cat}", texto, ctx, _rng())
    assert r.texto != texto
    assert _quitar(r.texto, r.info) == texto                      # solo se añadió el fragmento
    assert re.search(ORACION_2P[cat], r.info["insertado"])         # en 2.ª persona y de la categoría
    assert ctx.pj_nombre not in r.info["insertado"]                # nunca en 3.ª persona con nombre
    if texto is G1_TEXTO:
        assert r.texto.split("\nmecanica\n")[1] == texto.split("\nmecanica\n")[1]
        assert r.texto.startswith("narrativa\n")


@pytest.mark.parametrize("cat", CATEGORIAS)
def test_P1_es_ciega_para_el_detector_viejo_de_3a_persona(pt, it, cat):
    ctx = _ctx(it)
    r = pt.perturbar(f"P1_{cat}", G2_TEXTO, ctx, _rng())
    v = it.calcular(r.texto, r.ctx, nombres=["qn2_pj_piensa_narrado", "qn2_pj_accion_revisar",
                                              "cr1_veredicto_contradice_narracion",
                                              "cr2_nombres_no_reconocidos"])
    assert v == {"qn2_pj_piensa_narrado": False, "qn2_pj_accion_revisar": False,
                 "cr1_veredicto_contradice_narracion": False,
                 "cr2_nombres_no_reconocidos": False}


@pytest.mark.parametrize("cat", ["decision", "pensamiento", "emocion"])
def test_P2_dispara_el_detector_viejo_qn2_piensa(pt, it, cat):
    ctx = _ctx(it)
    assert it.calcular(G2_TEXTO, ctx, nombres=["qn2_pj_piensa_narrado"])["qn2_pj_piensa_narrado"] is False
    r = pt.perturbar(f"P2_{cat}", G2_TEXTO, ctx, _rng())
    assert _quitar(r.texto, r.info) == G2_TEXTO
    assert ctx.pj_nombre in r.info["insertado"]
    assert it.calcular(r.texto, r.ctx, nombres=["qn2_pj_piensa_narrado"])["qn2_pj_piensa_narrado"] is True


def test_P2_habla_no_dispara_piensa_y_P2_accion_dispara_revisar_solo_sin_tiradas(pt, it):
    ctx = _ctx(it)
    r = pt.perturbar("P2_habla", G2_TEXTO, ctx, _rng())
    assert ctx.pj_nombre in r.info["insertado"]
    assert it.calcular(r.texto, r.ctx, nombres=["qn2_pj_piensa_narrado"])["qn2_pj_piensa_narrado"] is False
    r = pt.perturbar("P2_accion", G2_TEXTO, ctx, _rng())
    assert it.calcular(r.texto, r.ctx, nombres=["qn2_pj_accion_revisar"])["qn2_pj_accion_revisar"] is True
    con_tirada = _ctx(it, tiradas=[{"etiqueta": "Ataque", "dado": 9, "pifia": False, "critico": False}])
    assert pt.elegible("P2_accion", G2_TEXTO, con_tirada) is False
    assert pt.elegible("P1_accion", G2_TEXTO, con_tirada) is False
    assert pt.elegible("P1_decision", G2_TEXTO, con_tirada) is True


@pytest.mark.parametrize("pid,persona", [("P1_accion_sin_tirada", "2p"), ("P2_accion_sin_tirada", "3p")])
def test_accion_sin_tirada_retira_las_tiradas_del_contexto_perturbado(pt, it, pid, persona):
    # 149 de 150 turnos reales llevan tirada y qn2_pj_accion_revisar solo mira turnos sin ella:
    # estas variantes simulan un turno sin tirada (el contexto original no se toca).
    tirada = {"etiqueta": "Atletismo", "dado": 12, "pifia": False, "critico": False}
    ctx = _ctx(it, tiradas=[tirada])
    assert pt.elegible(pid, G2_TEXTO, ctx) is True
    r = pt.perturbar(pid, G2_TEXTO, ctx, _rng())
    assert _quitar(r.texto, r.info) == G2_TEXTO
    assert r.ctx.tiradas == [] and ctx.tiradas == [tirada] and r.info["tiradas_retiradas"] == 1
    fuego = it.calcular(r.texto, r.ctx, nombres=["qn2_pj_accion_revisar"])["qn2_pj_accion_revisar"]
    assert fuego is (persona == "3p")            # 3.ª persona con nombre: el detector viejo sí; 2.ª: ciego
    assert pt.ESPERADO[pid]["qn2_pj_accion_revisar"] == "se_dispara"


# ---- P3: PNJ inactivo actúa o habla --------------------------------------
@pytest.mark.parametrize("pid,estado", [("P3_dead_actua", "dead"), ("P3_dead_habla", "dead"),
                                        ("P3_missing_actua", "missing"), ("P3_missing_habla", "missing")])
def test_P3_marca_un_pnj_inactivo_y_lo_hace_actuar(pt, it, pid, estado):
    ctx = _ctx(it)
    texto = "Un viento frío recorre la sala vacía. Nadie responde."
    r = pt.perturbar(pid, texto, ctx, _rng())
    nombre = r.info["pnj"]
    assert nombre in ("Kael", "Sargento Brea") and nombre in r.info["insertado"]
    assert _quitar(r.texto, r.info) == texto
    assert r.ctx.estados_pnj[nombre] == estado
    assert ctx.estados_pnj[nombre] == "alive"                       # contexto original intacto
    assert it.calcular(texto, ctx, nombres=["cl2_pnj_inactivo_actua"])["cl2_pnj_inactivo_actua"] is False
    assert it.calcular(r.texto, r.ctx, nombres=["cl2_pnj_inactivo_actua"])["cl2_pnj_inactivo_actua"] is True


def test_P3_no_es_elegible_sin_pnj(pt, it):
    ctx = _ctx(it, entidades=[{"tipo": "character", "nombre": "Ilvard"}], estados_pnj={})
    assert pt.elegible("P3_dead_actua", G2_TEXTO, ctx) is False


# ---- P4: muerte del PJ con HP > 0 -----------------------------------------
def test_P4_3p_dispara_cl2_hp_y_P4_2p_no_usa_el_nombre(pt, it):
    ctx = _ctx(it)
    r3 = pt.perturbar("P4_3p", G2_TEXTO, ctx, _rng())
    assert _quitar(r3.texto, r3.info) == G2_TEXTO
    assert it.calcular(r3.texto, r3.ctx, nombres=["cl2_pc_hp_contradice_narracion"])["cl2_pc_hp_contradice_narracion"] is True
    r2 = pt.perturbar("P4_2p", G2_TEXTO, ctx, _rng())
    assert _quitar(r2.texto, r2.info) == G2_TEXTO
    assert ctx.pj_nombre not in r2.info["insertado"]
    assert re.search(r"\b(Mueres|Caes muerto|Caes muerta|Pierdes la vida|Falleces)\b", r2.info["insertado"])
    assert it.calcular(r2.texto, r2.ctx, nombres=["cl2_pc_hp_contradice_narracion"])["cl2_pc_hp_contradice_narracion"] is False   # ciego en 2.ª persona
    assert r3.ctx.hp_current == ctx.hp_current == 20                  # el HP real no se toca


def test_P4_no_elegible_si_el_pj_ya_esta_a_0_o_sin_hp(pt, it):
    assert pt.elegible("P4_3p", G2_TEXTO, _ctx(it, hp_current=0)) is False
    assert pt.elegible("P4_2p", G2_TEXTO, _ctx(it, hp_current=None)) is False
    assert pt.elegible("P4_2p", G2_TEXTO, _ctx(it)) is True


# ---- P5: nombres inventados -----------------------------------------------
def test_P5_inserta_nombres_propios_que_no_estan_en_la_campana(pt, it):
    ctx = _ctx(it)
    r = pt.perturbar("P5", G2_TEXTO, ctx, _rng())
    assert _quitar(r.texto, r.info) == G2_TEXTO
    nombres = r.info["nombres"]
    assert len(nombres) == 2 and len(set(nombres)) == 2
    for n in nombres:
        assert re.fullmatch(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}", n)
        assert n not in ctx.conocidos and n not in G2_TEXTO
    assert set(it.nombres_no_reconocidos(r.texto, r.ctx)) == set(nombres)
    assert it.nombres_no_reconocidos(G2_TEXTO, ctx) == []


# ---- P6: corrupción gramatical ---------------------------------------------
def test_P6_baraja_palabras_en_minuscula_de_cerca_del_30_por_ciento_de_oraciones(pt, it):
    ctx = _ctx(it)
    r = pt.perturbar("P6", G2_TEXTO, ctx, _rng())
    assert r.texto != G2_TEXTO
    palabras = lambda s: sorted(re.findall(r"\w+", s.lower()))
    assert palabras(r.texto) == palabras(G2_TEXTO)                       # mismo multiconjunto
    assert re.sub(r"\w+", "", r.texto) == re.sub(r"\w+", "", G2_TEXTO)   # misma puntuación y espacios
    mayus = lambda s: [(i, t) for i, t in enumerate(re.findall(r"\w+", s)) if t[0].isupper()]
    assert mayus(r.texto) == mayus(G2_TEXTO)                              # mayúsculas en su sitio
    n_or = len(r.info["oraciones_barajadas"]) + r.info["oraciones_intactas"]
    assert 0.15 <= len(r.info["oraciones_barajadas"]) / n_or <= 0.5
    assert it.calcular(r.texto, ctx, nombres=["qn1_ttr", "qn1_legibilidad_fh"]) == \
        it.calcular(G2_TEXTO, ctx, nombres=["qn1_ttr", "qn1_legibilidad_fh"])   # invariantes exactos


def test_P6_respeta_las_etiquetas_de_g1(pt, it):
    r = pt.perturbar("P6", G1_TEXTO, _ctx(it, brazo="G1"), _rng())
    assert r.texto.startswith("narrativa\n")
    assert r.texto.split("\nmecanica\n")[1] == G1_TEXTO.split("\nmecanica\n")[1]


# ---- P7: párrafo duplicado ---------------------------------------------------
def test_P7_duplica_un_parrafo_completo(pt, it):
    r = pt.perturbar("P7", G2_TEXTO, _ctx(it), _rng())
    original = G2_TEXTO.split("\n\n")
    nuevo = r.texto.split("\n\n")
    assert len(nuevo) == len(original) + 1
    i = r.info["parrafo"]
    assert nuevo[i] == nuevo[i + 1] == original[i]
    assert nuevo[:i + 1] + nuevo[i + 2:] == original
    # la duplicación sube la repetición y baja el TTR
    c = _ctx(it)
    a = it.calcular(G2_TEXTO, c, nombres=["qn1_ngram_repeticion", "qn1_ttr"])
    b = it.calcular(r.texto, c, nombres=["qn1_ngram_repeticion", "qn1_ttr"])
    assert b["qn1_ngram_repeticion"] > a["qn1_ngram_repeticion"] and b["qn1_ttr"] < a["qn1_ttr"]


# ---- P8: contaminación cruzada ----------------------------------------------
def test_P8_sustituye_por_la_narracion_del_donante_y_lo_exige(pt, it):
    donante = "Un dragón de cobre sobrevuela Zarkaland mientras Mirtha canta."
    r = pt.perturbar("P8", G2_TEXTO, _ctx(it), _rng(), donante=donante)
    assert r.texto == donante
    with pytest.raises(ValueError):
        pt.perturbar("P8", G2_TEXTO, _ctx(it), _rng())


# ---- P9: permutación de la ventana -----------------------------------------
def test_P9_permuta_una_ventana_de_8_de_forma_determinista(pt):
    textos = [f"Turno {i} en la torre." for i in range(8)]
    r1 = pt.perturbar_ventana("P9", textos, _rng(3))
    r2 = pt.perturbar_ventana("P9", textos, _rng(3))
    assert r1.textos == r2.textos and r1.info == r2.info
    assert sorted(r1.textos) == sorted(textos) and r1.textos != textos
    assert sorted(r1.info["perm"]) == list(range(8))
    assert textos == [f"Turno {i} en la torre." for i in range(8)]     # original intacto
    assert any(pt.perturbar_ventana("P9", textos, _rng(s)).textos != r1.textos for s in range(10))


# ---- P10: pifia narrada como éxito ------------------------------------------
def test_P10_anade_una_pifia_y_narra_exito(pt, it):
    ctx = _ctx(it)
    r = pt.perturbar("P10", G2_TEXTO, ctx, _rng())
    assert _quitar(r.texto, r.info) == G2_TEXTO
    assert any(t["pifia"] and t["dado"] == 1 for t in r.ctx.tiradas) and ctx.tiradas == []
    assert it.calcular(G2_TEXTO, ctx, nombres=["cr1_veredicto_contradice_narracion"])["cr1_veredicto_contradice_narracion"] is False
    assert it.calcular(r.texto, r.ctx, nombres=["cr1_veredicto_contradice_narracion"])["cr1_veredicto_contradice_narracion"] is True


# ---- P11: artefacto de formato ----------------------------------------------
def test_P11a_inyecta_etiquetas_y_linea_mecanica_en_g2_y_se_puede_quitar(pt, it):
    from validacion_generar import prosa
    ctx = _ctx(it, brazo="G2")
    r = pt.perturbar("P11a_inyeccion", G2_TEXTO, ctx, _rng())
    assert re.search(r"^mecanica\s*$", r.texto, re.M) and r.texto.startswith("narrativa\n")
    assert re.search(r"\b(Éxito|Fallo) \(\d+ vs CD \d+\)", r.texto)
    assert prosa(r.texto, "G1") == G2_TEXTO.strip()
    assert pt.elegible("P11a_inyeccion", G2_TEXTO, ctx) is True
    assert pt.elegible("P11a_inyeccion", G1_TEXTO, _ctx(it, brazo="G1")) is False


def test_P11b_elimina_etiquetas_y_mecanica_en_g1_como_prosa(pt, it):
    from validacion_generar import prosa
    ctx = _ctx(it, brazo="G1")
    r = pt.perturbar("P11b_eliminacion", G1_TEXTO, ctx, _rng())
    assert r.texto == prosa(G1_TEXTO, "G1")
    assert "mecanica" not in r.texto and "Éxito" not in r.texto
    assert pt.elegible("P11b_eliminacion", G1_TEXTO, ctx) is True
    assert pt.elegible("P11b_eliminacion", G2_TEXTO, _ctx(it, brazo="G2")) is False


# ---- P12: otro alfabeto ------------------------------------------------------
def test_P12_inserta_palabras_de_otro_alfabeto_sin_tocar_el_resto(pt, it):
    from validacion_generar import SUCIO
    r = pt.perturbar("P12", G2_TEXTO, _ctx(it), _rng())
    assert not SUCIO.search(G2_TEXTO) and SUCIO.search(r.texto)
    assert len(r.info["palabras"]) == 3
    limpio = r.texto
    for p in r.info["palabras"]:
        limpio = limpio.replace(p + " ", "", 1)
    assert limpio == G2_TEXTO


# ---- propiedades comunes ----------------------------------------------------
PIDS_TURNO = [f"P1_{c}" for c in CATEGORIAS] + [f"P2_{c}" for c in CATEGORIAS] + [
    "P3_dead_actua", "P3_dead_habla", "P3_missing_actua", "P3_missing_habla",
    "P4_2p", "P4_3p", "P5", "P6", "P7", "P10", "P12"]


@pytest.mark.parametrize("pid", PIDS_TURNO)
def test_determinista_con_semilla_y_no_muta_entradas(pt, it, pid):
    ctx = _ctx(it)
    ctx_antes = copy.deepcopy(ctx)
    a = pt.perturbar(pid, G2_TEXTO, ctx, _rng(7))
    b = pt.perturbar(pid, G2_TEXTO, ctx, _rng(7))
    assert (a.texto, a.info, a.ctx.tiradas, a.ctx.estados_pnj) == (b.texto, b.info, b.ctx.tiradas, b.ctx.estados_pnj)
    assert ctx == ctx_antes and ctx.tiradas == [] and ctx.estados_pnj == ctx_antes.estados_pnj
    assert a.texto != G2_TEXTO
    assert G2_TEXTO.startswith("Te acercas a la columna")              # el original sigue intacto


# ======================================================================
# C. estadística (estadistica.py) y veredictos
# ======================================================================
@pytest.fixture
def es():
    import estadistica
    return estadistica


def test_wilson_valores_conocidos(es):
    lo, hi = es.wilson(0, 10)
    assert lo == pytest.approx(0.0, abs=1e-9) and hi == pytest.approx(0.2775, abs=1e-3)
    lo, hi = es.wilson(5, 10)
    assert (lo, hi) == pytest.approx((0.2366, 0.7634), abs=1e-3)
    assert es.wilson(0, 0) == (0.0, 1.0)


def test_mcnemar_exacta_bilateral(es):
    assert es.mcnemar_exacta(0, 0) == 1.0
    assert es.mcnemar_exacta(5, 0) == pytest.approx(0.0625)
    assert es.mcnemar_exacta(10, 2) == pytest.approx(158 / 4096)
    assert es.mcnemar_exacta(3, 3) == 1.0


def test_holm_ajusta_y_es_monotono(es):
    assert es.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert es.holm([]) == []
    assert es.holm([0.5]) == [0.5]
    assert max(es.holm([0.4, 0.9])) <= 1.0


def test_cliff_y_delta_pareado(es):
    assert es.cliff_delta([1, 2, 3], [1, 2, 3]) == 0
    assert es.cliff_delta([4, 5, 6], [1, 2, 3]) == 1
    assert es.cliff_delta([1, 2, 3], [4, 5, 6]) == -1
    assert es.delta_pareado([1, 1, -1, 0]) == pytest.approx(0.25)
    assert es.delta_pareado([]) == 0.0


def test_bootstrap_mediana_reproducible_y_sensato(es):
    assert es.ic_bootstrap_mediana([2.0] * 50, semilla=1) == (2.0, 2.0)
    d = [(-1) ** i * (1 + i % 3) for i in range(60)]
    a = es.ic_bootstrap_mediana(d, semilla=5, B=2000)
    assert a == es.ic_bootstrap_mediana(d, semilla=5, B=2000)
    assert a[0] <= 0 <= a[1]
    d2 = [1.0 + 0.01 * i for i in range(60)]
    lo, hi = es.ic_bootstrap_mediana(d2, semilla=5, B=2000)
    assert lo > 0.5


def test_prueba_de_signos_exacta(es):
    assert es.prueba_signos([1, 1, 1, 1, 1]) == pytest.approx(0.0625)
    assert es.prueba_signos([0, 0, 0]) == 1.0
    assert es.prueba_signos([1, -1, 1, -1]) == 1.0


def test_newcombe_pareado(es):
    d, lo, hi = es.newcombe_pareado(a=0, b=0, c=20, d=0)      # todo pasa de 0 a 1
    assert d == pytest.approx(1.0) and lo > 0.7 and hi <= 1.0
    d, lo, hi = es.newcombe_pareado(a=5, b=0, c=0, d=25)      # nadie cambia
    assert d == 0.0 and lo < 0 < hi


def test_tabla_2x2_pareada(es):
    antes = [0, 0, 1, 1, 0, 1]
    despues = [1, 0, 1, 0, 1, 1]
    assert es.contar_pareado(antes, despues) == {"a": 2, "b": 1, "c": 2, "d": 1}   # a: 1→1, b: 1→0, c: 0→1, d: 0→0


def test_direccion_numerica_exige_significancia_y_efecto_no_trivial(es):
    assert es.direccion_numerica(p_aj=0.001, delta=0.5) == "sube"
    assert es.direccion_numerica(p_aj=0.001, delta=-0.5) == "baja"
    assert es.direccion_numerica(p_aj=0.001, delta=0.10) == "sin_cambio"      # efecto despreciable (<0.147)
    assert es.direccion_numerica(p_aj=0.20, delta=0.9) == "sin_cambio"        # no significativo


def test_direccion_booleana(es):
    assert es.direccion_booleana(p_aj=0.001, b=0, c=20) == "se_dispara"
    assert es.direccion_booleana(p_aj=0.001, b=20, c=0) == "baja"
    assert es.direccion_booleana(p_aj=0.5, b=3, c=1) == "sin_cambio"


@pytest.mark.parametrize("esperado,observado,veredicto", [
    ("se_dispara", "se_dispara", "responde"), ("se_dispara", "sin_cambio", "no responde"),
    ("se_dispara", "baja", "dirección opuesta"),
    ("sube", "sube", "responde"), ("sube", "sin_cambio", "no responde"), ("sube", "baja", "dirección opuesta"),
    ("baja", "sube", "dirección opuesta"), ("baja", "baja", "responde"),
    ("sin_cambio", "sin_cambio", "responde"), ("sin_cambio", "sube", "cambio inesperado"),
    ("sin_cambio", "se_dispara", "cambio inesperado")])
def test_veredicto(es, esperado, observado, veredicto):
    assert es.veredicto(esperado, observado, n=100) == veredicto


def test_veredicto_no_aplica_con_pocos_pares(es):
    assert es.veredicto("se_dispara", "se_dispara", n=3) == "no aplica"
    assert es.veredicto("sube", "sube", n=0) == "no aplica"


# ======================================================================
# D. datos: muestreo reproducible y reconstrucción del contexto (solo SELECT)
# ======================================================================
@pytest.fixture(scope="module")
def dat():
    import datos
    return datos


@pytest.fixture(scope="module")
def conn():
    import db
    import psycopg
    from psycopg.rows import dict_row
    try:
        c = psycopg.connect(db.DSN, row_factory=dict_row, connect_timeout=3)
    except Exception as e:      # pragma: no cover
        pytest.skip(f"sin base de datos: {e}")
    yield c
    c.close()


def test_plan_muestra_reproducible_y_estratificado(dat):
    pares = dat.cargar_pares()
    p1 = dat.plan_muestra(pares, semilla=20260920)
    assert p1 == dat.plan_muestra(pares, semilla=20260920)
    assert p1 != dat.plan_muestra(pares, semilla=1)
    for brazo in ("G1", "G2"):
        assert len([t for t in p1["turnos"] if t["brazo"] == brazo]) == 150
    assert len(p1["pares"]) >= 8 and {p["lote"] for p in p1["pares"]} == {"v1", "v2"}
    assert all(2 <= t["turn"] <= 1400 for t in p1["turnos"])
    assert len({(t["campaign_id"], t["turn"]) for t in p1["turnos"]}) == 300
    assert all(v["start"] + 7 <= 1400 for v in p1["ventanas"])


def _campana(dat, conn, par_idx=0, brazo="G2", lote="v1"):
    pares = [p for p in dat.cargar_pares() if p["lote"] == lote]
    p = pares[par_idx]
    return dat.DatosCampana(conn, p["campaign_g2" if brazo == "G2" else "campaign_g1"], brazo, p["par"])


def test_contexto_respeta_created_at_turn_y_escena_anterior(dat, conn):
    d = _campana(dat, conn, 0, "G2", "v1")          # par 07 G2: 'Malakor' nace en el turno 452
    antes, despues = d.contexto(452), d.contexto(453)
    nombres = lambda c: {e["nombre"] for e in c.entidades}
    assert "Malakor" not in nombres(antes) and "Malakor" in nombres(despues)
    assert antes.escena_anterior == d.texto(451)
    assert antes.pj_nombre == "Tarq" and antes.hp_current == 24 and antes.brazo == "G2"
    assert "Tarq" in antes.nombres_pj_conocidos and len(antes.nombres_pj_conocidos) > 5


def test_estado_historico_de_pnj_converge_al_estado_final_de_la_base(dat, conn):
    d = _campana(dat, conn, 0, "G2", "v1")
    finales = {r["name"]: r["status"] for r in conn.execute(
        "SELECT name, status FROM npcs WHERE campaign_id=%s", (d.campaign_id,)).fetchall()}
    assert finales and all(d.estado_en(n, 10 ** 9) == s for n, s in finales.items())
    # y antes de nacer/morir es 'alive' (los sembrados empiezan vivos)
    assert all(d.estado_en(n, 0) == "alive" for n in finales)


def test_tiradas_se_reconstruyen_con_la_semilla_del_motor(dat, conn):
    d = _campana(dat, conn, 0, "G2", "v1")
    t = next(t for t in range(2, 400) if "{" in d.accion(t))
    ctx = d.contexto(t)
    assert ctx.tiradas and all({"etiqueta", "dado", "pifia"} <= set(x) for x in ctx.tiradas)
    assert d.contexto(t).tiradas == ctx.tiradas                       # determinista


def test_previas_solo_incluyen_menciones_de_turnos_anteriores(dat, conn):
    d = _campana(dat, conn, 0, "G2", "v1")
    c5, c50 = d.contexto(5), d.contexto(50)
    assert c5.previas <= c50.previas | {e["nombre"] for e in c5.entidades}
    assert len(c50.previas) >= len(c5.previas)


# ======================================================================
# E. fidelidad: el recálculo sobre texto reproduce lo guardado en turn_validation
# ======================================================================
@pytest.fixture(scope="module")
def fi():
    import fidelidad
    return fidelidad


def test_fidelidad_compara_a_los_decimales_de_la_columna(fi):
    from decimal import Decimal
    assert fi.coincide(0.1234, Decimal("0.123"), 3) is True
    assert fi.coincide(0.1236, Decimal("0.123"), 3) is False
    assert fi.coincide(51.14, Decimal("51.14"), 2) is True
    assert fi.coincide(None, None, 3) is True
    assert fi.coincide(None, Decimal("0.1"), 3) is False
    assert fi.coincide(0.5, None, 3) is False


def test_fidelidad_resume_coincidencias_y_discrepancias(fi):
    filas = [{"columna": "qn1_ttr", "ok": True}, {"columna": "qn1_ttr", "ok": False},
             {"columna": "qn1_ttr", "ok": True}, {"columna": "otro", "ok": True}]
    r = fi.resumir(filas)
    assert r["qn1_ttr"] == {"n": 3, "ok": 2, "discrepancias": 1}
    assert r["otro"] == {"n": 1, "ok": 1, "discrepancias": 0}


def test_fidelidad_recalcula_un_turno_real_con_las_5_columnas(fi, dat, conn):
    d = _campana(dat, conn, 0, "G2", "v1")
    fila = dat.guardado_en_turn_validation(conn, d.campaign_id, [10])[10]
    res = fi.comparar_turno(d, 10, fila)
    cols = {r["columna"] for r in res}
    assert {"qn1_ttr", "qn1_ngram_repeticion", "qn1_legibilidad_fh",
            "cl2_lugar_jaccard_similarity", "cr2_entidad_grafo_densidad",
            "qn2_pj_piensa_narrado", "cl2_pnj_inactivo_actua", "cr1_veredicto_contradice_narracion",
            "cl2_pc_hp_contradice_narracion", "qn2_pj_accion_revisar",
            "cr2_nombres_no_reconocidos", "meta_comentario", "comenta_reglas"} <= cols
    assert all("recalculado" in r and "guardado" in r for r in res)


def test_la_prueba_de_fidelidad_detecta_un_contexto_equivocado(fi, dat, conn):
    # control de la propia prueba: con la escena anterior equivocada NO debe coincidir
    d = _campana(dat, conn, 1, "G2", "v1")
    r = fi.control_de_mutacion(conn, {"a": d}, [(d.campaign_id, t) for t in range(100, 120)])
    assert r["escena_erronea"]["n"] == 20 and r["escena_erronea"]["discrepancias"] >= 15


def test_fidelidad_50_turnos_reales_coinciden_con_turn_validation(fi, dat, conn):
    # regresión: si alguien cambia vertical_slice.py o el contexto, esto se rompe
    for brazo, lote in (("G2", "v1"), ("G1", "v2")):
        d = _campana(dat, conn, 1, brazo, lote)
        ids = list(range(100, 125))
        guardado = dat.guardado_en_turn_validation(conn, d.campaign_id, ids)
        filas = [f for t in ids for f in fi.comparar_turno(d, t, guardado[t])]
        malas = [(f["turn"], f["columna"], f["recalculado"], f["guardado"]) for f in filas if not f["ok"]]
        assert not malas, malas


# ======================================================================
# F. correr_sensibilidad: celdas, familias de comparaciones, Holm y veredictos
# ======================================================================
@pytest.fixture(scope="module")
def co():
    import correr_sensibilidad
    return correr_sensibilidad


def test_celda_booleana(co):
    c = co.estadisticos_celda("bool", [False] * 40, [True] * 40, semilla=1)
    assert (c["n"], c["a"], c["b"], c["c"], c["d"]) == (40, 0, 0, 40, 0)
    assert c["tasa_antes"] == 0 and c["tasa_despues"] == 1 and c["p"] < 1e-9
    assert c["ic_dif"][0] > 0.8


def test_celda_numerica_excluye_pares_con_none(co):
    antes = [0.5] * 40 + [None] * 5
    despues = [0.6 + 0.001 * i for i in range(40)] + [0.4] * 5
    c = co.estadisticos_celda("num", antes, despues, semilla=1)
    assert c["n"] == 40 and c["delta_pareado"] == 1.0 and c["ic_dif"][0] > 0.09
    assert c["mediana_dif"] > 0.1


def test_matriz_marca_responde_con_deteccion_parcial(co):
    base = {"esperado": "se_dispara", "veredicto": "responde", "observado": "se_dispara", "tipo": "bool"}
    assert co._celda_resumen(dict(base, tasa_despues=1.0)) == "●✓"
    assert co._celda_resumen(dict(base, tasa_despues=0.10)) == "●✓~"           # detecta <50 % de lo inyectado
    assert co._celda_resumen(dict(base, veredicto="no responde", observado="sin_cambio", tasa_despues=0.0)) == "●✗(=)"
    assert co._celda_resumen({"esperado": "sube", "veredicto": "responde", "observado": "sube", "tipo": "num"}) == "▲✓"


def test_celda_vacia_es_no_aplica_sin_romper(co):
    esperado = {"P1_accion": {"qn2_pj_accion_revisar": "se_dispara", "qn1_ttr": "sube"}}
    celdas = {("G2", "P1_accion", "qn2_pj_accion_revisar"): {"tipo": "bool", "antes": [], "despues": []},
              ("G2", "P1_accion", "qn1_ttr"): {"tipo": "num", "antes": [], "despues": []}}
    filas = co.evaluar(celdas, esperado, semilla=1)
    assert [f["veredicto"] for f in filas] == ["no aplica", "no aplica"] and all(f["n"] == 0 for f in filas)


def test_completar_celdas_esperadas_crea_las_que_faltan(co):
    celdas = {("G2", "P5", "qn1_ttr"): {"tipo": "num", "antes": [0.5], "despues": [0.6]}}
    co.completar_celdas_esperadas(celdas, {"P5": {"qn1_ttr": "sube", "meta_comentario": "sin_cambio"}},
                                  brazos=("G1", "G2"))
    assert celdas[("G1", "P5", "qn1_ttr")] == {"tipo": "num", "antes": [], "despues": []}
    assert celdas[("G2", "P5", "meta_comentario")] == {"tipo": "bool", "antes": [], "despues": []}
    assert celdas[("G2", "P5", "qn1_ttr")]["antes"] == [0.5]                      # no pisa lo existente


def test_evaluar_aplica_holm_por_familia_y_da_veredicto(co):
    esperado = {"P1_decision": {"qn2_pj_piensa_narrado": "se_dispara", "meta_comentario": "sin_cambio",
                                "qn1_ttr": "sube"}}
    celdas = {
        ("G2", "P1_decision", "qn2_pj_piensa_narrado"): {"tipo": "bool", "antes": [0] * 40, "despues": [0] * 40},
        ("G2", "P1_decision", "meta_comentario"): {"tipo": "bool", "antes": [0] * 40, "despues": [0] * 40},
        ("G2", "P1_decision", "qn1_ttr"): {"tipo": "num", "antes": [0.5] * 40,
                                           "despues": [0.5 + 0.01 * (1 + i % 5) for i in range(40)]},
        ("G2", "P1_decision", "cr2_entidad_grafo_densidad"): {"tipo": "num", "antes": [0.5] * 40,
                                                              "despues": [0.5] * 40},
        ("G1", "P1_decision", "qn2_pj_piensa_narrado"): {"tipo": "bool", "antes": [0] * 4, "despues": [1] * 4},
    }
    filas = {(f["brazo"], f["perturbacion"], f["instrumento"]): f
             for f in co.evaluar(celdas, esperado, semilla=1)}
    f = filas[("G2", "P1_decision", "qn2_pj_piensa_narrado")]
    assert f["familia"] == "confirmatoria" and f["observado"] == "sin_cambio" and f["veredicto"] == "no responde"
    f = filas[("G2", "P1_decision", "qn1_ttr")]
    assert f["observado"] == "sube" and f["veredicto"] == "responde" and f["p_holm"] >= f["p"]
    assert filas[("G2", "P1_decision", "meta_comentario")]["familia"] == "control"
    assert filas[("G2", "P1_decision", "meta_comentario")]["veredicto"] == "responde"
    f = filas[("G2", "P1_decision", "cr2_entidad_grafo_densidad")]
    assert f["familia"] == "descriptivo" and f["veredicto"] == ""           # sin expectativa pre-especificada
    assert filas[("G1", "P1_decision", "qn2_pj_piensa_narrado")]["veredicto"] == "no aplica"   # n=4 < 10
