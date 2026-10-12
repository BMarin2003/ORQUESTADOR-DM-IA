#!/usr/bin/env python3
"""
Pruebas de persona2.py (detector determinista de usurpación de agencia y muerte
del PJ en narración de DM en español, 2.ª persona).

Escritas ANTES que el código (TDD). Cada caso está escrito a mano; no se han
extraído de la muestra de evaluación. Corre con:

    PYTHONUTF8=1 py scripts/instrumentos/test_persona2.py        # runner plano
    PYTHONUTF8=1 py -m pytest scripts/instrumentos/test_persona2.py   # también vale

Convenciones de los casos:
  H(dm, accion, nombre)  -> lista de hallazgos de detectar_usurpacion
  cats(hs)               -> lista de categorías
  «positivo»  = el DM narra algo del PJ que el jugador no declaró.
  «negativo»  = exclusión obligatoria (percepción, consecuencia mecánica
                involuntaria, ejecución de lo declarado, diálogo de PNJ,
                pregunta, condicional, PNJ que no es el PJ...).
"""
import json
import pathlib
import sys
import traceback

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import spacy  # noqa: E402

import persona2 as P  # noqa: E402

NLP = spacy.load("es_core_news_sm")


def H(dm, accion="", nombre=None):
    return P.detectar_usurpacion(dm, accion, NLP, nombre_pj=nombre)


def cats(hs):
    return [h["categoria"] for h in hs]


def uno(hs, cat):
    l = [h for h in hs if h["categoria"] == cat]
    assert l, f"esperaba un hallazgo {cat}; obtuve {cats(hs)}"
    return l[0]


# ═════════════════════ POSITIVOS · 2.ª persona ═════════════════════

def test_volicion_implicita_decides():
    h = uno(H("Decides huir por la ventana."), "VOLICION")
    assert h["verbo_lema"] == "decidir"
    assert h["persona"] == "2" and h["explicito"] is False
    assert h["confianza"] == "alta"


def test_volicion_sujeto_tu_explicito():
    h = uno(H("Tú decides quedarte junto a la puerta."), "VOLICION")
    assert h["explicito"] is True


def test_volicion_te_obligas_a():
    h = uno(H("Te obligas a seguir adelante."), "VOLICION")
    assert h["verbo_lema"] == "obligar"


def test_volicion_eliges():
    uno(H("Eliges el camino de la izquierda."), "VOLICION")


def test_cognicion_comprendes():
    h = uno(H("Comprendes que no hay salida."), "COGNICION")
    assert h["verbo_lema"] == "comprender"


def test_cognicion_te_das_cuenta():
    h = uno(H("Te das cuenta de que la puerta está cerrada."), "COGNICION")
    assert h["verbo_lema"] == "darse cuenta"


def test_cognicion_recuerdas_inicio_de_oracion():
    # spaCy es_core_news_sm etiqueta «Recuerdas» inicial como ADJ: el detector no puede depender de eso
    uno(H("Recuerdas su rostro con una nitidez incómoda."), "COGNICION")


def test_cognicion_dudas_verbo():
    uno(H("Dudas un instante antes de responder."), "COGNICION")


def test_cognicion_se_te_ocurre():
    uno(H("Se te ocurre esconderte tras el barril."), "COGNICION")


def test_emocion_sientes_miedo():
    h = uno(H("Sientes miedo al ver la sombra."), "EMOCION")
    assert h["verbo_lema"] == "sentir"


def test_emocion_te_invade_el_temor():
    uno(H("Te invade el temor."), "EMOCION")


def test_emocion_sujeto_antepuesto_te_embarga():
    uno(H("Un miedo helado te embarga."), "EMOCION")


def test_emocion_te_sientes_seguro():
    uno(H("Te sientes seguro en la penumbra."), "EMOCION")


def test_emocion_tienes_miedo():
    uno(H("Tienes miedo, aunque no lo admitas."), "EMOCION")


def test_emocion_gana_a_sensorial_punzada_de_miedo():
    # «punzada» es sensorial pero «miedo» es emoción: la emoción manda
    uno(H("Sientes una punzada de miedo en el estómago."), "EMOCION")


def test_habla_dices_tras_cita():
    h = uno(H("«No me toques», dices con voz ronca."), "HABLA")
    assert h["verbo_lema"] == "decir"


