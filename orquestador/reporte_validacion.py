"""
REPORTE DE VALIDACIÓN — agregado por campaña, sobre lo que ya escribió
turn_validation turno a turno.

Tres piezas, cada una documentada en QM - Respaldo bibliografico
instrumentos deterministicos.md (sección "Deep Research" y "Pendiente"):

  1. Resumen de turn_validation: cuántos turnos tuvieron problema en cada
     chequeo Tier 1/2, promedio de los proxies Tier 3, cuántos quedaron
     "revisar" (Tier 4). Longitudinal en sentido débil: agrega el turno a
     turno, no rastrea causalidad entre turnos.

  2. Detector de bucles/estancamiento: reconstruye el camino de
     ubicaciones REALMENTE visitadas (no el espacio completo de
     posibilidades, que no existe en un sistema de texto libre -- ver
     "Twine/Symmetry" en la nota) a partir de qué ubicaciones conocidas
     menciona la narración de cada turno, y corre detección de
     componentes fuertemente conexos (SCC) sobre el grafo de transiciones
     realizadas. Un SCC de tamaño >1 = la campaña entra y sale de un
     mismo conjunto cerrado de lugares sin llegar a ninguno nuevo.
     Inspirado en Puchalski & Woźna-Szcześniak (Symmetry 2026), pero
     reconstruido desde el historial real, no desde un grafo Twee
     autorado -- limitación explícita: solo ve el camino recorrido, no
     todo el espacio de posibilidades.

  3. Relojes disparados no reconocidos: para cada faction_clock que ya
     disparó (fired_at_turn no nulo), busca si el turno siguiente
     menciona la facción o algo de la agenda/on_fire_event. Si no, se
     marca como "no reconocido" -- la pieza de validación LONGITUDINAL-
     CAUSAL fuerte que turn_validation no cubre por diseño (compara
     contra el estado ACTUAL, no si una promesa/consecuencia temprana se
     resolvió más adelante).

Todo Tier 3/"revisar" -- descriptivo, nunca pass/fail. Ver "Precaución
metodológica -- Ley de Goodhart" en la nota: estos umbrales/heurísticas
deben tratarse igual que los de turn_validation, no ajustarse después de
ver qué arquitectura "gana".

Uso:
  py orquestador\\reporte_validacion.py
  py orquestador\\reporte_validacion.py --campaign-id <uuid>
"""

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
import db as bd        # noqa: E402


def paso(titulo):
    print(f"\n{'─'*74}\n{titulo}\n{'─'*74}")


# ---------------------------------------------------------------- 1. resumen

# Columnas booleanas Tier 1/2 (problema real) y Tier 4 (revisar) que
# turn_validation puede tener en `true`. Numéricas Tier 3 aparte.
COLUMNAS_PROBLEMA = [
    "cr1_veredicto_contradice_narracion",
    "qn2_pj_piensa_narrado",
    "cl2_pnj_inactivo_actua",
    "cl2_pc_hp_contradice_narracion",
    "cl1_campo_inmutable_alterado",
]
COLUMNAS_REVISAR = ["qn2_pj_accion_revisar"]
COLUMNAS_PROXY = [
    "cl2_lugar_jaccard_similarity",
    "qn1_ttr",
    "qn1_ngram_repeticion",
    "qn1_legibilidad_fh",
    "cr2_entidad_grafo_densidad",
]


def resumen_turn_validation(filas):
    """filas: lista de dict (una por turno, columnas de turn_validation).
    No asume qué columnas existen -- una campaña sembrada antes de la
    sexta/séptima pasada no tendrá qn1_legibilidad_fh ni
    cr2_entidad_grafo_densidad pobladas en sus primeros turnos, y eso es
    correcto, no un error (ver nota de respaldo bibliográfico)."""
    total = len(filas)
    resumen = {"total_turnos": total, "problemas": {}, "revisar": {},
               "proxies": {}}
    for col in COLUMNAS_PROBLEMA:
        n = sum(1 for f in filas if f.get(col))
        resumen["problemas"][col] = n
    for col in COLUMNAS_REVISAR:
        n = sum(1 for f in filas if f.get(col))
        resumen["revisar"][col] = n
    for col in COLUMNAS_PROXY:
        valores = [float(f[col]) for f in filas if f.get(col) is not None]
        if valores:
            resumen["proxies"][col] = {
                "n": len(valores),
                "promedio": round(sum(valores) / len(valores), 3),
                "min": round(min(valores), 3),
                "max": round(max(valores), 3),
            }
    # cr2_nombres_no_reconocidos es text[], no numérico -- se cuenta aparte.
    con_no_reconocidos = sum(
        1 for f in filas if f.get("cr2_nombres_no_reconocidos"))
    resumen["cr2_turnos_con_nombres_no_reconocidos"] = con_no_reconocidos
    return resumen


def imprimir_resumen(resumen):
    paso("1. RESUMEN turn_validation (longitudinal débil -- agregado, "
         "no causal)")
    print(f"  {resumen['total_turnos']} turnos registrados")
    print("  Tier 1/2 (problema real), turnos afectados:")
    for col, n in resumen["problemas"].items():
        pct = (100 * n / resumen["total_turnos"]) if resumen["total_turnos"] else 0
        print(f"    {col:38s} {n:4d} ({pct:5.1f}%)")
    print("  Tier 4 (revisar, nunca problema duro):")
    for col, n in resumen["revisar"].items():
        pct = (100 * n / resumen["total_turnos"]) if resumen["total_turnos"] else 0
        print(f"    {col:38s} {n:4d} ({pct:5.1f}%)")
    print("  Tier 3 (proxy descriptivo, nunca pass/fail):")
    for col, st in resumen["proxies"].items():
        print(f"    {col:38s} n={st['n']:3d}  prom={st['promedio']:.3f}  "
              f"[{st['min']:.3f}, {st['max']:.3f}]")
    n = resumen["cr2_turnos_con_nombres_no_reconocidos"]
    print(f"  CR-2 turnos con algún nombre no reconocido: {n}")


# --------------------------------------------------- 2. bucles/estancamiento

def indice_ubicaciones(ubicaciones):
    """token/nombre completo -> nombre canónico. Igual convención que
    entidades_conocidas() en vertical_slice.py (nombre completo + cada
    palabra suelta de 3+ letras), pero restringido a ubicaciones y
    devuelto como índice en vez de solo el vocabulario, porque acá
    necesitamos saber A CUÁL ubicación pertenece cada match, no solo si
    es una entidad conocida."""
    idx = {}
    for u in ubicaciones:
        nombre = u["nombre"]
        idx[nombre] = nombre
        for tok in nombre.split():
            if len(tok) >= 3:
                idx.setdefault(tok, nombre)
    return idx


