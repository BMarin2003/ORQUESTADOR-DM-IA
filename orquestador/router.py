r"""
Router de G1 — determinista, sin llamada a modelo.

Implementa el algoritmo fijado en docs/descomposicion_prompts.md §5.1, tras
la auditoría de paridad del 2026-09-04 (las 16 instrucciones que la matriz
le asignaba a un Router-LLM: la mayoría ya tenían respaldo en otro rol, y
las que no, son mecánicas — ver §8 y §9 de ese documento). Aquí solo está
el cómo; el porqué está allá.

`clasificar_turno()` es una función PURA a propósito: no toca Postgres ni
conoce el orquestador. Recibe como parámetros el historial que necesita.
Eso la hace testeable sin base de datos y sin red (ver
`probar_router.py`), y deja a la vista una decisión de diseño que el
orquestador real todavía tiene pendiente — ver el aviso al final de este
archivo sobre `turn_log`.
"""
import re

CORCHETES = re.compile(r"\[[^\]]+\]")
COMILLAS = re.compile(r"\"[^\"]+\"")
TIRADA = re.compile(r"\(resultado:\s*(\d+)[^)]*\)")

# Verbos de intención: si aparecen, el turno probablemente altera el mundo
# aunque no haya tirada de por medio ("le entrego el mapa" no tira nada,
# pero sí es un delta que el Árbitro debería poder pesar). Es una
# heurística, no un contrato: un falso positivo aquí solo cuesta una
# llamada de más al Árbitro, no rompe nada río abajo.
VERBOS_INTENCION = re.compile(
    r"\b(atac\w*|rob\w*|promet\w*|amenaz\w*|soborn\w*|entreg\w*|revel\w*|"
    r"mat[oó]\w*|matar\w*|liber\w*)\b", re.I)

VENTANA_AMBIENTAL = 2  # turnos de enfriamiento — SAL-6, ver §9: se aplica
                        # igual delante de G2 y de G1, no es exclusivo de aquí


def clasificar_turno(buffer, npcs_presentes, ultimo_pnj_hablo=None,
                      historial_modos=()):
    """
    buffer              texto del jugador YA procesado por dados.resolver_turno()
                        (con {llaves} sustituidas por "(resultado: N ...)";
                        dados.py deja el texto sin llaves salvo que la
                        habilidad no exista, en cuyo caso solo quita las
                        llaves sin añadir resultado)
    npcs_presentes      nombres de los PNJ en la escena, en cualquier orden
    ultimo_pnj_hablo    nombre del PNJ que intervino en el turno anterior,
                        o None si no hubo ninguno
    historial_modos     modos de los últimos VENTANA_AMBIENTAL turnos,
                        más reciente al final — p.ej. ("en_rol", "ambiental")

    Devuelve el objeto de clasificación tal como lo describe §5.1:
        modo, requiere_arbitro, pnj_que_responden, altera_estado, peso
    """
    # 1. fuera de rol — pisa todo lo demás
    if CORCHETES.search(buffer):
        return {
            "modo": "fuera_de_rol",
            "requiere_arbitro": True,
            "pnj_que_responden": [],
            "altera_estado": False,
            "peso": "conversacional",
        }

    # 2. extraer
    tiradas = TIRADA.findall(buffer)

    # 3. a quién habla — nombrado explícito, en el orden en que aparece en
    #    el texto (no el orden de la lista npcs_presentes)
    nombrados = [n for n in npcs_presentes if n.lower() in buffer.lower()]
    if nombrados:
        pnj_que_responden = sorted(
            nombrados, key=lambda n: buffer.lower().find(n.lower()))
    elif len(npcs_presentes) == 1:
        pnj_que_responden = list(npcs_presentes)
    elif npcs_presentes and ultimo_pnj_hablo in npcs_presentes:
        pnj_que_responden = [ultimo_pnj_hablo]
    else:
        pnj_que_responden = []

    # 4. altera_estado
    altera_estado = bool(tiradas) or bool(VERBOS_INTENCION.search(buffer))

    # 5. modo — ambiental/silencio solo si de verdad nada interpela
    hay_interpelacion = bool(pnj_que_responden) or bool(tiradas) or "?" in buffer
    if not hay_interpelacion:
        ultimos = list(historial_modos[-VENTANA_AMBIENTAL:])
        modo = "silencio" if "ambiental" in ultimos else "ambiental"
        return {
            "modo": modo,
            "requiere_arbitro": False,
            "pnj_que_responden": [],
            "altera_estado": False,
            "peso": "trivial",
        }

    # 6. peso
    n_palabras = len(buffer.split())
    if not tiradas and n_palabras < 40 and not pnj_que_responden:
        peso = "trivial"
    elif tiradas or altera_estado or len(pnj_que_responden) > 1:
        peso = "consecuente"
    else:
        peso = "conversacional"

    return {
        "modo": "en_rol",
        "requiere_arbitro": altera_estado,
        "pnj_que_responden": pnj_que_responden,
        "altera_estado": altera_estado,
        "peso": peso,
    }


# ──────────────────────────────────────────────────────────────────────
# RESUELTO (2026-09-06): `turn_log` ya tiene router_modo y router_last_npc
# (migrations/001_schema.sql, commit f516b54). El orquestador real arma
# los dos argumentos que faltan así:
#
#   historial_modos, ultimo_pnj_hablo = campaña.historial_router()
#   clasif = clasificar_turno(buffer, npcs_presentes,
#                             ultimo_pnj_hablo, historial_modos)
#   ... (turno completo) ...
#   campaña.registrar_turno(turn_id, buffer, dm_output, gate_passed,
#                           router_modo=clasif["modo"],
#                           router_last_npc=campaña.id_de(
#                               "npc", clasif["pnj_que_responden"][0])
#                               if clasif["pnj_que_responden"] else None)
#
# Ver orquestador/db.py: Campaña.historial_router() y el registrar_turno()
# ampliado. Sigue siendo NULL en G2 (ese brazo no tiene Router).
# ──────────────────────────────────────────────────────────────────────