def test_habla_murmuras_inicio_de_oracion():
    assert "HABLA" in cats(H("Murmuras una excusa y bajas la mirada."))


def test_accion_te_levantas():
    h = uno(H("Te levantas con cuidado."), "ACCION_NO_DECLARADA")
    assert h["confianza"] == "media" and h["declarada"] is False


def test_accion_das_un_paso():
    uno(H("Das un paso hacia la sombra."), "ACCION_NO_DECLARADA")


def test_accion_abres_y_avanzas():
    hs = [h for h in H("Abres la puerta y avanzas hacia la sombra.")
          if h["categoria"] == "ACCION_NO_DECLARADA"]
    assert sorted(h["verbo_lema"] for h in hs) == ["abrir", "avanzar"]


def test_accion_retrocedes():
    uno(H("Retrocedes hasta tocar la pared."), "ACCION_NO_DECLARADA")


# ═════════════════════ EXCLUSIONES OBLIGATORIAS ═════════════════════

def test_excl_percepcion_ves_oyes_notas():
    assert H("Ves una luz tenue y oyes pasos lejanos. Notas un olor a humo.") == []


def test_excl_sientes_el_frio_del_metal():
    assert H("Sientes el frío del metal.") == []


def test_excl_sientes_dolor_y_vibracion():
    assert H("Sientes un dolor punzante en el hombro y una vibración en el suelo.") == []


def test_excl_sientes_como():
    assert H("Sientes cómo su respiración se vuelve errática.") == []


def test_excl_notas_que_es_percepcion():
    assert H("Notas que el patrón no es solo decorativo.") == []


def test_excl_consecuencia_mecanica_involuntaria():
    assert H("Tropiezas y caes al suelo; sangras por la ceja.") == []


def test_excl_tienes_frio_no_es_emocion():
    assert H("Tienes frío y las manos entumecidas.") == []


def test_excl_accion_declarada_mismo_lema():
    assert H("Abres la puerta con un chirrido.", "Intento abrir la puerta.") == []


def test_excl_accion_declarada_sinonimo_obvio():
    # tocar ~ recorrer (mismo grupo de sinónimos del léxico)
    assert H("Recorres el metal con la yema de los dedos.", "Toco el metal.") == []


def test_accion_no_declarada_si_el_lema_difiere():
    h = uno(H("Recorres el metal con los dedos.", "Me quedo quieto y escucho."),
            "ACCION_NO_DECLARADA")
    assert h["declarada"] is False


def test_falso_amigo_tus_dedos_recorren_el_metal():
    # sujeto = parte del cuerpo del PJ («tus dedos», 3.ª pl.): es una acción del PJ narrada por metonimia.
    # Si el jugador declaró tocar el metal (sinónimo recorrer~tocar) NO es usurpación.
    assert H("Tus dedos recorren el metal.", "Toco el metal con la yema de los dedos.") == []


def test_parte_del_cuerpo_como_sujeto_sin_declarar_si_marca():
    h = uno(H("Tus dedos recorren el metal.", "Me quedo quieto y escucho."), "ACCION_NO_DECLARADA")
    assert h["verbo_lema"] == "recorrer" and h["confianza"] == "media"
    uno(H("Tu mano se cierra sobre la empuñadura.", ""), "ACCION_NO_DECLARADA")


def test_parte_del_cuerpo_reflejo_involuntario_no_marca():
    assert H("Tus manos tiemblan y tus piernas flaquean.", "") == []


def test_falso_amigo_sustantivo_dudas():
    assert H("Tus dudas se disipan con el amanecer.") == []
    assert H("Las dudas del guardia crecen.") == []


def test_falso_amigo_sustantivo_notas():
    assert H("Las notas del bardo llenan la sala.") == []


def test_excl_dialogo_pnj_entre_comillas():
    assert H('El guardia gruñe: "Sabes que no puedes entrar. Decides ahora."') == []


def test_excl_dialogo_pnj_con_raya():
    assert H("—Llamas a quien no ha sido invocado y preguntas por secretos —dice la voz—.") == []


def test_excl_pregunta_al_jugador():
    assert H("¿Qué decides hacer ahora?") == []


def test_excl_condicional_si():
    assert H("Si decides avanzar, el suelo cederá bajo tus pies.") == []


def test_excl_modal_y_obligacion_no_son_narracion():
    assert H("Puedes decidir tu siguiente paso. Tienes que decidir rápido.") == []