def detectar_ubicaciones(narracion, idx):
    detectadas = set()
    for token, nombre in idx.items():
        if re.search(rf"\b{re.escape(token)}\b", narracion):
            detectadas.add(nombre)
    return detectadas


def camino_realizado(turnos, idx):
    """Reduce la secuencia de turnos a la secuencia de ubicaciones
    REALIZADAS (colapsando repeticiones consecutivas -- quedarse varios
    turnos en el mismo lugar no es una arista nueva, es la misma visita
    prolongada). Un turno sin ubicación detectable hereda la anterior
    (no se re-describe el entorno en cada turno, es normal). Un turno
    con MÁS de una ubicación detectada se marca ambiguo y no cuenta como
    transición clara -- se documenta, no se fuerza una elección
    arbitraria."""
    camino = []      # [(turn_id, ubicacion)], colapsado
    ambiguos = []
    actual = None
    for fila in turnos:
        detectadas = detectar_ubicaciones(fila["dm_output"], idx)
        if len(detectadas) == 1:
            actual = next(iter(detectadas))
        elif len(detectadas) > 1:
            ambiguos.append((fila["turn_id"], sorted(detectadas)))
            # no se cambia `actual`: turno ambiguo no cuenta como
            # transición clara, se documenta y se sigue.
        # si no detecta ninguna, `actual` se mantiene igual que el
        # turno anterior (persistencia, mismo criterio que `presentes`
        # en vertical_slice.py).
        if actual is None:
            continue
        if not camino or camino[-1][1] != actual:
            camino.append((fila["turn_id"], actual))
        else:
            camino[-1] = (camino[-1][0], actual)  # mismo lugar, no crece
    return camino, ambiguos


def tarjan_scc(nodos, aristas):
    """Componentes fuertemente conexos, Tarjan clásico. Grafos de este
    reporte son chicos (decenas de ubicaciones como mucho), así que la
    versión recursiva simple basta -- no hace falta la variante
    iterativa que necesitaría un dataset de otro orden de magnitud."""
    sys.setrecursionlimit(max(1000, len(nodos) * 4))
    indice = {}
    low = {}
    en_pila = set()
    pila = []
    contador = [0]
    resultado = []

    def visitar(v):
        indice[v] = low[v] = contador[0]
        contador[0] += 1
        pila.append(v)
        en_pila.add(v)
        for w in aristas.get(v, ()):
            if w not in indice:
                visitar(w)
                low[v] = min(low[v], low[w])
            elif w in en_pila:
                low[v] = min(low[v], indice[w])
        if low[v] == indice[v]:
            componente = []
            while True:
                w = pila.pop()
                en_pila.discard(w)
                componente.append(w)
                if w == v:
                    break
            resultado.append(componente)

    for v in nodos:
        if v not in indice:
            visitar(v)
    return resultado


def detector_bucles(turnos, ubicaciones):
    idx = indice_ubicaciones(ubicaciones)
    camino, ambiguos = camino_realizado(turnos, idx)
    nombres = [u for _, u in camino]
    nodos = sorted(set(nombres))
    aristas = {n: set() for n in nodos}
    for a, b in zip(nombres, nombres[1:]):
        if a != b:
            aristas[a].add(b)
    sccs = [c for c in tarjan_scc(nodos, aristas) if len(c) > 1]
    # estancamiento: turno de inicio/fin de cada visita en el camino SIN
    # colapsar -- cuántos turnos reales duró la visita más larga.
    return {
        "camino": camino,               # [(turn_id, ubicacion)]
        "ambiguos": ambiguos,            # [(turn_id, [ubicaciones])]
        "ciclos": sccs,                  # [[ubicacion, ...], ...]
        "num_visitas": len(camino),
        "num_ubicaciones_distintas": len(nodos),
    }


def imprimir_bucles(r):
    paso("2. DETECTOR DE BUCLES (grafo de transiciones REALIZADAS, "
         "candidato inspirado en Twine/Symmetry)")
    print(f"  {r['num_visitas']} visitas distintas · "
          f"{r['num_ubicaciones_distintas']} ubicaciones conocidas "
          f"mencionadas en total")
    if r["ciclos"]:
        for ciclo in r["ciclos"]:
            print(f"  ⚠ ciclo detectado: {' ↔ '.join(sorted(ciclo))} "
                  f"(la campaña entra y sale de este conjunto sin "
                  f"llegar a lugares nuevos)")
    else:
        print("  sin ciclos -- el camino de ubicaciones avanza sin "
              "quedar atrapado en un conjunto cerrado")
    if r["ambiguos"]:
        print(f"  {len(r['ambiguos'])} turno(s) con más de una ubicación "
              f"mencionada a la vez (no cuentan como transición clara):")
        for turn_id, ubis in r["ambiguos"][:5]:
            print(f"    turno {turn_id}: {', '.join(ubis)}")
    if r["camino"]:
        print("  camino (primeras y últimas visitas):")
        muestra = r["camino"][:3] + (["..."] if len(r["camino"]) > 6 else []) + r["camino"][-3:]
        for v in muestra:
            print(f"    {v}" if v == "..." else f"    turno {v[0]:>3} → {v[1]}")


# ------------------------------------------------------- 3. relojes no reconocidos

def _texto_reloj(reloj):
    """Vocabulario de búsqueda para un reloj disparado: nombre de la
    facción + palabras de 4+ letras de la agenda + cualquier valor de
    texto dentro de on_fire_event (headline/consequence/scope en el
    fixture actual -- ver nota: contexto_escena() en db.py busca la
    clave "descripcion" que NO existe en el fixture, así que en la
    práctica el DM solo ve `agenda` como fallback; se buscan también
    headline/consequence/scope acá por si en el futuro sí se pasan)."""
    palabras = {reloj["faccion"]}
    palabras.update(p for p in re.findall(r"\w+", reloj["agenda"])
                     if len(p) >= 4)
    ofe = reloj.get("on_fire_event") or {}
    for v in ofe.values():
        if isinstance(v, str):
            palabras.update(p for p in re.findall(r"\w+", v) if len(p) >= 4)
    return palabras


