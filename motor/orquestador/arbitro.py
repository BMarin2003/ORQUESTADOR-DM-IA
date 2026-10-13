r"""
Árbitro de G1 — híbrido: código puro para el camino mecánico, LLM solo
donde de verdad hace falta juicio.

Por qué híbrido y no todo-LLM ni todo-código, ver docs/especificaciones/descomposicion_prompts.md
§5.2 y la discusión de 2026-09-06 (QM - Ruta crítica en el vault): la tabla
de presupuesto de latencia de QM - Composición G1 dice "Árbitro mecánico sin
LLM (−6,7s) — la aritmética es código; el modelo solo para el tutor OOC".
Eso es exacto cuando ya hay una tirada — `dados.py` ya hizo la aritmética del
d20, aquí solo falta compararla contra una CD. Pero dos casos SÍ necesitan
juicio y no están en esa frase: NUN-5 (una solución ingeniosa sin tirada
previa puede funcionar igual) y el propio modo tutor. Esta función cubre
SOLO el camino mecánico; el resto vive en motor/dm/prompt_arbitro_g1.md.

`resolver_veredicto()` es una función PURA a propósito, igual que
`clasificar_turno()` de router.py: no toca Postgres ni llama a ningún
modelo. El orquestador real le pasa la banda de disposición ya resuelta
(disposition_band() en Postgres) — esta función no la calcula.
"""
import re

TIRADA = re.compile(r"\(resultado:\s*(\d+)[^)]*\)")

# SRD 5.2 (CC-BY-4.0), tabla "Typical Difficulty Classes": Muy fácil 5,
# Fácil 10, Media 15, Difícil 20, Muy difícil 25, Casi imposible 30.
# Sin ningún dato en el esquema que fije la dificultad de una acción
# concreta (ningún lugar/objeto guarda una "CD"), el propio DMG del SRD
# recomienda partir de Media (15) cuando no hay razón para desviarse.
# No es una invención nuestra: es el default que el manual mismo sugiere
# para este caso exacto.
CD_DEFECTO = 15

# PNJ-16: "la disposición modifica las CD sociales: hostil +5, indiferente
# base, amistoso −5". disposition_band() (Postgres) devuelve 7 bandas; la
# instrucción original solo define 3 niveles, así que las 7 se agrupan sin
# inventar más granularidad de la que el contrato pide:
#   hostile, wary   → hostil      (+5, más difícil convencerlo)
#   cold, neutral, cordial → indiferente (0, base)
#   loyal, devoted  → amistoso    (−5, más fácil)
MODIFICADOR_DISPOSICION = {
    "hostile": 5, "wary": 5,
    "cold": 0, "neutral": 0, "cordial": 0,
    "loyal": -5, "devoted": -5,
}


def resolver_veredicto(buffer, altera_estado, banda_disposicion=None):
    """
    buffer              texto del turno YA procesado por dados.resolver_turno()
    altera_estado       clasificar_turno(...)["altera_estado"] del Router —
                        si hubo verbo de intención sin tirada, esta función
                        no puede resolverlo sola (NUN-5) y lo señala
    banda_disposicion   una de las 7 bandas de disposition_band() para el
                        PNJ interpelado, o None si no aplica (acción física,
                        no social, o ningún PNJ presente)

    Devuelve:
      None                          — no había nada que resolver (no debería
                                      llamarse: el Router ya decide
                                      requiere_arbitro=False en ese caso)
      {"necesita_juicio": True}     — pásalo a motor/dm/prompt_arbitro_g1.md,
                                      modo "veredicto_sin_tirada"
      {"necesita_juicio": False,
       "veredicto", "cd", "resultado",
       "recurso_consumido", "correccion_al_jugador"}
                                    — resuelto en código, listo para el
                                      Narrador tal cual
    """
    tirada = TIRADA.search(buffer)

    if not tirada:
        if altera_estado:
            return {"necesita_juicio": True}
        return None

    resultado = int(tirada.group(1))
    cd = CD_DEFECTO + MODIFICADOR_DISPOSICION.get(banda_disposicion, 0)

    return {
        "necesita_juicio": False,
        "veredicto": "éxito" if resultado >= cd else "fallo",
        "cd": cd,
        "resultado": resultado,
        # ENT-4 ({llaves} de objeto/recurso): dados.py ya quitó las llaves
        # para cuando el buffer llega aquí, así que identificar qué objeto
        # se usó requiere comparar contra characters.inventory o juicio del
        # modelo. No se resuelve a medias: queda para cuando se conecte el
        # Mundo, que es quien de verdad toca inventario (apply_delta).
        "recurso_consumido": None,
        "correccion_al_jugador": None,
    }