def test_excl_pnj_que_decide_no_es_el_pj():
    assert H("Ves cómo el guardia decide huir.") == []


def test_excl_tercera_persona_sin_nombre_pj():
    assert H("El guardia abre la puerta y se aleja.") == []


def test_perifrasis_seguir_gerundio_hereda_lo_declarado():
    # «sigues revisando»: el núcleo es «revisar»; si el jugador declaró buscar/revisar, no es usurpación
    assert H("Sigues revisando los registros.", "Busco en el mapa con calma.") == []
    uno(H("Sigues revisando los registros.", "Me quedo quieto y escucho."), "ACCION_NO_DECLARADA")


def test_perifrasis_intentar_infinitivo_hereda_lo_declarado():
    assert H("Intentas abrir la puerta.", "Abro la puerta despacio.") == []
    h = uno(H("Intentas fundirte con las sombras.", "Me pego a la pared."), "ACCION_NO_DECLARADA")
    assert h["verbo_lema"] == "intentar"


# ═════════════════════ tirada y declarada ═════════════════════

def test_tirada_declarada_true_con_tag_de_habilidad():
    h = uno(H("Entiendes que el patrón no es decorativo.",
              "Examino los grabados con calma.\n\n{Investigación}"), "COGNICION")
    assert h["tirada_declarada"] is True and h["declarada"] is False


def test_tirada_declarada_false_sin_tag():
    h = uno(H("Entiendes que el patrón no es decorativo.", "Examino los grabados con calma."),
            "COGNICION")
    assert h["tirada_declarada"] is False


def test_volicion_eco_de_lo_declarado_queda_marcada_declarada():
    h = uno(H("Decides huir.", "Decido huir por la ventana."), "VOLICION")
    assert h["declarada"] is True


def test_habla_con_cita_declarada_marca_declarada():
    h = uno(H("Respondes con frialdad.", '"No pienso decírtelo." Cruzo los brazos.'), "HABLA")
    assert h["declarada"] is True


# ═════════════════════ CONTROL POSITIVO · 3.ª persona con nombre ═════════════════════

def test_control_osric_decide_huir():
    h = uno(H("Osric decide huir.", "", "Osric"), "VOLICION")
    assert h["persona"] == "3" and h["confianza"] == "alta"


def test_control_el_guardia_decide_huir_no_marca():
    assert H("El guardia decide huir.", "", "Osric") == []


def test_control_sin_nombre_pj_no_marca():
    assert H("Osric decide huir.", "", None) == []


def test_control_ilvard_piensa():
    uno(H("Ilvard piensa que es una trampa.", "", "Ilvard"), "COGNICION")


def test_control_pnj_con_el_pj_como_objeto_no_marca():
    assert H("El guardia mira a Osric y decide huir.", "", "Osric") == []


def test_control_accion_fisica_con_nombre():
    h = uno(H("Osric golpea la puerta con el hombro.", "", "Osric"), "ACCION_NO_DECLARADA")
    assert h["persona"] == "3"


def test_control_accion_fisica_declarada_no_marca():
    assert H("Osric golpea la puerta con el hombro.", "Golpeo la puerta.", "Osric") == []


def test_control_habla_con_nombre():
    uno(H("Osric responde con una risa amarga.", "", "Osric"), "HABLA")


def test_control_nombre_dentro_de_cita_no_marca():
    assert H('La mujer dice: "Osric decide por todos."', "", "Osric") == []


def test_control_verbo_antepuesto_al_nombre():
    uno(H('«Basta», murmura Osric.', "", "Osric"), "HABLA")


# ═════════════════════ MUERTE DEL PJ ═════════════════════

def test_muerte_mueres():
    r = P.narra_muerte_pj("Un tajo certero te abre el cuello y mueres desangrado.", NLP)
    assert r is not None and r["categoria"] == "MUERTE_PJ" and r["persona"] == "2"


def test_muerte_ultimo_aliento():
    assert P.narra_muerte_pj("Exhalas tu último aliento sobre las piedras.", NLP) is not None


def test_muerte_has_muerto():
    assert P.narra_muerte_pj("Has muerto. Tu aventura termina aquí.", NLP) is not None


def test_muerte_nombre_pj_cae_muerto():
    r = P.narra_muerte_pj("Osric cae muerto en el barro.", NLP, nombre_pj="Osric")
    assert r is not None and r["persona"] == "3"
    assert P.narra_muerte_pj("Osric cae muerto en el barro.", NLP) is None