def relojes_no_reconocidos(relojes, turnos_por_id, ventana=2):
    """Para cada reloj disparado en `fired_at_turn`, busca sus palabras
    clave en la narración de los `ventana` turnos siguientes (el propio
    turno de disparo casi nunca alcanza a narrar la consecuencia porque
    avanzar_relojes() corre DESPUÉS de escribir -- ver
    eventos_reloj_turno() en db.py -- así que se revisa desde
    fired_at_turn+1). No reconocido = tier "revisar", nunca "problema"
    duro: el chequeo es un proxy de solapamiento léxico, no prueba
    semántica de que el DM ignoró el evento."""
    resultado = []
    for r in relojes:
        vocab = _texto_reloj(r)
        disparo = r["fired_at_turn"]
        reconocido = False
        turno_evidencia = None
        for tid in range(disparo + 1, disparo + 1 + ventana):
            texto = turnos_por_id.get(tid)
            if not texto:
                continue
            if any(re.search(rf"\b{re.escape(p)}\b", texto, re.I)
                   for p in vocab):
                reconocido = True
                turno_evidencia = tid
                break
        resultado.append({
            "faccion": r["faccion"], "agenda": r["agenda"],
            "disparado_turno": disparo, "reconocido": reconocido,
            "turno_evidencia": turno_evidencia,
        })
    return resultado


def imprimir_relojes(resultado):
    paso("3. RELOJES DISPARADOS — ¿la narración reconoció la consecuencia? "
         "(validación longitudinal-causal)")
    if not resultado:
        print("  ningún reloj ha disparado todavía en esta campaña")
        return
    for r in resultado:
        estado = (f"✓ reconocido en turno {r['turno_evidencia']}"
                  if r["reconocido"] else "⚠ NO reconocido en los turnos "
                                          "siguientes")
        print(f"  {r['faccion']:20s} disparó en turno {r['disparado_turno']:>3} "
              f"· {estado}")
        print(f"    agenda: {r['agenda']}")


# ------------------------------------------------------- 4. Papalampidi et al.

# Papalampidi, Cao & Kocisky (2022), "Towards Coherent and Consistent Use of
# Entities in Narrative Generation" (EMNLP Findings). Dos métricas a nivel de
# NARRATIVA COMPLETA (toda la campaña concatenada en orden de turno), no por
# turno individual -- por eso viven acá y no en turn_validation. Fórmulas
# citadas literalmente del paper (Sección 2 y Ecuación de V):
#
#   C (coherencia de rango largo): se toman los "protagonistas" (entidades
#   con más menciones), se divide la narrativa en L secciones iguales
#   (el paper usa L=10 sobre historias completas de WikiPlots/WritingPrompts
#   -- acá se adapta a L=10 turnos contiguos, o menos si la campaña tiene
#   menos de 10 turnos, documentado explícitamente como adaptación), y para
#   cada protagonista i se calcula el span máximo Ci = (sli - sfi) / 2, donde
#   sfi/sli son los índices de sección de la primera/última mención. C es el
#   promedio de Ci sobre los protagonistas.
#
#   V (consistencia de atributos): para cada protagonista i, se toman todos
#   los verbos/adjetivos que aparecen en las mismas ORACIONES que mencionan
#   a i (Aj = atributos de la oración j), y Vi = |A_in \ A_out| / |A_in|,
#   donde A_in es la unión de Aj sobre oraciones que SÍ mencionan a i, y
#   A_out la unión sobre oraciones que NO lo mencionan -- el % de atributos
#   de i que no se comparten con ningún otro contexto de la narrativa.
#
# Simplificaciones frente al paper (documentadas, mismo criterio que el
# resto de proxies Tier 3 de este sistema):
#   - El paper identifica entidades vía correferencia end-to-end (Lee et
#     al. 2018); acá se cuenta mención LITERAL del nombre completo del
#     personaje (mismo límite ya documentado para CR-2/grafo de entidad:
#     no hay resolución de pronombres).
#   - Verbos/adjetivos requieren POS tagging -- única pieza de este sistema
#     que usa un modelo entrenado (spaCy es_core_news_sm) en vez de regex
#     puro. Se decidió así explícitamente (ver nota de respaldo
#     bibliográfico) para ser fiel a la métrica real del paper en vez de
#     aproximarla con una heurística de sufijos -- V es la pieza más
#     sensible a juicio humano según el propio paper (r=0.08 con humanos,
#     la correlación más baja de las cuatro métricas automáticas que
#     proponen), así que no vale la pena degradarla más con un POS tagger
#     casero.
#
# Ambas son descriptivas -- nunca pass/fail, nunca Tier 1/2. Solo tienen
# sentido con varias campañas para comparar (ver "Pendiente" en la nota).

PROTAGONISTA_TIPOS = ("character", "npc")


def _modelo_pos():
    """Carga perezosa de spaCy es_core_news_sm, cacheada a nivel de módulo.
    Devuelve None (con aviso impreso UNA vez) si no está instalado -- V se
    omite del reporte en ese caso, pero el resto del script sigue
    funcionando (no es una dependencia dura del reporte completo)."""
    global _MODELO_POS_CACHE
    try:
        return _MODELO_POS_CACHE
    except NameError:
        pass
    try:
        import spacy
        _MODELO_POS_CACHE = spacy.load(
            "es_core_news_sm", disable=["parser", "ner", "lemmatizer"])
    except (ImportError, OSError):
        print("  ⚠ spaCy / es_core_news_sm no instalado -- V (consistencia "
              "de atributos) se omite. Instalar con:\n"
              "      pip install spacy\n"
              "      python -m spacy download es_core_news_sm")
        _MODELO_POS_CACHE = None
    return _MODELO_POS_CACHE


def _dividir_en_secciones(turnos, L=10):
    """turnos en orden -> lista de hasta L listas de dm_output (secciones
    contiguas, lo más parejas posible por CANTIDAD DE TURNOS -- adaptación
    de "L secciones iguales" del paper, que las mide en tokens sobre una
    historia ya completa; acá el turno es la unidad atómica natural del
    sistema, partirlo a la mitad no tendría sentido narrativo)."""
    n = len(turnos)
    if n == 0:
        return []
    L_efectivo = min(L, n)
    secciones = []
    for k in range(L_efectivo):
        ini = (k * n) // L_efectivo
        fin = ((k + 1) * n) // L_efectivo
        secciones.append(" ".join(t["dm_output"] for t in turnos[ini:fin]))
    return secciones


def _top_protagonistas(turnos, entidades, top_n=3):
    """Cuenta menciones LITERALES del nombre completo de cada entidad tipo
    character/npc en toda la narrativa concatenada, devuelve las top_n con
    al menos 1 mención (nombre, conteo). Mismo límite que el resto del
    sistema: sin resolución de correferencia/pronombres."""
    texto_completo = " ".join(t["dm_output"] for t in turnos)
    candidatas = [e for e in entidades if e["tipo"] in PROTAGONISTA_TIPOS]
    conteos = []
    for e in candidatas:
        n = len(re.findall(rf"\b{re.escape(e['nombre'])}\b", texto_completo))
        if n > 0:
            conteos.append((e["nombre"], n))
    conteos.sort(key=lambda x: x[1], reverse=True)
    return conteos[:top_n]


