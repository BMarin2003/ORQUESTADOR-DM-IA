"""
Pruebas unitarias del reporte v2 (instrumentos recalculados sobre texto NORMALIZADO).
TDD: este archivo se escribe ANTES que normalizacion.py / recalcular.py / comparar_v1_v2.py.

    PYTHONUTF8=1 py -m pytest experimento/scripts/reporte_v2/test_reporte_v2.py -q -p no:cacheprovider

Bloques:
  A. normalizacion: normalizar_turno / detectar_residuos con casos REALES de G1 y G2
     (turnos de la base, recortados) y una medición sobre 3000 turnos G1 reales.
  B. recalcular: filas por turno, sanidad G2 (v1 = v2), reanudación.
  C. comparar_v1_v2: Hodges-Lehmann, rank-biserial, Wilcoxon exacto, bootstrap, clasificación.
"""
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
for _p in (AQUI, RAIZ / "experimento" / "scripts", RAIZ / "experimento" / "scripts" / "sensibilidad", RAIZ / "motor" / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


# ======================================================================
# Casos reales (turnos de turn_log, par 18 / par 07 / par 21 / par 26)
# ======================================================================
G1_ETIQUETAS_SOLAS = (
    "narrativa\nEl efecto es inmediato. Los estudiantes, que hace un segundo se sentían los dueños del campus, "
    "retroceden atropelladamente hasta chocar contra una columna cubierta de musgo.\n\n"
    "El grupo se queda congelado, encajonados contra la piedra fría.\n\n"
    "mecanica\nIntimidación: Éxito (16 vs CD 15). El grupo de alumnos ha quedado coaccionado.\n\n"
    "presion\nLos estudiantes están a punto de quebrarse, pero si no presionas ahora, alguno podría huir.")
G1_ETIQUETAS_SOLAS_ESPERADO = (
    "El efecto es inmediato. Los estudiantes, que hace un segundo se sentían los dueños del campus, "
    "retroceden atropelladamente hasta chocar contra una columna cubierta de musgo.\n\n"
    "El grupo se queda congelado, encajonados contra la piedra fría.\n\n"
    "Los estudiantes están a punto de quebrarse, pero si no presionas ahora, alguno podría huir.")

# Par 12 (campaña 5f0506…), turnos 198-236 y 674+: etiquetas en negrita markdown y tirada «(11/10)».
G1_NEGRITA = (
    "**narrativa**\nDesde el refugio entre las cajas de carga, el mundo se reduce a un laberinto de sombras "
    "oxidadas. Selmira no retrocede ni se muestra perturbada por la distancia.\n\n"
    "**mecanica**\nPercepción: Éxito (11/10).\n\n"
    "**presion**\nSelmira ha dejado claro que el tiempo es un recurso limitado.")
G1_NEGRITA_ESPERADO = (
    "Desde el refugio entre las cajas de carga, el mundo se reduce a un laberinto de sombras "
    "oxidadas. Selmira no retrocede ni se muestra perturbada por la distancia.\n\n"
    "Selmira ha dejado claro que el tiempo es un recurso limitado.")

# Par 18, turno 375: «Mecanica» con mayúscula inicial (prosa() solo reconoce minúsculas).
G1_MECANICA_MAYUSCULA = (
    "narrativa\nTrata el documento como una pieza de museo.\n\n"
    "Mecanica\nPerspicacia: Éxito (16 vs CD 15)\n\n"
    "presion\nLa calma es superficial; cualquier distracción podría romper el equilibrio.")
# Par 21, turno 858: «Mecánica» con acento y la tirada escrita «15 vs CD 15 (Éxito)».
G1_MECANICA_ACENTO = (
    "narrativa\nLa puerta reforzada ha comenzado su descenso lento.\n\n"
    "Mecánica\nPercepción: 15 vs CD 15 (Éxito)\n\n"
    "presion\nLa puerta sigue bajando; en pocos segundos el cierre será total.")

# Par 13, turno 1149: el modelo devolvió el JSON crudo.
G1_JSON = ('{\n  "narrativa": "La mirada se desplaza hacia el suelo.\\n\\nBaldemar Cruz no se mueve. '
           'Su voz surge seca: \\"Sigue mirando las piedras\\".",\n'
           '  "mecanica": "Percepción: Fallo (19 vs CD 20). No encuentras nada.",\n'
           '  "presion": "La paciencia de Baldemar se ha agotado."\n}')
G1_JSON_ESPERADO = ('La mirada se desplaza hacia el suelo.\n\nBaldemar Cruz no se mueve. '
                    'Su voz surge seca: "Sigue mirando las piedras".\n\nLa paciencia de Baldemar se ha agotado.')

G2_REAL = (
    "Honorio parpadea lentamente, manteniendo la mirada mientras el silencio se prolonga. Su expresión no "
    "cambia; el cansancio que habita en sus ojos parece actuar como un escudo natural.\n\n"
    "—Mira, chaval, he estado aquí desde que las gárgolas eran gatitos de piedra —dice con una monotonía "
    "absoluta—. No hay \"soluciones rápidas\" en este edificio, solo hay formularios más largos.")
G2_NEGRITA_LEGITIMA = ("El nombre subrayado es **Elias Thorne**. Al repasarlo, los fragmentos de memoria "
                       "encajan con precisión.")


# ======================================================================
# A. normalizacion
# ======================================================================
@pytest.fixture
def nz():
    import normalizacion
    return normalizacion


def test_g1_quita_etiquetas_y_bloque_mecanica(nz):
    assert nz.normalizar_turno(G1_ETIQUETAS_SOLAS, "G1") == G1_ETIQUETAS_SOLAS_ESPERADO


def test_g1_etiquetas_en_negrita_markdown_y_tirada_con_barra(nz):
    assert nz.normalizar_turno(G1_NEGRITA, "G1") == G1_NEGRITA_ESPERADO


def test_g1_etiqueta_con_mayuscula_o_acento(nz):
    a = nz.normalizar_turno(G1_MECANICA_MAYUSCULA, "G1")
    b = nz.normalizar_turno(G1_MECANICA_ACENTO, "G1")
    assert a == ("Trata el documento como una pieza de museo.\n\n"
                 "La calma es superficial; cualquier distracción podría romper el equilibrio.")
    assert b == ("La puerta reforzada ha comenzado su descenso lento.\n\n"
                 "La puerta sigue bajando; en pocos segundos el cierre será total.")


def test_g1_json_crudo_se_desempaqueta(nz):
    assert nz.normalizar_turno(G1_JSON, "G1") == G1_JSON_ESPERADO


def test_g1_sin_bloque_presion(nz):
    txt = "narrativa\nCruzas la sala.\n\nmecanica\nAtletismo: Fallo (5 vs CD 10)."
    assert nz.normalizar_turno(txt, "G1") == "Cruzas la sala."


def test_g1_linea_de_tirada_suelta_sin_etiqueta(nz):
    txt = "Cruzas la sala.\n\nPercepción: Éxito (10 vs CD 10)\n\nOtra frase."
    assert nz.normalizar_turno(txt, "G1") == "Cruzas la sala.\n\nOtra frase."


def test_g1_no_borra_prosa_legitima_con_dos_puntos(nz):
    txt = ("Nota: la puerta está cerrada.\n\nTe dice: Éxito rotundo, amigo, y sonríe.\n\n"
           "El guardia grita: Fallo tuyo, no mío (dice sin convicción).")
    assert nz.normalizar_turno(txt, "G1") == txt


def test_g1_texto_sin_formato_solo_se_recorta(nz):
    assert nz.normalizar_turno("  \n" + G2_REAL + "\n\n ", "G1") == G2_REAL


def test_g1_es_idempotente(nz):
    for x in (G1_ETIQUETAS_SOLAS, G1_NEGRITA, G1_MECANICA_MAYUSCULA, G1_MECANICA_ACENTO, G1_JSON):
        una = nz.normalizar_turno(x, "G1")
        assert nz.normalizar_turno(una, "G1") == una


def test_g1_vacio_y_none(nz):
    assert nz.normalizar_turno(None, "G1") == ""
    assert nz.normalizar_turno("", "G1") == ""
    assert nz.normalizar_turno("   \n ", "G1") == ""


@pytest.mark.parametrize("texto", [
    G2_REAL, G2_NEGRITA_LEGITIMA,
    "narrativa\nEsto es prosa de G2 que casualmente trae una etiqueta.\n\nmecanica\nPercepción: Éxito (10 vs CD 10)",
    "# Titulo\n\nTexto con encabezado.\n\n**mecanica**\nAtletismo: Fallo (5 vs CD 10).",
    '{"narrativa": "x", "mecanica": "y"}',
])
def test_g2_identidad_salvo_strip(nz, texto):
    assert nz.normalizar_turno(texto, "G2") == texto.strip()
    assert nz.normalizar_turno("  " + texto + " \n", "G2") == texto.strip()


def test_g2_none(nz):
    assert nz.normalizar_turno(None, "G2") == ""


def test_prosa_original_deja_residuos_en_los_casos_reales(nz):
    """Caracterización (por qué hace falta normalizar_turno): prosa() de validacion_generar.py
    falla con la negrita, con «Mecanica» capitalizada y con el JSON crudo."""
    from validacion_generar import prosa
    for caso in (G1_NEGRITA, G1_MECANICA_MAYUSCULA, G1_MECANICA_ACENTO, G1_JSON):
        assert any(nz.detectar_residuos(prosa(caso, "G1")).values()), caso[:40]
    assert not any(nz.detectar_residuos(prosa(G1_ETIQUETAS_SOLAS, "G1")).values())


def test_detectar_residuos_categorias(nz):
    r = nz.detectar_residuos(G1_ETIQUETAS_SOLAS)
    assert r["etiquetas"] and r["linea_tirada"] and r["patron_habilidad"]
    assert not r["encabezados"] and not r["json_crudo"]
    assert nz.detectar_residuos("**narrativa**\nx")["etiquetas"]
    assert nz.detectar_residuos("Mecánica\nx")["etiquetas"]
    assert nz.detectar_residuos("Aviso\n\n# Titulo\n\nTexto")["encabezados"]
    assert nz.detectar_residuos("Aviso\n\n## Titulo\n\nTexto")["encabezados"]
    assert nz.detectar_residuos('{"narrativa": "x"}')["json_crudo"]
    assert nz.detectar_residuos("Percepción: 15 vs CD 15 (Éxito)")["linea_tirada"]
    assert nz.detectar_residuos("Percepción: Éxito (11/10).")["linea_tirada"]
    limpio = nz.detectar_residuos(G2_REAL)
    assert not any(limpio.values())
    assert not any(nz.detectar_residuos(G2_NEGRITA_LEGITIMA).values())    # negrita en el cuerpo no es formato G1
    # «Mecánica» dentro de una frase no es una etiqueta
    assert not nz.detectar_residuos("Una disciplina gélida y mecánica, una pared de indiferencia.")["etiquetas"]


def test_medir_residuos_cuenta_fracciones(nz):
    textos = [G1_ETIQUETAS_SOLAS, G1_NEGRITA, G2_REAL, G2_REAL]
    m = nz.medir_residuos(textos, lambda x: x)
    assert m["n"] == 4 and m["con_algun_residuo"] == 2 and m["etiquetas"] == 2
    assert m["fraccion"]["etiquetas"] == pytest.approx(0.5)
    m2 = nz.medir_residuos(textos, lambda x: nz.normalizar_turno(x, "G1"))
    assert m2["con_algun_residuo"] == 0


# ---- muestra real (semilla 20260920) ---------------------------------
def _conexion_o_skip():
    try:
        import datos
        return datos.abrir_conexion()
    except Exception as e:                                  # pragma: no cover
        pytest.skip(f"sin base de datos: {e!r}")


def test_muestra_real_g1_normalizada_no_deja_residuos(nz):
    conn = _conexion_o_skip()
    with conn:
        muestra = nz.muestrear_turnos(conn, "G1", n=3000, semilla=20260920)
    assert len(muestra) == 3000
    assert len({(m["campaign_id"], m["turn_id"]) for m in muestra}) == 3000     # sin repetidos
    textos = [m["dm_output"] for m in muestra]
    m = nz.medir_residuos(textos, lambda x: nz.normalizar_turno(x, "G1"))
    assert m["con_algun_residuo"] == 0, m
    # y donde prosa() ya estaba limpia, normalizar_turno da EXACTAMENTE lo mismo
    from validacion_generar import prosa
    for x in textos:
        p = prosa(x, "G1")
        if not any(nz.detectar_residuos(p).values()):
            assert nz.normalizar_turno(x, "G1") == p
    # la normalización nunca deja un turno vacío
    assert all(nz.normalizar_turno(x, "G1") for x in textos)


def test_muestra_real_g2_identidad(nz):
    conn = _conexion_o_skip()
    with conn:
        muestra = nz.muestrear_turnos(conn, "G2", n=3000, semilla=20260920)
    for m in muestra:
        assert nz.normalizar_turno(m["dm_output"], "G2") == (m["dm_output"] or "").strip()


def test_g1_texto_antes_de_la_primera_etiqueta_se_conserva(nz):
    txt = "Prólogo del turno.\nnarrativa\nCruzas la sala.\n\nmecanica\nAtletismo: Fallo (5 vs CD 10).\n\npresion\nAlguien te sigue."
    assert nz.normalizar_turno(txt, "G1") == "Prólogo del turno.\n\nCruzas la sala.\n\nAlguien te sigue."


# ======================================================================
# B. recalcular
# ======================================================================
@pytest.fixture
def rc():
    import recalcular
    return recalcular


def _ctx_base(brazo="G1"):
    import instrumentos_texto as it
    return it.Contexto(
        pj_nombre="Ilvard",
        entidades=[{"tipo": "character", "nombre": "Ilvard"},
                   {"tipo": "npc", "nombre": "Selmira"},
                   {"tipo": "location", "nombre": "Muelle Siete"}],
        estados_pnj={}, brazo=brazo)


def test_columnas_empiezan_por_turn_id_y_van_en_pares_v1_v2(rc):
    cols = rc.COLUMNAS
    assert cols[0] == "turn_id"
    for instr in rc.INSTRUMENTOS:
        assert f"{instr}_v1" in cols and f"{instr}_v2" in cols
        assert cols.index(f"{instr}_v2") == cols.index(f"{instr}_v1") + 1
    assert set(rc.INSTRUMENTOS) >= {"qn1_ttr", "qn1_ngram_repeticion", "qn1_legibilidad_fh",
                                    "cl2_lugar_jaccard_similarity", "cr2_entidad_grafo_densidad",
                                    "cr2_n_nombres_no_reconocidos", "cr2_nombres_no_reconocidos",
                                    "grammaticality_lt"}


def test_v1_desde_fila_de_turn_validation(rc):
    from decimal import Decimal
    fila = {"qn1_ttr": Decimal("0.649"), "qn1_ngram_repeticion": Decimal("0.011"),
            "qn1_legibilidad_fh": Decimal("59.24"), "cl2_lugar_jaccard_similarity": Decimal("0.100"),
            "cr2_entidad_grafo_densidad": None, "cr2_nombres_no_reconocidos": ["Fallo", "Percepción"]}
    v1 = rc.v1_de_fila(fila)
    assert v1["qn1_ttr"] == 0.649 and v1["qn1_legibilidad_fh"] == 59.24
    assert v1["cr2_entidad_grafo_densidad"] is None
    assert v1["cr2_n_nombres_no_reconocidos"] == 2 and v1["cr2_nombres_no_reconocidos"] == 1
    assert rc.v1_de_fila(dict(fila, cr2_nombres_no_reconocidos=[]))["cr2_nombres_no_reconocidos"] == 0
    assert rc.v1_de_fila(dict(fila, cr2_nombres_no_reconocidos=None))["cr2_n_nombres_no_reconocidos"] == 0


def test_v2_g1_quita_el_artefacto_de_nombres_no_reconocidos(rc):
    """La línea de tirada («Percepción: Éxito…») cuenta como nombre propio en el crudo (v1)."""
    import instrumentos_texto as it
    ctx = _ctx_base("G1")
    crudo = "narrativa\nSelmira camina por el Muelle Siete sin mirar atrás.\n\nmecanica\nPercepción: Éxito (11 vs CD 10).\n\npresion\nLa patrulla se acerca."
    assert it.cr2_nombres_no_reconocidos(crudo, ctx) is True
    fila = rc.calcular_fila(5, crudo, "Turno anterior con Selmira.", ctx, {}, "G1")
    assert fila["cr2_nombres_no_reconocidos_v1"] is None             # v1 viene de turn_validation (aquí vacío)
    assert fila["cr2_nombres_no_reconocidos_v2"] == 0
    assert fila["cr2_n_nombres_no_reconocidos_v2"] == 0


def test_calcular_fila_g2_v2_igual_a_recalculo_crudo(rc):
    import instrumentos_texto as it
    ctx = _ctx_base("G2")
    txt = G2_REAL + " Selmira asiente en el Muelle Siete."
    prev = "Selmira observa el Muelle Siete desde lejos."
    esperado = it.calcular(txt, ctx.copia(escena_anterior=prev),
                           nombres={"qn1_ttr", "qn1_ngram_repeticion", "qn1_legibilidad_fh",
                                    "cl2_lugar_jaccard_similarity", "cr2_entidad_grafo_densidad"})
    fila = rc.calcular_fila(7, txt, prev, ctx, {}, "G2")
    for k, v in esperado.items():
        assert fila[f"{k}_v2"] == v, k
    assert fila["turn_id"] == 7


def test_jaccard_v2_usa_la_escena_anterior_normalizada(rc):
    ctx = _ctx_base("G1")
    prev_crudo = "narrativa\nSelmira vigila la calle.\n\nmecanica\nPercepción: Éxito (11 vs CD 10).\n\npresion\nLa patrulla llega."
    txt_crudo = "narrativa\nSelmira vigila la calle.\n\nmecanica\nPercepción: Éxito (12 vs CD 10).\n\npresion\nLa patrulla llega."
    fila = rc.calcular_fila(9, txt_crudo, prev_crudo, ctx, {}, "G1")
    assert fila["cl2_lugar_jaccard_similarity_v2"] == 1.0          # mismo texto de fondo, sin formato


def test_lt_solo_cuando_se_pide_y_una_llamada_si_raw_igual_norm(rc):
    llamadas = []
    fake = lambda t: llamadas.append(t) or 0.9
    ctx = _ctx_base("G2")
    f = rc.calcular_fila(10, G2_REAL, "x", ctx, {}, "G2", lt=fake)
    assert f["grammaticality_lt_v1"] == 0.9 and f["grammaticality_lt_v2"] == 0.9 and len(llamadas) == 1
    llamadas.clear()
    f = rc.calcular_fila(10, G1_ETIQUETAS_SOLAS, "x", _ctx_base("G1"), {}, "G1", lt=fake)
    assert len(llamadas) == 2 and llamadas[0] != llamadas[1]
    f = rc.calcular_fila(10, G2_REAL, "x", ctx, {}, "G2", lt=None)
    assert f["grammaticality_lt_v1"] is None and f["grammaticality_lt_v2"] is None


def test_turnos_para_lt_uno_de_cada_n(rc):
    assert [t for t in range(1, 41) if rc.toca_lt(t, 10)] == [10, 20, 30, 40]
    assert [t for t in range(1, 6) if rc.toca_lt(t, 1)] == [1, 2, 3, 4, 5]


def test_sanidad_g2_detecta_y_cuantifica(rc):
    ok = {"turn_id": 2, "qn1_ttr_v1": 0.7, "qn1_ttr_v2": 0.7, "qn1_legibilidad_fh_v1": 59.24,
          "qn1_legibilidad_fh_v2": 59.2400001, "cr2_n_nombres_no_reconocidos_v1": 0, "cr2_n_nombres_no_reconocidos_v2": 0}
    mal = {"turn_id": 3, "qn1_ttr_v1": 0.7, "qn1_ttr_v2": 0.71, "qn1_legibilidad_fh_v1": None,
           "qn1_legibilidad_fh_v2": 50.0, "cr2_n_nombres_no_reconocidos_v1": 0, "cr2_n_nombres_no_reconocidos_v2": 0}
    s = rc.sanidad_filas([ok, mal])
    assert s["qn1_ttr"]["n"] == 2 and s["qn1_ttr"]["discrepancias"] == 1
    assert s["qn1_legibilidad_fh"]["discrepancias"] == 1          # None vs valor
    assert s["cr2_n_nombres_no_reconocidos"]["discrepancias"] == 0
    assert s["qn1_ttr"]["ejemplos"][0]["turn_id"] == 3


def test_csv_roundtrip_atomico_y_reanudacion(rc, tmp_path):
    filas = [{c: None for c in rc.COLUMNAS} | {"turn_id": t, "qn1_ttr_v1": 0.5, "qn1_ttr_v2": 0.6,
                                               "cr2_nombres_no_reconocidos_v1": 1} for t in (1, 2, 3)]
    ruta = tmp_path / "par07_G1.csv"
    assert not rc.csv_completo(ruta, 3)
    rc.escribir_csv(ruta, filas)
    assert rc.csv_completo(ruta, 3) and not rc.csv_completo(ruta, 4)
    assert not list(tmp_path.glob("*.tmp"))
    leidas = rc.leer_csv(ruta)
    assert [f["turn_id"] for f in leidas] == [1, 2, 3]
    assert leidas[0]["qn1_ttr_v2"] == 0.6 and leidas[0]["qn1_ttr_v1"] == 0.5
    assert leidas[0]["qn1_legibilidad_fh_v1"] is None and leidas[0]["cr2_nombres_no_reconocidos_v1"] == 1
    assert not rc.csv_tiene_lt(ruta)
    filas[1]["grammaticality_lt_v1"] = 0.9
    rc.escribir_csv(ruta, filas)
    assert rc.csv_tiene_lt(ruta)


def test_procesar_campana_real_g2_v1_igual_v2_y_g1_distinto(rc, tmp_path):
    import datos
    pares = datos.cargar_pares()
    p = pares[0]
    with datos.abrir_conexion() as conn:
        rg2 = rc.procesar_campana(conn, p["par"], "G2", p["campaign_g2"], tmp_path, hasta=120)
        rg1 = rc.procesar_campana(conn, p["par"], "G1", p["campaign_g1"], tmp_path, hasta=120)
    assert len(rg2) == 120 and len(rg1) == 120
    s2 = rc.sanidad_filas(rg2)
    assert all(v["discrepancias"] == 0 for v in s2.values()), s2
    s1 = rc.sanidad_filas(rg1)
    assert s1["cr2_nombres_no_reconocidos"]["discrepancias"] > 100     # el artefacto: v1 marcaba casi todo
    assert sum(f["cr2_nombres_no_reconocidos_v2"] for f in rg1) < 60   # y v2 ya no
    # reanudación: la segunda llamada no vuelve a calcular (devuelve None = saltada)
    assert rc.procesar_campana(None, p["par"], "G1", p["campaign_g1"], tmp_path, hasta=120) is None


def test_control_g1_recalculo_sobre_texto_crudo_reproduce_v1(rc, tmp_path):
    """Control del propio recálculo en G1: con el normalizador identidad (texto crudo) el contexto
    reconstruido reproduce lo guardado por el motor; así la diferencia v1 -> v2 es solo el formato."""
    import datos
    p = datos.cargar_pares()[0]
    with datos.abrir_conexion() as conn:
        filas = rc.procesar_campana(conn, p["par"], "G1", p["campaign_g1"], tmp_path, hasta=150,
                                    normalizador=lambda x, brazo: (x or "").strip())
    s = rc.sanidad_filas(filas)
    assert all(v["discrepancias"] == 0 for v in s.values()), s


def test_reanudacion_completa_solo_languagetool(rc, tmp_path):
    """Primero la corrida rápida (sin LT); luego --con-lt no recalcula todo: solo añade LT
    en 1 de cada N turnos al CSV existente, y una tercera llamada ya no hace nada."""
    import datos
    p = datos.cargar_pares()[0]
    llamadas = []
    fake = lambda t: llamadas.append(t) or 0.5
    with datos.abrir_conexion() as conn:
        base = rc.procesar_campana(conn, p["par"], "G1", p["campaign_g1"], tmp_path, hasta=30)
        assert len(base) == 30 and not rc.csv_tiene_lt(tmp_path / rc.nombre_csv(p["par"], "G1"))
        v2_antes = [f["qn1_ttr_v2"] for f in base]
        filas = rc.procesar_campana(conn, p["par"], "G1", p["campaign_g1"], tmp_path, con_lt=True,
                                    lt_cada=10, hasta=30, lt_fn=fake)
        assert [f["turn_id"] for f in filas if f["grammaticality_lt_v1"] is not None] == [10, 20, 30]
        assert [f["qn1_ttr_v2"] for f in filas] == v2_antes            # lo demás no se toca
        assert rc.csv_tiene_lt(tmp_path / rc.nombre_csv(p["par"], "G1"))
        assert len(llamadas) == 6                                       # 3 turnos x (crudo, normalizado)
        assert rc.procesar_campana(conn, p["par"], "G1", p["campaign_g1"], tmp_path, con_lt=True,
                                   lt_cada=10, hasta=30, lt_fn=fake) is None


# ======================================================================
# C. comparar_v1_v2
# ======================================================================
@pytest.fixture
def cp():
    import comparar_v1_v2
    return comparar_v1_v2


def _wilcoxon_bruto(d):
    """p bilateral exacta por enumeración de los 2^n signos (con rangos medios y ceros descartados)."""
    import itertools
    import numpy as np
    d = [x for x in d if x != 0]
    n = len(d)
    if n == 0:
        return 1.0
    a = np.abs(np.array(d, dtype=float))
    orden = np.argsort(a, kind="mergesort")
    rangos = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and a[orden[j + 1]] == a[orden[i]]:
            j += 1
        rangos[orden[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    total = rangos.sum()
    obs = abs(rangos[np.array(d) > 0].sum() - total / 2)
    ge = sum(1 for signos in itertools.product((0, 1), repeat=n)
             if abs(sum(r for r, s in zip(rangos, signos) if s) - total / 2) >= obs - 1e-9)
    return ge / 2 ** n


def test_hodges_lehmann_es_la_mediana_de_los_promedios_de_walsh(cp):
    assert cp.hodges_lehmann([1, 2, 3]) == pytest.approx(2.0)
    assert cp.hodges_lehmann([1, 2, 6]) == pytest.approx(2.75)
    assert cp.hodges_lehmann([-3]) == pytest.approx(-3.0)
    assert cp.hodges_lehmann([0, 0, 0]) == 0.0


def test_rank_biserial_pareada(cp):
    assert cp.rank_biserial_pareada([1, 2, 3]) == pytest.approx(1.0)
    assert cp.rank_biserial_pareada([-1, -2]) == pytest.approx(-1.0)
    assert cp.rank_biserial_pareada([1, -2, 3]) == pytest.approx((4 - 2) / 6)
    assert cp.rank_biserial_pareada([1, -1, 2]) == pytest.approx(0.5)      # empate: rangos medios 1.5, 1.5, 3
    assert cp.rank_biserial_pareada([0, 0, 1]) == pytest.approx(1.0)       # ceros descartados
    assert cp.rank_biserial_pareada([0, 0]) == 0.0


@pytest.mark.parametrize("d", [
    [1, 2, 3, 4, 5], [1, -2, 3, -4, 5, 0.5], [1, -1, 2, -2, 3, 3, -3, 0, 0],
    [0.3, -0.1, 0.25, -0.25, 0.7, 0.1, -0.05, 0.9], [-1.0, -2.0, -3.0]])
def test_wilcoxon_exacto_coincide_con_la_enumeracion(cp, d):
    assert cp.wilcoxon_exacto(d)["p"] == pytest.approx(_wilcoxon_bruto(d), abs=1e-12)


def test_wilcoxon_exacto_casos_conocidos(cp):
    assert cp.wilcoxon_exacto([1, 2, 3, 4, 5])["p"] == pytest.approx(2 / 32)
    assert cp.wilcoxon_exacto([1] * 21)["p"] == pytest.approx(2 / 2 ** 21)
    assert cp.wilcoxon_exacto([0, 0, 0])["p"] == 1.0
    w = cp.wilcoxon_exacto([1, 2, -3])
    assert w["n_efectivo"] == 3 and w["W_mas"] == pytest.approx(3.0) and w["W_menos"] == pytest.approx(3.0)


def test_bootstrap_pares_es_reproducible_y_acotado(cp):
    d = [0.1, 0.4, -0.2, 0.3, 0.5, 0.05, -0.1, 0.2, 0.6, 0.3]
    a = cp.ic_bootstrap_pares(d, cp.rank_biserial_pareada, semilla=1, B=500)
    b = cp.ic_bootstrap_pares(d, cp.rank_biserial_pareada, semilla=1, B=500)
    assert a == b and -1 <= a[0] <= a[1] <= 1
    lo, hi = cp.ic_bootstrap_pares([1] * 21, cp.rank_biserial_pareada, semilla=1, B=200)
    assert lo == hi == 1.0


def test_medias_por_campana_omite_none_y_turnos_previos_al_2(cp):
    filas = [{"turn_id": 1, "qn1_ttr_v1": 9.0, "qn1_ttr_v2": 9.0},
             {"turn_id": 2, "qn1_ttr_v1": 0.5, "qn1_ttr_v2": 0.6},
             {"turn_id": 3, "qn1_ttr_v1": None, "qn1_ttr_v2": None},
             {"turn_id": 4, "qn1_ttr_v1": 0.7, "qn1_ttr_v2": 0.8}]
    m = cp.media_campana(filas, "qn1_ttr")
    assert m["v1"] == pytest.approx(0.6) and m["v2"] == pytest.approx(0.7) and m["n"] == 2


def _res(hl, p, r=0.5):
    return {"hl": hl, "p_holm": p, "rb": r}


def test_clasificar_cambio(cp):
    assert "signo" in cp.clasificar_cambio(_res(-0.9, 0.001), _res(0.05, 0.8))["banderas"]
    c = cp.clasificar_cambio(_res(0.5, 0.001), _res(0.55, 0.001))
    assert c["banderas"] == [] and c["titular"] == "sin cambio material"
    assert cp.clasificar_cambio(_res(0.5, 0.001), _res(0.2, 0.001))["banderas"] == ["tamaño"]
    d = cp.clasificar_cambio(_res(0.5, 0.001), _res(0.45, 0.4))
    assert d["banderas"] == ["desaparece"] and d["titular"] == "desaparece"
    a = cp.clasificar_cambio(_res(0.1, 0.4), _res(0.11, 0.001))
    assert a["banderas"] == ["aparece"]
    s = cp.clasificar_cambio(_res(-0.5, 0.001), _res(0.5, 0.001))
    assert s["banderas"] == ["signo"] and s["titular"] == "cambia de signo"
    # el signo tiene precedencia como titular aunque también desaparezca la significancia
    m = cp.clasificar_cambio(_res(-0.9, 0.001), _res(0.05, 0.8))
    assert m["titular"] == "cambia de signo" and set(m["banderas"]) == {"signo", "desaparece"}


def test_analizar_sintetico_desaparece_el_efecto(cp, rc, tmp_path):
    """G1 = G2 + 1 en v1 y G1 = G2 en v2 en las 21 parejas: v1 muy significativo, v2 nulo."""
    import datos
    pares = datos.cargar_pares()
    for k, p in enumerate(pares):
        for brazo in ("G1", "G2"):
            filas = []
            for t in range(1, 6):
                base = 0.5 + 0.01 * k + 0.001 * t
                f = {c: None for c in rc.COLUMNAS}
                f.update(turn_id=t, qn1_ttr_v2=base, qn1_ttr_v1=base + (1.0 if brazo == "G1" else 0.0))
                filas.append(f)
            rc.escribir_csv(tmp_path / rc.nombre_csv(p["par"], brazo), filas)
    res = cp.analizar(tmp_path, pares, instrumentos=["qn1_ttr"], B=300)
    r = res["instrumentos"]["qn1_ttr"]
    assert r["v1"]["n_pares"] == 21 and r["v2"]["n_pares"] == 21
    assert r["v1"]["hl"] == pytest.approx(1.0) and r["v1"]["rb"] == pytest.approx(1.0)
    assert r["v1"]["p"] == pytest.approx(2 / 2 ** 21)
    assert r["v2"]["hl"] == pytest.approx(0.0, abs=1e-12) and r["v2"]["p"] == 1.0
    assert r["cambio"]["titular"] == "desaparece" and "tamaño" in r["cambio"]["banderas"]
    assert r["v1"]["media_g1"] == pytest.approx(r["v1"]["media_g2"] + 1.0)


def test_tipografia_dialogo_cuenta_raya_y_comillas(nz):
    textos = ['—Hola —dice.\n\nSigue.', 'Dice: "no pasarás por aquí".', 'Sin diálogo.', '—Ah.\n\n"Bien dicho", añade.']
    t = nz.tipografia_dialogo(textos)
    assert t["n"] == 4
    assert t["raya"] == pytest.approx(0.5) and t["comillas"] == pytest.approx(0.5)


def test_residuos_por_par_agrupa_por_par(nz):
    from validacion_generar import prosa
    filas = [("12", G1_NEGRITA), ("12", G1_NEGRITA), ("13", G1_JSON), ("13", G1_ETIQUETAS_SOLAS)]
    r = nz.residuos_por_par(filas, lambda x: prosa(x, "G1"))
    assert r == {"12": 2, "13": 1}