def test_muerte_pnj_no_cuenta():
    assert P.narra_muerte_pj("El guardia cae muerto en el barro.", NLP, nombre_pj="Osric") is None
    assert P.narra_muerte_pj("El guardia muere. Osric observa la escena.", NLP,
                             nombre_pj="Osric") is None


def test_muerte_amenaza_condicional_o_casi_no_cuenta():
    assert P.narra_muerte_pj("Si sigues así, morirás en este pasillo.", NLP) is None
    assert P.narra_muerte_pj("Casi mueres cuando la viga cae a tu lado.", NLP) is None
    assert P.narra_muerte_pj("Estás a punto de morir.", NLP) is None
    assert P.narra_muerte_pj("No mueres, pero el golpe te deja sin aire.", NLP) is None


def test_muerte_hiperbole_no_cuenta():
    assert P.narra_muerte_pj("Mueres de ganas por saber qué hay dentro.", NLP) is None


def test_muerte_en_dialogo_de_pnj_no_cuenta():
    assert P.narra_muerte_pj('"Vas a morir aquí", gruñe el jefe.', NLP) is None


# ═════════════════════ REGLA DE «DECLARADA» v2 (ejecución de lo declarado) ═════════════════════
# Filas reales de la muestra de desarrollo en las que el DM solo narra la EJECUCIÓN de lo que el
# jugador declaró con otro verbo o con más detalle. Deben ser NEGATIVAS (no marcar).

def acc_fis(hs):
    return [h for h in hs if h["categoria"] == "ACCION_NO_DECLARADA"]


def test_v2_neg_separo_de_la_danza_alejas_del_torbellino():        # sinónimo verbal separar~alejar
    assert acc_fis(H("Te alejas del torbellino.", "Me separo de la danza de luz.\n{Acrobacias}")) == []


def test_v2_neg_recojo_el_pergamino_levantas_el_papel():           # sinónimo verbal recoger~levantar
    assert acc_fis(H("Levantas el papel con cuidado.", "Recojo el pergamino con cuidado.\n{Investigación}")) == []


def test_v2_neg_trato_de_extraer_tus_dedos_rozan():                # sujeto = parte del cuerpo + verbo genérico
    assert acc_fis(H("Tus dedos rozan la superficie fría del metal.",
                     "Trato de extraer el cilindro de su ranura.\n{Trucos de manos}")) == []


def test_v2_neg_me_lanzo_a_un_lado_te_desplazas_en_un_arco():      # esquivar~desplazar
    assert acc_fis(H("Te desplazas en un arco amplio.", "Me lanzo hacia un lado para esquivar.\n{Acrobacias}")) == []


def test_v2_neg_bajo_el_pergamino_tus_dedos_recorren():            # contenido compartido + verbo genérico
    assert acc_fis(H("Tus dedos recorren la superficie del pergamino.",
                     "Bajo el pergamino y lo examino con calma.\n{Investigación}")) == []


def test_v2_neg_me_acerco_al_altar_te_inclinas_sobre_la_piedra():  # acercar~inclinar
    assert acc_fis(H("Te inclinas sobre la piedra.", "Me acerco al altar para verlo mejor.\n{Percepción}")) == []


def test_v2_neg_contenido_compartido_placa_de_bronce():            # «placa»/«bronce» aparecen en lo declarado
    assert acc_fis(H("Te agachas junto a la placa de bronce, pero la superficie está cubierta de hollín.",
                     "Miro la placa de bronce con atención.\n{Percepción}")) == []


def test_v2_neg_contenido_compartido_fe():                         # «fe» aparece en lo declarado
    assert acc_fis(H("Cierras los ojos y buscas el calor de tu fe.",
                     "Cierro los ojos e intento canalizar mi fe.\n{Religión}")) == []


def test_v2_dialogo_del_jugador_no_cuenta_como_accion_declarada():
    # las palabras que el jugador DICE no son acciones que declaró: «yo me muevo primero» no declara moverse
    hs = acc_fis(H("Te mueves hacia la puerta.", '"Yo me muevo primero", digo.\nMe quedo quieto.'))
    assert [h["verbo_lema"] for h in hs] == ["mover"]