def coherencia_entidad_C(turnos, entidades, top_n=3, L=10):
    """C de Papalampidi et al. -- ver docstring de sección arriba.
    Devuelve (C_promedio, L_efectivo, detalle) o (None, 0, []) si no hay
    turnos o ningún protagonista con menciones."""
    protagonistas = _top_protagonistas(turnos, entidades, top_n)
    secciones = _dividir_en_secciones(turnos, L)
    if not protagonistas or not secciones:
        return None, 0, []
    detalle = []
    for nombre, _conteo in protagonistas:
        patron = rf"\b{re.escape(nombre)}\b"
        idx_apariciones = [i for i, sec in enumerate(secciones)
                           if re.search(patron, sec)]
        if not idx_apariciones:
            continue
        sf, sl = idx_apariciones[0], idx_apariciones[-1]
        Ci = (sl - sf) / 2
        detalle.append((nombre, Ci, sf, sl))
    if not detalle:
        return None, len(secciones), []
    C = sum(d[1] for d in detalle) / len(detalle)
    return round(C, 3), len(secciones), detalle


_ATRIBUTO_POS = {"VERB", "AUX", "ADJ"}


def _atributos_por_oracion(oraciones, modelo):
    """Una pasada de spaCy sobre todas las oraciones (batch, más barato que
    una llamada por oración). Devuelve lista paralela a `oraciones` de
    sets de lemas en VERB/AUX/ADJ -- se usa el lema, no la forma literal,
    para que "atacó"/"ataca"/"atacando" cuenten como el mismo atributo en
    vez de inflar V con conjugaciones distintas del mismo verbo (desviación
    documentada frente al paper, que no lematiza)."""
    modelo_lema = modelo
    resultado = []
    for doc in modelo.pipe(oraciones):
        resultado.append({t.lemma_.lower() if t.lemma_ else t.text.lower()
                          for t in doc if t.pos_ in _ATRIBUTO_POS})
    return resultado


def consistencia_atributos_V(turnos, entidades, top_n=3, L=10):
    """V de Papalampidi et al. -- ver docstring de sección arriba. Reusa
    los mismos top_n protagonistas que C (mismo conjunto, para que ambas
    métricas del reporte hablen de las mismas entidades). Devuelve
    (V_promedio, detalle) o (None, []) si spaCy no está disponible, no hay
    oraciones, o ningún protagonista tiene atributos propios."""
    modelo = _modelo_pos()
    if modelo is None:
        return None, []
    protagonistas = _top_protagonistas(turnos, entidades, top_n)
    if not protagonistas:
        return None, []
    texto_completo = " ".join(t["dm_output"] for t in turnos)
    oraciones = [o.strip() for o in re.split(r"[.!?]+", texto_completo)
                if o.strip()]
    if not oraciones:
        return None, []
    # Lematizamos deshabilitado arriba para velocidad -- lo re-habilitamos
    # solo para este cálculo, cargándolo una vez (spaCy permite activar
    # componentes deshabilitados bajo demanda).
    if "lemmatizer" in modelo.disabled:
        modelo.enable_pipe("lemmatizer")
    atributos_por_oracion = _atributos_por_oracion(oraciones, modelo)
    detalle = []
    for nombre, _conteo in protagonistas:
        patron = rf"\b{re.escape(nombre)}\b"
        a_in, a_out = set(), set()
        tiene_mencion = False
        for oracion, atributos in zip(oraciones, atributos_por_oracion):
            if re.search(patron, oracion):
                a_in |= atributos
                tiene_mencion = True
            else:
                a_out |= atributos
        if not tiene_mencion or not a_in:
            continue
        Vi = len(a_in - a_out) / len(a_in)
        detalle.append((nombre, round(Vi, 3), len(a_in)))
    if not detalle:
        return None, []
    V = sum(d[1] for d in detalle) / len(detalle)
    return round(V, 3), detalle


def imprimir_papalampidi(C, L_efectivo, detalle_c, V, detalle_v):
    paso("4. COHERENCIA (C) Y CONSISTENCIA DE ATRIBUTOS (V) — "
         "Papalampidi et al. 2022 (agregado de campaña completa)")
    if C is None:
        print("  no hay suficientes turnos/protagonistas con menciones "
              "para calcular C")
    else:
        print(f"  C promedio = {C}  (sobre {L_efectivo} secciones; "
              f"máximo teórico = {(L_efectivo - 1) / 2})")
        for nombre, Ci, sf, sl in detalle_c:
            print(f"    {nombre}: Ci={Ci}  (primera mención sección {sf}, "
                 f"última sección {sl})")
    if V is None:
        print("  V no calculado (spaCy no disponible, o sin protagonistas "
              "con atributos propios)")
    else:
        print(f"  V promedio = {V}  (1.0 = todos los atributos de la "
              f"entidad son exclusivos suyos en la narrativa)")
        for nombre, Vi, n_attrs in detalle_v:
            print(f"    {nombre}: Vi={Vi}  ({n_attrs} atributos propios "
                 f"detectados)")


# --------------------------------------------------- 5. Jericho-QA State Graph

# Ammanabrolu et al. (2020), "Structured Exploration Strategies for Textual
# Worlds" (Jericho-QA): mide si las tripletas de estado extraídas de la
# narración coinciden (Exact Match / F1) con el grafo de conocimiento real
# del mundo. Ver "Evaluación Determinista de Narrativa Interactiva.md"
# (documento de brechas, 2026-09) -- instrumento de "alta aplicabilidad"
# identificado como brecha frente a lo que ya cubre este script.
#
# Adaptación deliberada, documentada en vez de disimulada:
#   - El paper compara tripletas EXTRAÍDAS por un modelo entrenado contra
#     el grafo real. Acá no hay extractor de tripletas de texto libre en
#     español (fuera de alcance de este proyecto) -- en su lugar, la
#     "tripleta extraída" se aproxima con un detector léxico: ¿aparece en
#     la narración alguna palabra del campo semántico esperado para el
#     NUEVO valor que state_deltas ya registró como verdad?
#   - Por eso este instrumento reporta únicamente RECALL (de los cambios
#     de estado reales, ¿cuántos se ven reflejados en la narración?),
#     nunca F1 ni precisión: calcular precisión exigiría detectar
#     afirmaciones de estado en la narración que NO están respaldadas por
#     la base -- eso sí requeriría el extractor de tripletas real. Llamar
#     "F1" a esto sería inflar la métrica con una mitad que no se está
#     midiendo. Mismo criterio de honestidad que el resto de proxies Tier 3
#     de este sistema (ver "Ley de Goodhart" en la nota de respaldo).
#   - Cobertura deliberadamente acotada a tres campos con vocabulario de
#     salida CERRADO (enum o numérico-a-banda): npc.status, npc.affinity
#     (vía disposition_band), quest.status. Campos de texto libre
#     (location.detail, character.inventory, etc.) quedan fuera: no hay
#     forma determinística honesta de chequearlos sin NLP entrenado.
#   - npc.status='alive', quest.status en {'active','unknown'} y
#     npc.affinity en banda 'neutral' se EXCLUYEN del cálculo: son los
#     valores por defecto/sin marca, sin vocabulario distintivo en
#     español que permita decidir si "no se detectó" significa "no se
#     narró" o "no había nada que narrar". Incluir estos como "fallos"
#     inflaría el recall a la baja de forma artificial.

