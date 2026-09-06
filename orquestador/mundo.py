r"""
Agente del Mundo de G1 — híbrido: código para lo que el esquema ya
resuelve sin juicio (relojes, lugares congelados, cola de semillas),
LLM solo para lo que sí es creativo (el texto del boceto, qué semilla
plantar y con qué palabras, propagación a PNJ con vínculo, tono de
ritmo). Mismo patrón que orquestador/arbitro.py y orquestador/router.py.

Por qué esto es lo más importante para Coherencia Longitudinal: es el
único de los cinco roles cuyo trabajo es EXACTAMENTE mantener el mundo
persistente y consistente frente a la acción del jugador turno a turno
-- no solo generarlo una vez. Un reloj que no avanza cuando debía, un
lugar que cambia de descripción cada vez que el jugador vuelve, o una
semilla que nunca se planta, son exactamente los fallos que la métrica
de "consistencia de eventos y estado del mundo a largo plazo" tiene que
detectar. Por eso MUN-1/2 (relojes) y MUN-4/5/6 (lugares) se resuelven
en código: si dependieran del modelo acordándose, dejarían de ser
garantía y volverían a ser propiedad emergente frágil (ver
`QM - Lecciones de ingeniería` §3: "si el modelo tiene que adivinar
algo que la base sabe, dáselo").

`resolver_mundo()` es una función PURA a propósito: recibe lo que
orquestador/db.py ya leyó/escribió (relojes disparados, estado del
lugar, semillas candidatas) y decide qué de eso ya está resuelto y qué
necesita pasar al LLM. No toca Postgres ni llama a ningún modelo.
"""

# Tipos de lugar que el SRD/la campaña tratan como topología acoplada:
# MUN-7 exige planificarlos COMPLETOS antes de entrar, no en boceto.
LUGARES_COMPLETOS = {"dungeon", "ruin", "crypt"}


def resolver_mundo(lugar, eventos_reloj, semillas_candidatas, escena_pregunta=False):
    """
    lugar                 dict de db.lugar_estado(location_id), o None si
                          el turno no ocurre en ningún lugar registrado
                          todavía (lugar nuevo, aún no creado)
    eventos_reloj         lista de db.avanzar_relojes(...) -- ya avanzados
                          y evaluados contra el umbral, YA es verdad en la
                          base si algo hay aquí
    semillas_candidatas   lista de db.semillas_sin_ubicar(...)
    escena_pregunta       True si el Router/Árbitro marcaron que el
                          jugador preguntó algo concreto sobre el lugar
                          (dispara MUN-5: el detalle que dé el LLM ahora
                          queda fijo para siempre)

    Devuelve un objeto con lo ya resuelto en código y lo que falta
    decidir en `dm/prompt_mundo_g1.md`:

      eventos_reloj        tal cual, listos para el Narrador (MUN-1/2,
                            cero LLM -- el evento YA ocurrió en la base)
      lugar_repite          True + `descripcion` si el lugar ya estaba
                            congelado (`observed`/`full`): se repite la
                            MISMA descripción, cero LLM (MUN-6)
      lugar_necesita_boceto True si hay que generar texto nuevo: lugar
                            inexistente/`sketch` sin pregunta concreta
                            (boceto de trazo grueso, MUN-4), o con
                            pregunta concreta (detalle que se fijará,
                            MUN-5), o lugar `dungeon`/`ruin`/`crypt` que
                            nunca se planificó completo (MUN-7)
      fijar_al_responder    True si la respuesta del LLM debe congelarse
                            con `db.fijar_lugar()` -- solo cuando hay
                            pregunta concreta o el lugar exige plan
                            completo; un boceto de trazo grueso normal
                            NO se fija (sigue siendo `sketch` la próxima
                            vez, a propósito: MUN-4 no es MUN-5)
      semilla_candidata     la semilla más antigua sin plantar, o None
      necesita_llm          True si queda algo de lo anterior por escribir
    """
    lugar_repite = False
    descripcion_fija = None
    lugar_necesita_boceto = False
    fijar_al_responder = False

    if lugar is None:
        lugar_necesita_boceto = True
    elif lugar["kind"] in LUGARES_COMPLETOS and lugar["detail"] != "full":
        lugar_necesita_boceto = True
        fijar_al_responder = True
    elif lugar["detail"] in ("observed", "full"):
        lugar_repite = True
        descripcion_fija = lugar["description_canonical"]
    elif escena_pregunta:
        lugar_necesita_boceto = True
        fijar_al_responder = True
    else:
        lugar_necesita_boceto = True  # sketch, sin pregunta: boceto normal

    semilla_candidata = semillas_candidatas[0] if semillas_candidatas else None

    return {
        "eventos_reloj": list(eventos_reloj),
        "lugar_repite": lugar_repite,
        "descripcion": descripcion_fija,
        "lugar_necesita_boceto": lugar_necesita_boceto,
        "fijar_al_responder": fijar_al_responder,
        "semilla_candidata": semilla_candidata,
        "necesita_llm": lugar_necesita_boceto or semilla_candidata is not None,
    }