def test_v2_pos_examino_el_altar_sacas_la_daga_y_golpeas():
    hs = acc_fis(H("Sacas tu daga y golpeas al guardia.", "Examino el altar.\n{Investigación}"))
    assert sorted(h["verbo_lema"] for h in hs) == ["golpear", "sacar"]


def test_v2_pos_declarado_hablar_y_el_dm_mueve_al_pj():
    uno(H("Te levantas de un salto y corres hacia la salida.", "Le pregunto al tabernero por el mapa.\n{Persuasión}"),
        "ACCION_NO_DECLARADA")


def test_v2_pos_parte_del_cuerpo_sin_verbo_generico_ni_contenido():
    uno(H("Tus dedos cortan el pergamino.", "Me quedo quieto y escucho.\n{Percepción}"), "ACCION_NO_DECLARADA")


def test_v2_configurable_contenido_apagado_vuelve_a_marcar():
    dm, acc = "Cierras los ojos y buscas el calor de tu fe.", "Cierro los ojos e intento canalizar mi fe."
    assert acc_fis(P.detectar_usurpacion(dm, acc, NLP)) == []
    hs = acc_fis(P.detectar_usurpacion(dm, acc, NLP, config={"contenido": False}))
    assert [h["verbo_lema"] for h in hs] == ["buscar"]


def test_v2_configurable_cuerpo_generico_apagado_vuelve_a_marcar():
    dm, acc = "Tus dedos rozan la superficie fría.", "Trato de extraer el cilindro."
    assert acc_fis(P.detectar_usurpacion(dm, acc, NLP)) == []
    hs = acc_fis(P.detectar_usurpacion(dm, acc, NLP, config={"cuerpo_generico": False}))
    assert [h["verbo_lema"] for h in hs] == ["rozar"]


def test_v2_config_v1_reproduce_la_regla_solo_verbal():
    hs = acc_fis(P.detectar_usurpacion("Te inclinas sobre la piedra.", "Me acerco al altar.", NLP, config=P.CONFIG_V1))
    assert [h["verbo_lema"] for h in hs] == ["inclinar"]


def test_v2_categorias_mentales_no_usan_la_regla_de_contenido():
    # «Comprendes» sigue marcándose aunque comparta objeto con la acción declarada
    uno(H("Comprendes que el altar es falso.", "Examino el altar con calma.\n{Investigación}"), "COGNICION")


def test_v2_hallazgo_informa_por_que_via_se_declaro_en_excluidos():
    hs, ex = P.analizar_completo("Cierras los ojos y buscas el calor de tu fe.", "Cierro los ojos e intento canalizar mi fe.", NLP)
    vias = {e["verbo_lema"]: e.get("via") for e in ex if e["motivo"] == "declarada"}
    assert vias.get("buscar") == "contenido" and vias.get("cerrar") == "verbo"


# --- v2b: residuales de la muestra de desarrollo (mismo patrón: el DM narra la ejecución de lo declarado) ---

def test_v2b_neg_intentar_tratar_son_sinonimos():
    assert acc_fis(H("Intentas descifrar el sentido de las formas.", "Trato de orientarme analizando el terreno.\n{Supervivencia}")) == []


def test_v2b_neg_retroceder_tras_paso_o_salto_atras():
    assert acc_fis(H("Retrocedes mientras el frío muerde tu piel.", "Doy un salto hacia atrás.\n{Acrobacias}")) == []


def test_v2b_neg_levantarse_tras_ponerse_en_pie():
    assert acc_fis(H("Te levantas con cautela.", "Me pongo en pie con cuidado.\n{Atletismo}")) == []


def test_v2b_neg_clase_movimiento_deslizarse_tras_alejarse():
    assert acc_fis(H("Te deslizas entre los peatones.", "Me alejo rápidamente de él.\n{Sigilo}")) == []


def test_v2b_neg_consecuencia_involuntaria_marcada_en_el_texto():
    assert acc_fis(H("En el forcejeo golpeas accidentalmente el tintero.", "Recojo los papeles del suelo.\n{Atletismo}")) == []


def test_v2b_neg_volverse_invisible_es_cambio_de_estado_no_movimiento():
    assert acc_fis(H("Te vuelves invisible para el ojo humano.", "Busco una salida alternativa.\n{Sigilo}")) == []


def test_v2b_pos_volverse_hacia_si_es_movimiento():
    uno(H("Te vuelves hacia la puerta.", "Me quedo quieto y escucho.\n{Percepción}"), "ACCION_NO_DECLARADA")