_KEYWORDS_NPC_STATUS = {
    "dead": ("muert", "murió", "murio", "cadáver", "cadaver", "cayó sin vida",
             "cayo sin vida", "falleci"),
    "missing": ("desapareci", "desaparecid", "sin rastro", "no se le encuentra",
                "no se lo encuentra", "no se le encontró", "paradero desconocido"),
    "captured": ("captur", "apres", "cautiv", "encadenad", "prisioner"),
    # 'alive' es el default -- sin vocabulario distintivo, se excluye.
}

_KEYWORDS_QUEST_STATUS = {
    "completed": ("complet", "logr", "cumpli", "conclu", "resuelt", "resolvi"),
    "failed": ("fall", "fracas", "perdid", "irrecuperable"),
    "abandoned": ("abandon", "renunci", "desisti"),
    # 'active'/'unknown' son default -- se excluyen.
}

# disposition_band() (migrations/001_schema.sql) es el umbral real; se
# reimplementa aquí en Python para no pagar un roundtrip a Postgres por
# cada delta de afinidad -- los umbrales están duplicados A PROPÓSITO,
# documentado, mismo criterio que el resto de "duplicado, no reutilizado"
# de este proyecto (ver vertical_slice_g1.py).
def _banda_afinidad(valor):
    v = float(valor)
    if v <= -60: return "hostile"
    if v <= -25: return "wary"
    if v <= -8: return "cold"
    if v < 8: return "neutral"
    if v < 25: return "cordial"
    if v < 60: return "loyal"
    return "devoted"


_KEYWORDS_AFINIDAD_BANDA = {
    "hostile": ("hostil", "odia", "odio", "enemig", "detesta"),
    "wary": ("desconf", "recel", "cautel", "suspica"),
    "cold": ("fría", "frio", "fría", "distante", "gélid", "gelid", "seca"),
    "cordial": ("cordial", "amable", "cortés", "cortes", "amistos"),
    "loyal": ("leal", "fiel", "confía plenamente", "confia plenamente"),
    "devoted": ("devot", "entregad", "adora", "venera", "incondicional"),
    # 'neutral' es el punto medio sin marca -- se excluye.
}


def _ventana_texto(turnos_por_id, turn_id, ventana):
    """Concatena dm_output de [turn_id, turn_id+ventana] -- la consecuencia
    de un delta puede narrarse en el mismo turno que se escribió (la
    mayoría de los casos, a diferencia de los relojes) o, si el
    orquestador la difiere, en el inmediato siguiente."""
    partes = [turnos_por_id[t] for t in range(turn_id, turn_id + ventana + 1)
              if t in turnos_por_id]
    return " ".join(partes).lower()


def jericho_qa_recall(deltas, turnos_por_id, ventana=1):
    """Recall del grafo de estado (ver docstring de sección arriba).
    `deltas`: filas de Campaña.deltas_narrables(). Devuelve dict con
    conteo/recall por campo (npc.status, npc.affinity, quest.status) y
    total, más el detalle de los NO reconocidos (para poder citarlos)."""
    familias = {
        "npc.status": [], "npc.affinity": [], "quest.status": [],
    }
    no_reconocidos = []
    for d in deltas:
        campo = f"{d['entity_type']}.{d['field_name']}"
        valor_crudo = d["new_value"]
        # new_value es jsonb -- puede venir como número, string con
        # comillas de json.dumps, o directamente el tipo ya decodificado
        # por psycopg (jsonb se decodifica solo). Se normaliza a str/float
        # según el campo.
        if campo == "npc.status":
            estado = str(valor_crudo).strip('"').lower()
            claves = _KEYWORDS_NPC_STATUS.get(estado)
        elif campo == "quest.status":
            estado = str(valor_crudo).strip('"').lower()
            claves = _KEYWORDS_QUEST_STATUS.get(estado)
        elif campo == "npc.affinity":
            try:
                banda = _banda_afinidad(valor_crudo)
            except (TypeError, ValueError):
                continue
            # Solo cruces de banda cuentan como evento narrable -- varios
            # deltas pequeños seguidos que caen en la MISMA banda que ya
            # tenían no son "cambios de estado" desde el punto de vista de
            # lo que un narrador razonablemente marcaría (ver docstring de
            # deltas_narrables() en db.py). old_value=NULL (primer delta de
            # afinidad de esa entidad, sin banda previa registrada) SÍ
            # cuenta -- es la primera vez que hay algo que narrar.
            if d.get("old_value") is not None:
                try:
                    banda_previa = _banda_afinidad(d["old_value"])
                except (TypeError, ValueError):
                    banda_previa = None
                if banda_previa == banda:
                    continue
            claves = _KEYWORDS_AFINIDAD_BANDA.get(banda)
            estado = banda
        else:
            continue
        if not claves:
            continue  # valor sin vocabulario distintivo (default) -- excluido
        texto = _ventana_texto(turnos_por_id, d["turn_id"], ventana)
        reconocido = any(k in texto for k in claves)
        familias[campo].append(reconocido)
        if not reconocido:
            no_reconocidos.append({
                "turno": d["turn_id"], "entidad": d["entity_name"],
                "campo": campo, "valor": estado,
            })
    resultado = {"familias": {}, "no_reconocidos": no_reconocidos}
    total_si, total_n = 0, 0
    for campo, marcas in familias.items():
        n = len(marcas)
        si = sum(marcas)
        total_si += si
        total_n += n
        resultado["familias"][campo] = {"n": n, "reconocidos": si,
                                        "recall": round(si / n, 3) if n else None}
    resultado["recall_global"] = round(total_si / total_n, 3) if total_n else None
    resultado["n_total"] = total_n
    return resultado


def imprimir_jericho_qa(r):
    paso("5. JERICHO-QA STATE GRAPH — Recall (deltas de estado vs. "
         "narración; ver nota: SOLO recall, no F1 -- limitación declarada)")
    if r["n_total"] == 0:
        print("  sin deltas de npc.status/affinity o quest.status con "
              "vocabulario distintivo detectable en esta campaña")
        return
    for campo, st in r["familias"].items():
        if st["n"] == 0:
            continue
        print(f"    {campo:16s} recall={st['recall']:.3f}  "
              f"({st['reconocidos']}/{st['n']})")
    print(f"  recall global: {r['recall_global']:.3f}  "
          f"({r['n_total']} deltas evaluables)")
    if r["no_reconocidos"]:
        print(f"  {len(r['no_reconocidos'])} delta(s) sin reflejo textual "
              f"detectado en la ventana de turnos:")
        for x in r["no_reconocidos"][:8]:
            print(f"    turno {x['turno']:>4} · {x['entidad']} · "
                  f"{x['campo']}={x['valor']}")


# ---------------------- 6. CL-1: Entity Coreference Rate (Roemmele & Gordon)

def entity_coreference_rate(turnos, entidades):
    """Roemmele & Gordon, "Evaluating Story Generation Systems Using
    Automated Linguistic Analyses" -- Entity Coreference Rate: de las
    entidades reales de la campaña mencionadas en un turno, qué proporción
    YA era conocida (mencionada en un turno anterior) frente a nueva.

    Post-hoc, sin dependencias nuevas (mismo principio de gazetteer que
    CR-2: nombre completo o palabra suelta de 3+ letras) -- deliberadamente
    NO se toca vertical_slice.py/vertical_slice_g1.py ni el schema de
    turn_validation con esto (ver bitácora QM, punto 33: riesgo de tocar
    el motor de generación a días de la corrida a escala completa).

    Es un ángulo distinto de CR-2: mide persistencia de identidad a lo
    largo de la campaña (CL-1), no arraigo contextual inmediato (CR-2).
    NO detecta colisión de identidad (un nombre reasignado a una entidad
    incompatible) -- solo si las entidades reaparecen o no. Se declara
    esa limitación explícitamente, igual que con el resto de proxies de
    esta nota."""
    nombres = {e["nombre"] for e in entidades}
    primera_mencion = {}
    por_turno = []
    for t in turnos:
        texto = t["dm_output"]
        mencionadas = set()
        for nombre in nombres:
            tokens = [nombre] + [p for p in nombre.split() if len(p) >= 3]
            if any(tok and tok in texto for tok in tokens):
                mencionadas.add(nombre)
        if mencionadas:
            ya_conocidas = sum(1 for n in mencionadas if n in primera_mencion)
            por_turno.append({
                "turn_id": t["turn_id"],
                "mencionadas": len(mencionadas),
                "ya_conocidas": ya_conocidas,
                "tasa": ya_conocidas / len(mencionadas),
            })
        for n in mencionadas:
            primera_mencion.setdefault(n, t["turn_id"])

    tasas = [x["tasa"] for x in por_turno]
    promedio = sum(tasas) / len(tasas) if tasas else None
    return {"promedio": promedio, "por_turno": por_turno,
            "n_turnos_con_entidad": len(por_turno)}


def imprimir_entity_coreference(r):
    paso("6. ENTITY COREFERENCE RATE (Roemmele & Gordon) — proxy de CL-1, "
         "persistencia de identidad a lo largo de la campaña")
    if r["promedio"] is None:
        print("  sin turnos con entidades reconocibles detectadas")
        return
    print(f"  tasa promedio: {r['promedio']:.3f}  "
          f"({r['n_turnos_con_entidad']} turnos con al menos 1 entidad "
          f"reconocida)")
    print("  (1.0 = todas las entidades mencionadas ya eran conocidas de "
          "turnos previos; 0.0 = todas nuevas en ese turno. NO detecta "
          "colisión de identidad -- solo mide reaparición, ver nota en "
          "el código)")


# --------- 7. CR-1: Grammaticality (Roemmele & Gordon, vía LanguageTool)

def _herramienta_lt():
    """Carga perezosa de LanguageTool (es), cacheada a nivel de módulo.
    Requiere Java 8+ instalado -- si no está disponible, o la librería no
    está instalada, se avisa UNA vez y esta sección se omite del reporte
    (no es una dependencia dura del resto del script). Primera ejecución
    descarga ~260MB del motor de LanguageTool -- solo una vez, queda
    cacheado localmente."""
    global _LT_CACHE
    try:
        return _LT_CACHE
    except NameError:
        pass
    try:
        import language_tool_python
        _LT_CACHE = language_tool_python.LanguageTool("es")
    except Exception as e:
        print(f"  ⚠ LanguageTool no disponible ({e!r}) -- Grammaticality "
              f"(CR-1) se omite. Requiere Java 8+ y:\n"
              f"      pip install language-tool-python")
        _LT_CACHE = None
    return _LT_CACHE


def grammaticality_lt(texto, tool):
    """Roemmele & Gordon -- Grammaticality: proporción de palabras SIN
    error gramatical detectado. Excluye deliberadamente la categoría
    TYPOS (ortografía): los nombres propios inventados de la campaña
    (PNJ, lugares, facciones) disparan falsos positivos de ortografía de
    forma sistemática -- no están en el diccionario de LanguageTool y no
    es un error real. Contar eso mediría "cuántos nombres de fantasía
    hay", no gramática. Ver bitácora QM, punto 34."""
    if not texto.strip():
        return None
    matches = [m for m in tool.check(texto) if m.category != "TYPOS"]
    n_palabras = len(texto.split())
    if n_palabras == 0:
        return None
    if not matches:
        return 1.0
    posiciones = set()
    for m in matches:
        posiciones.update(range(m.offset, m.offset + m.error_length))
    palabras_con_error, cursor = 0, 0
    for palabra in texto.split(" "):
        fin = cursor + len(palabra)
        if any(p in posiciones for p in range(cursor, fin)):
            palabras_con_error += 1
        cursor = fin + 1
    return round(1 - palabras_con_error / n_palabras, 3)


def reporte_grammaticality(turnos):
    tool = _herramienta_lt()
    if tool is None:
        return None
    puntajes = []
    for t in turnos:
        g = grammaticality_lt(t["dm_output"], tool)
        if g is not None:
            puntajes.append(g)
    if not puntajes:
        return None
    return {"promedio": round(sum(puntajes) / len(puntajes), 3),
            "min": min(puntajes), "max": max(puntajes), "n": len(puntajes)}