def test_v2b_neg_estirar_alcanzar():
    assert acc_fis(H("Estiras el brazo con cautela.", "Trato de alcanzar el sello de plata.\n{Atletismo}")) == []


def test_v2b_pos_manipulacion_no_queda_cubierta_por_movimiento():
    # el jugador declaró moverse; el DM le hace desenvainar: acción de otra clase -> se marca
    uno(H("Sacas tu daga.", "Me acerco al altar.\n{Percepción}"), "ACCION_NO_DECLARADA")


def test_v2b_via_perifrasis_queda_registrada():
    hs, ex = P.analizar_completo("Sigues revisando los registros.", "Busco en el mapa con calma.", NLP)
    assert [e.get("via") for e in ex if e["motivo"] == "declarada"] == ["nucleo"]


def test_fallback_spacy_no_emite_categorias_de_solo_declaracion():
    # bug hallado al comparar nlp=None con spaCy: los verbos «solo declaración» (alcanzar...) servían para
    # decidir «declarada» pero el respaldo Person=2 de spaCy los convertía en hallazgos de categoría DECL
    validas = {"VOLICION", "COGNICION", "EMOCION", "HABLA", "ACCION_NO_DECLARADA"}
    for t in ("Con calma, alcanzas el borde de la mesa.", "Mientras alcanzas el borde, el suelo cruje.",
              "Tú alcanzas la cima, tú examinas la roca y limpias el polvo."):
        assert {h["categoria"] for h in H(t)} <= validas, t
        assert H(t) == P.detectar_usurpacion(t, "", None) or all(h["categoria"] in validas for h in H(t))


# ═════════════════════ CONTRATO DEL API ═════════════════════

def test_contrato_campos_y_offsets():
    dm = "El aire huele a cera. Decides huir por la ventana."
    h = uno(H(dm, ""), "VOLICION")
    for k in ("categoria", "confianza", "verbo_lema", "evidencia", "inicio", "fin",
              "tirada_declarada", "declarada"):
        assert k in h, f"falta el campo {k}"
    assert h["confianza"] in ("alta", "media")
    assert isinstance(h["tirada_declarada"], bool) and isinstance(h["declarada"], bool)
    assert dm[h["inicio"]:h["fin"]].lower() == "decides"
    assert "Decides huir" in h["evidencia"] and "cera" not in h["evidencia"]


def test_determinismo_y_orden_por_posicion():
    dm = "Abres la puerta. Comprendes que es tarde. Sientes miedo."
    a, b = H(dm), H(dm)
    assert a == b and len(a) >= 3
    assert [h["inicio"] for h in a] == sorted(h["inicio"] for h in a)


def test_funciona_sin_nlp():
    hs = P.detectar_usurpacion("Decides huir.", "", None)
    assert cats(hs) == ["VOLICION"]


def test_texto_vacio_o_none():
    assert P.detectar_usurpacion("", "", NLP) == []
    assert P.detectar_usurpacion(None, None, NLP) == []
    assert P.narra_muerte_pj("", NLP) is None


def test_lexicon_json_documenta_fuentes():
    lex = json.loads((AQUI / "lexicon_persona2.json").read_text(encoding="utf-8"))
    fuentes = lex["_fuentes"]
    assert "elaboración propia" in fuentes["general"].lower()
    assert "paper" in fuentes["general"].lower()  # aclara que NO viene de un paper
    for k in ("verbos", "excluidos", "sustantivos"):
        assert k in lex, k
    for cat in ("VOLICION", "COGNICION", "EMOCION", "HABLA", "ACCION"):
        assert lex["verbos"][cat], cat
        assert cat in fuentes["listas"], f"falta fuente de la lista {cat}"


# ═════════════════════ runner plano ═════════════════════

def _correr():
    pruebas = [(n, f) for n, f in list(globals().items())
               if n.startswith("test_") and callable(f)]
    fallos = []
    for n, f in pruebas:
        try:
            f()
            print(f"  ok    {n}")
        except Exception as e:  # noqa: BLE001
            fallos.append((n, e))
            tb = traceback.extract_tb(e.__traceback__)[-1]
            print(f"  FALLA {n}: {type(e).__name__}: {e} (línea {tb.lineno})")
    print(f"\n{len(pruebas) - len(fallos)}/{len(pruebas)} pruebas pasan")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(_correr())