def imprimir_grammaticality(r):
    paso("7. GRAMMATICALITY (Roemmele & Gordon, vía LanguageTool-es) — "
         "proxy de CR-1, fluidez/corrección gramatical")
    if r is None:
        print("  omitido (LanguageTool no disponible o sin turnos con texto)")
        return
    print(f"  promedio: {r['promedio']:.3f}  (min {r['min']:.3f}, "
          f"max {r['max']:.3f}, n={r['n']} turnos)")
    print("  (excluye ortografía -- nombres propios inventados no cuentan "
          "como error; solo gramática/sintaxis real)")


# ------------- 8. CR-2 (complemento): grafo de coherencia por lema (spaCy)

def _modelo_grafo():
    """Carga perezosa de spaCy con parser+lemmatizer activos (distinto del
    cache de _modelo_pos(), que los desactiva para Papalampidi). Mismo
    patrón de degradación amable: None + aviso único si no está instalado."""
    global _MODELO_GRAFO_CACHE
    try:
        return _MODELO_GRAFO_CACHE
    except NameError:
        pass
    try:
        import spacy
        _MODELO_GRAFO_CACHE = spacy.load("es_core_news_sm", disable=["ner"])
    except (ImportError, OSError):
        print("  ⚠ spaCy / es_core_news_sm no instalado -- grafo de "
              "coherencia por lema (CR-2 complementario) se omite.")
        _MODELO_GRAFO_CACHE = None
    return _MODELO_GRAFO_CACHE


def grafo_lema_densidad(texto, lemas_conocidos, nlp):
    """Guinaudeau & Strube (2013) -- versión con lematización real (spaCy)
    en vez del match por substring de `cr2_entidad_grafo_densidad`
    (implementación original, ver bitácora QM Tier 3). Sustantivos/nombres
    propios lematizados por oración; dos oraciones consecutivas quedan
    conectadas si comparten un lema que corresponde a una entidad REAL de
    la campaña (mismo principio de gazetteer que el resto de esta nota,
    ahora con forma canónica en vez de coincidencia literal de texto).

    Deliberadamente NO reemplaza `cr2_entidad_grafo_densidad` (columna ya
    escrita en vivo por vertical_slice.py/g1.py) -- se calcula acá,
    post-hoc, para no tocar el motor de generación a días de la corrida a
    escala completa (ver bitácora QM, punto 33). Se reportan ambas para
    comparar si la lematización cambia la lectura."""
    doc = nlp(texto)
    oraciones = list(doc.sents)
    n = len(oraciones)
    if n < 2:
        return None
    por_oracion = [
        {t.lemma_.lower() for t in o
         if t.pos_ in ("NOUN", "PROPN") and len(t.lemma_) >= 3} & lemas_conocidos
        for o in oraciones
    ]
    aristas = sum(1 for i in range(n - 1) if por_oracion[i] & por_oracion[i + 1])
    return round(aristas / (n - 1), 3)


def reporte_grafo_lema(turnos, entidades):
    nlp = _modelo_grafo()
    if nlp is None:
        return None
    lemas_conocidos = set()
    for e in entidades:
        for tok in nlp(e["nombre"]):
            if len(tok.lemma_) >= 3:
                lemas_conocidos.add(tok.lemma_.lower())
    densidades = []
    for t in turnos:
        d = grafo_lema_densidad(t["dm_output"], lemas_conocidos, nlp)
        if d is not None:
            densidades.append(d)
    if not densidades:
        return None
    return {"promedio": round(sum(densidades) / len(densidades), 3),
            "n": len(densidades)}


def imprimir_grafo_lema(r):
    paso("8. GRAFO DE COHERENCIA POR LEMA (Guinaudeau & Strube, vía spaCy) "
         "— complemento lematizado de cr2_entidad_grafo_densidad")
    if r is None:
        print("  omitido (spaCy no disponible o sin turnos con ≥2 oraciones)")
        return
    print(f"  densidad promedio: {r['promedio']:.3f}  (n={r['n']} turnos "
          f"con ≥2 oraciones)")
    print("  (compara contra cr2_entidad_grafo_densidad de la sección 1 -- "
          "si difieren mucho, la lematización está capturando continuidad "
          "que el match literal por substring se perdía, o viceversa)")


# ------------------- 9. Refinamiento sintáctico de cl2_pnj_inactivo_actua

# Hallazgo 2026-09-18 (ver plan doc, "Cierre de Par 04/05/06"): el chequeo
# EN VIVO cl2_pnj_inactivo_actua (vertical_slice.py/vertical_slice_g1.py)
# dispara con la sola presencia LITERAL del nombre de un PNJ con
# status != 'alive' en la narración del turno -- sin distinguir si el PNJ
# aparece como sujeto de una acción (error real de continuidad) o como
# referencia retrospectiva/callback ("todavía se preguntan qué le pasó a
# Yenna" -- narrativamente correcto, no un error). Como G1 sostiene
# referencias a su elenco a lo largo de muchas más secciones que G2 (ver
# Papalampidi C, sección 4), tiene mecánicamente más ocasiones de que una
# mención tardía dispare el chequeo crudo, sin que eso implique
# necesariamente un fallo de continuidad -- ambos hallazgos podrían ser
# dos caras del mismo rasgo narrativo (G1 referencia más, por más tiempo)
# en vez de dos hallazgos independientes.
#
# Este refinamiento NO reemplaza la columna en vivo (que sí usa el estado
# HISTÓRICO correcto al momento exacto de generación, algo que este script
# post-hoc no puede reconstruir con la misma fidelidad) -- reclasifica los
# turnos que ESE chequeo ya marcó, aplicando un criterio sintáctico más
# fino sobre el mismo texto ya generado. Por eso se puede correr
# retroactivamente sobre cualquier campaña ya cerrada, sin regenerar nada
# ni tocar vertical_slice.py/g1.py ni el schema de turn_validation (mismo
# criterio de no perturbar el motor de generación que el resto de esta
# nota, ver bitácora QM punto 33).
#
# Criterio: spaCy (mismo modelo con parser activo que la sección 8)
# determina si el nombre del PNJ es sujeto gramatical (dep_ en
# nsubj/nsubj:pass) de un token en la misma oración donde aparece. Si lo
# es, se cuenta como "narrado actuando" (repite/confirma el hallazgo
# crudo); si no, como "solo mencionado/referenciado" (retrospectiva,
# diálogo ajeno sobre él, recuerdo, etc.) -- y NO debería tratarse como
# error de continuidad hasta nueva verificación manual.

def pnj_inactivo_refinado(filas_validacion, turnos_por_id, entidades):
    """Reclasifica los turnos con cl2_pnj_inactivo_actua=true (ver
    docstring de sección arriba). Devuelve None si spaCy no está
    disponible; si no, dict con listas 'actuando', 'solo_referenciado' y
    'sin_evidencia_reconstruible' (turno flageado pero el PNJ ya no
    aparece literal en el texto guardado -- no debería pasar, pero se
    documenta en vez de fallar silenciosamente)."""
    nlp = _modelo_grafo()
    if nlp is None:
        return None
    nombres_pnj = {e["nombre"] for e in entidades if e["tipo"] == "npc"}
    flagged = [f for f in filas_validacion if f.get("cl2_pnj_inactivo_actua")]
    resultado = {"actuando": [], "solo_referenciado": [],
                 "sin_evidencia_reconstruible": [], "n_flagged": len(flagged)}
    for f in flagged:
        turn_id = f["turn_id"]
        texto = turnos_por_id.get(turn_id)
        if not texto:
            resultado["sin_evidencia_reconstruible"].append(turn_id)
            continue
        doc = nlp(texto)
        clasificado = False
        for sent in doc.sents:
            for nombre in nombres_pnj:
                if nombre not in sent.text:
                    continue
                es_sujeto = any(
                    tok.dep_ in ("nsubj", "nsubj:pass") and nombre in tok.text
                    for tok in sent)
                entrada = {"turno": turn_id, "pnj": nombre,
                          "oracion": sent.text.strip()[:160]}
                if es_sujeto:
                    resultado["actuando"].append(entrada)
                else:
                    resultado["solo_referenciado"].append(entrada)
                clasificado = True
        if not clasificado:
            resultado["sin_evidencia_reconstruible"].append(turn_id)
    return resultado


def imprimir_pnj_inactivo_refinado(r):
    paso("9. REFINAMIENTO SINTÁCTICO DE cl2_pnj_inactivo_actua (post-hoc, "
         "spaCy) -- ¿el PNJ inactivo actúa o solo se le menciona?")
    if r is None:
        print("  omitido (spaCy no disponible)")
        return
    if r["n_flagged"] == 0:
        print("  ningún turno con cl2_pnj_inactivo_actua=true en esta "
              "campaña -- nada que reclasificar")
        return
    n_act = len(r["actuando"])
    n_ref = len(r["solo_referenciado"])
    n_sin = len(r["sin_evidencia_reconstruible"])
    print(f"  {r['n_flagged']} turno(s) marcados en vivo. Reclasificación:")
    print(f"    sujeto de una acción (repite el hallazgo crudo): "
          f"{n_act} ({100*n_act/r['n_flagged']:.1f}%)")
    print(f"    solo mencionado/referenciado (posible falso positivo): "
          f"{n_ref} ({100*n_ref/r['n_flagged']:.1f}%)")
    if n_sin:
        print(f"    sin evidencia reconstruible en el texto guardado: {n_sin}")
    if r["actuando"]:
        print("  muestra de 'actuando' (spot-check manual recomendado "
              "antes de citar en la tesis):")
        for x in r["actuando"][:5]:
            print(f"    turno {x['turno']:>4} · {x['pnj']}: «{x['oracion']}»")


# --------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-id", default=None,
                    help="UUID de campaña; por defecto la más antigua "
                         "(mismo criterio que vertical_slice.py)")
    ap.add_argument("--hasta-turno", type=int, default=None,
                    help="Analiza solo turn_id <= N, para comparar "
                         "'sesión 1' de dos campañas con distinto número "
                         "de turnos generados sobre el mismo espacio de "
                         "turnos, sin tener que regenerar la más larga.")
    args = ap.parse_args()

    import psycopg
    if args.campaign_id:
        campaign_id = args.campaign_id
    else:
        with psycopg.connect(bd.DSN) as c:
            r = c.execute(
                "SELECT id, title FROM campaigns ORDER BY created_at "
                "LIMIT 1").fetchone()
        if not r:
            sys.exit("No hay campañas en la base. Carga fixtures/seed.sql")
        campaign_id = r[0]

    camp = bd.Campaña(campaign_id)
    cab = camp.cabecera()
    titulo_rango = (f" · hasta turno {args.hasta_turno}"
                    if args.hasta_turno is not None else "")
    print(f"\n{'='*74}\nREPORTE DE VALIDACIÓN · {cab['title']} · "
          f"{cab['architecture']}{titulo_rango}\n{'='*74}")

    with camp._conn() as c:
        camp._tx(c)
        if args.hasta_turno is not None:
            filas_validacion = c.execute("""
                SELECT * FROM turn_validation
                 WHERE campaign_id=%s AND turn_id <= %s
                 ORDER BY turn_id""", (campaign_id, args.hasta_turno)).fetchall()
        else:
            filas_validacion = c.execute("""
                SELECT * FROM turn_validation WHERE campaign_id=%s
                 ORDER BY turn_id""", (campaign_id,)).fetchall()

    imprimir_resumen(resumen_turn_validation(filas_validacion))

    turnos = camp.turnos_narracion()
    if args.hasta_turno is not None:
        # Recorte a posteriori, no en SQL: turnos_narracion() es compartida
        # con otros usos y no vale la pena parametrizarla solo por esto --
        # el volumen de una campaña (miles de turnos como máximo) no
        # justifica evitar traer todo y filtrar en Python.
        turnos = [t for t in turnos if t["turn_id"] <= args.hasta_turno]
    ubicaciones = [e for e in camp.entidades() if e["tipo"] == "location"]
    imprimir_bucles(detector_bucles(turnos, ubicaciones))

    turnos_por_id = {f["turn_id"]: f["dm_output"] for f in turnos}
    relojes = camp.relojes_disparados()
    if args.hasta_turno is not None:
        relojes = [r for r in relojes if r["fired_at_turn"] <= args.hasta_turno]
    imprimir_relojes(relojes_no_reconocidos(relojes, turnos_por_id))

    C, L_efectivo, detalle_c = coherencia_entidad_C(turnos, camp.entidades())
    V, detalle_v = consistencia_atributos_V(turnos, camp.entidades())
    imprimir_papalampidi(C, L_efectivo, detalle_c, V, detalle_v)

    deltas = camp.deltas_narrables()
    if args.hasta_turno is not None:
        deltas = [d for d in deltas if d["turn_id"] <= args.hasta_turno]
    imprimir_jericho_qa(jericho_qa_recall(deltas, turnos_por_id))

    imprimir_entity_coreference(entity_coreference_rate(turnos, camp.entidades()))

    imprimir_grammaticality(reporte_grammaticality(turnos))

    imprimir_grafo_lema(reporte_grafo_lema(turnos, camp.entidades()))

    imprimir_pnj_inactivo_refinado(
        pnj_inactivo_refinado(filas_validacion, turnos_por_id, camp.entidades()))

    print(f"\n{'='*74}\n")


if __name__ == "__main__":
    main()
