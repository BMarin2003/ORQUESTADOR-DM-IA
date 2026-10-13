#!/usr/bin/env python3
"""
Genera los 27 personajes jugadores de las 27 campañas pareadas.

Por qué 27 distintos y por qué cubrir el espectro moral:
  El mismo personaje juega AMBOS brazos, así que la variación entre
  personajes es varianza entre pares, que el Wilcoxon pareado descarta por
  diseño. No añade ruido: añade generalización. Si el MAS gana con paladines
  y con villanos, el resultado es más robusto.

  Los grises mutables son los que más discriminan, porque exigen que el
  sistema rastree una evolución en vez de un rasgo fijo.

Ejes (los mismos que usan los PNJ, para que resolve_event sea comparable):
  warmth     frío y calculador ←→ cálido y afectuoso
  candor     disimulado ←→ franco
  principle  pragmático ←→ principista
  boldness   cauto ←→ audaz

Y dos parámetros propios del jugador:
  desvio     cuánto persigue lo suyo frente a los ganchos del DM
  deriva     si sus ejes se mueven durante la campaña (grises mutables)

Estadísticas D&D 5e (nuevo 2026-09-16):
  Hasta ahora `motor/jugador/dados.py` tiraba con una tabla de modificadores PLANA
  y compartida por los 27 personajes -- un Paladín de juramento y un
  Nigromante académico tiraban exactamente igual. Eso no es correcto: cada
  arquetipo trae su propia clase, y la clase debería determinar en qué es
  bueno. Se agrega aquí, por ficha, `caracteristicas` (las 6 puntuaciones
  base, standard array 15/14/13/12/10/8 asignado por prioridad de clase) y
  `modificadores` (las 24 entradas -- 6 características + 18 habilidades --
  ya calculadas, listas para que `dados.py` las use en vez de su tabla
  global). Es determinista: la prioridad por clase es fija, no consume del
  generador `random`.

Uso:  python3 generar_personajes.py > personajes_jugadores.json
"""

import json
import random

random.seed(20260901)   # reproducible: los mismos 27 en cada ejecución

ARQUETIPOS = [
    # (nombre, clase, warmth, candor, principle, boldness, desvio, deriva)
    ("Paladín de juramento",      "paladín",   45,  85,  92,  70, 25, None),
    ("Clériga de la ley",         "clérigo",   30,  75,  88,  40, 20, None),
    ("Guardián del bosque",       "explorador",55,  60,  75,  55, 45, None),
    ("Caballera caída",           "guerrero",  20,  55,  60,  75, 40, "principle:-2"),
    ("Bardo de causa justa",      "bardo",     70,  40,  65,  80, 55, None),

    ("Mercenaria pragmática",     "guerrero",   0, -20,   5,  65, 60, None),
    ("Ladrón con código",         "pícaro",    25, -40,  35,  70, 65, None),
    ("Mago calculador",           "mago",     -20,  10,  20,  30, 50, None),
    ("Contrabandista amable",     "pícaro",    60, -55,  -5,  60, 70, None),
    ("Cazarrecompensas neutral",  "explorador",-10,  20,  15,  70, 55, None),
    ("Erudita obsesiva",          "mago",       5,  50,  25,  35, 80, None),
    ("Superviviente del camino",  "bárbaro",   15, -10,   0,  55, 60, None),

    ("Antihéroe vengativo",       "bárbaro",  -30, -60,  45,  90, 70, "warmth:+2"),
    ("Espía de dos caras",        "pícaro",    10, -85,  30,  50, 75, "candor:+3"),
    ("Bruja del pacto",           "brujo",    -25, -30,  40,  60, 65, None),
    ("Inquisidor implacable",     "paladín",  -45,  70,  80,  75, 35, "principle:-3"),
    ("Médica de guerra",          "clérigo",   65,  45,  55,  30, 50, None),

    ("Oportunista sin bandera",   "pícaro",   -35, -70, -45,  65, 85, None),
    ("Señor de la guerra",        "guerrero", -50, -25, -60,  95, 75, None),
    ("Estafador de sonrisa fácil","bardo",     40, -90, -55,  70, 80, None),
    ("Nigromante académico",      "mago",     -60,  15, -40,  45, 70, None),
    ("Sicario metódico",          "pícaro",   -70, -50, -70,  60, 55, None),
    ("Fanático del culto",        "brujo",    -55,  35, -30,  85, 45, "principle:-2"),

    # Grises mutables — los más discriminantes
    ("Huérfana de la frontera",   "explorador",30, -15,  10,  50, 65, "principle:+4"),
    ("Noble desheredado",         "guerrero",  10,  30,  50,  45, 60, "principle:-4"),
    ("Devota con dudas",          "clérigo",   50,  60,  70,  35, 55, "candor:-4"),
    ("Bárbaro que aprende",       "bárbaro",   35, -35, -20,  80, 70, "warmth:+4"),
]

NOMBRES = [
    "Ilvard", "Senna", "Torvald", "Maelis", "Corvin", "Yarah", "Dunmar",
    "Reia", "Aldric", "Bexa", "Solvei", "Harn", "Mirek", "Vessa", "Otto",
    "Lianne", "Garrek", "Nadia", "Bram", "Kestra", "Elior", "Wynn",
    "Tarq", "Isolde", "Fenn", "Marta", "Osric",
]

TRASFONDOS = ["forastero", "artesano", "soldado", "criminal", "acólito",
              "noble", "huérfano", "marinero", "erudito"]


# --------------------------------------------------------------- D&D 5e ---

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
PROFICIENCIA = 2  # nivel 3, todas las clases

# Orden de prioridad de las 6 características por clase (mayor a menor).
# El standard array se reparte en ese orden -- así cada clase sale con un
# perfil de puntuaciones coherente con su rol, sin necesitar random.
PRIORIDAD_CLASE = {
    "paladín":    ["carisma", "fuerza", "constitución", "sabiduría", "destreza", "inteligencia"],
    "clérigo":    ["sabiduría", "constitución", "fuerza", "carisma", "destreza", "inteligencia"],
    "explorador": ["destreza", "sabiduría", "constitución", "fuerza", "carisma", "inteligencia"],
    "guerrero":   ["fuerza", "constitución", "destreza", "sabiduría", "carisma", "inteligencia"],
    "bardo":      ["carisma", "destreza", "constitución", "sabiduría", "inteligencia", "fuerza"],
    "pícaro":     ["destreza", "carisma", "constitución", "inteligencia", "sabiduría", "fuerza"],
    "mago":       ["inteligencia", "constitución", "destreza", "sabiduría", "carisma", "fuerza"],
    "bárbaro":    ["fuerza", "constitución", "destreza", "sabiduría", "carisma", "inteligencia"],
    "brujo":      ["carisma", "constitución", "destreza", "sabiduría", "inteligencia", "fuerza"],
}

# Salvaciones competentes por clase (SRD, 2 por clase).
SALVACIONES_CLASE = {
    "paladín":    {"sabiduría", "carisma"},
    "clérigo":    {"sabiduría", "carisma"},
    "explorador": {"fuerza", "destreza"},
    "guerrero":   {"fuerza", "constitución"},
    "bardo":      {"destreza", "carisma"},
    "pícaro":     {"destreza", "inteligencia"},
    "mago":       {"inteligencia", "sabiduría"},
    "bárbaro":    {"fuerza", "constitución"},
    "brujo":      {"sabiduría", "carisma"},
}

# Habilidad -> característica ligada (SRD).
HABILIDAD_CARACTERISTICA = {
    "atletismo": "fuerza",
    "acrobacias": "destreza", "sigilo": "destreza", "juego de manos": "destreza",
    "arcanos": "inteligencia", "historia": "inteligencia",
    "investigación": "inteligencia", "naturaleza": "inteligencia",
    "religión": "inteligencia",
    "perspicacia": "sabiduría", "medicina": "sabiduría",
    "percepción": "sabiduría", "supervivencia": "sabiduría",
    "trato con animales": "sabiduría",
    "engaño": "carisma", "intimidación": "carisma",
    "interpretación": "carisma", "persuasión": "carisma",
}

# Habilidades "de afinidad" por clase (competencia típica del arquetipo).
AFINIDAD_CLASE = {
    "paladín":    {"atletismo", "perspicacia", "intimidación", "persuasión", "religión"},
    "clérigo":    {"perspicacia", "medicina", "persuasión", "religión", "historia"},
    "explorador": {"naturaleza", "percepción", "sigilo", "supervivencia", "trato con animales"},
    "guerrero":   {"atletismo", "intimidación", "percepción", "supervivencia"},
    "bardo":      {"interpretación", "persuasión", "engaño", "historia", "perspicacia"},
    "pícaro":     {"sigilo", "juego de manos", "engaño", "percepción", "acrobacias"},
    "mago":       {"arcanos", "historia", "investigación", "religión"},
    "bárbaro":    {"atletismo", "intimidación", "percepción", "supervivencia"},
    "brujo":      {"arcanos", "engaño", "intimidación", "investigación", "persuasión"},
}


def modificador(puntuacion):
    """Modificador estándar de D&D 5e: (puntuación - 10) // 2."""
    return puntuacion // 2 - 5


def generar_caracteristicas(clase):
    """Reparte el standard array (15/14/13/12/10/8) según la prioridad de
    la clase. Determinista: no consume random, la prioridad es fija."""
    orden = PRIORIDAD_CLASE[clase]
    return {hab: val for hab, val in zip(orden, STANDARD_ARRAY)}


def calcular_modificadores(clase, caracteristicas):
    """Las 24 entradas (6 características + 18 habilidades) que
    `motor/jugador/dados.py` usa para resolver una tirada. Característica pura:
    mod de la puntuación, +COMPETENCIA si la clase es competente en esa
    salvación. Habilidad: mod de su característica ligada, +COMPETENCIA
    si es una habilidad de afinidad de la clase."""
    mods = {}
    for hab, val in caracteristicas.items():
        base = modificador(val)
        if hab in SALVACIONES_CLASE[clase]:
            base += PROFICIENCIA
        mods[hab] = base
    for skill, carac in HABILIDAD_CARACTERISTICA.items():
        base = modificador(caracteristicas[carac])
        if skill in AFINIDAD_CLASE[clase]:
            base += PROFICIENCIA
        mods[skill] = base
    return mods


def agenda(arq, i):
    """Objetivos propios, independientes de lo que plantee el DM.

    Son la fuente de la agencia real: sin objetivos propios, el agente solo
    puede seguir o ignorar los ganchos, y 'desviarse' se vuelve ruido
    aleatorio en vez de intención.

    CUIDADO con las contradicciones internas. La primera versión daba
    "No volver a estar en deuda con nadie" a personajes principistas, y el
    modelo lo leía como "no acepto órdenes de autoridad" — lo que invertía
    el desvío bajo. Cada objetivo tiene que ser coherente con los ejes.
    """
    _, clase, w, c, p, b, desvio, deriva = arq
    base = []

    # Objetivo moral, alineado con `principle`
    if p > 50:
        base.append("Dejar el sitio mejor de como lo encontró, aunque nadie lo agradezca.")
    elif p < -30:
        base.append("Salir de aquí con más de lo que trajo, sin importar cómo.")
    else:
        base.append("Conseguir estabilidad: dinero, un techo, alguien de fiar.")

    # Objetivo de información, alineado con `candor`
    if c < -40:
        base.append("Averiguar algo que nadie más sepa y guardárselo hasta que valga.")
    elif c > 60:
        base.append("Que se sepa la verdad de lo que pasa aquí, le convenga a quien le convenga.")
    else:
        base.append("Entender qué está pasando de verdad en este sitio.")

    # Objetivo personal. La independencia solo para los que no son
    # principistas: en un principista contradice el respeto a la autoridad.
    if b > 70:
        base.append("Enfrentarse a algo que le dé miedo, para comprobar que puede.")
    elif w > 50:
        base.append("Proteger a alguien concreto que no puede protegerse solo.")
    elif p > 50:
        base.append("Estar a la altura de lo que se espera de alguien de su posición.")
    else:
        base.append("No volver a estar en deuda con nadie.")

    return base


def main():
    """Imprime por stdout el JSON de las fichas de los arquetipos (personalidad, agenda, características y modificadores) con semilla fija."""
    fichas = []
    for i, arq in enumerate(ARQUETIPOS):
        nombre_arq, clase, w, c, p, b, desvio, deriva = arq
        eje, delta = (deriva.split(":") if deriva else (None, None))
        caracteristicas = generar_caracteristicas(clase)
        fichas.append({
            "id": f"PJ{i+1:02d}",
            "nombre": NOMBRES[i],
            "arquetipo": nombre_arq,
            "clase": clase,
            "nivel": 3,
            "trasfondo": TRASFONDOS[i % len(TRASFONDOS)],
            "personalidad": {"warmth": w, "candor": c, "principle": p, "boldness": b},
            "ideal": None,      # se completa a mano o lo genera el arnés
            "vinculo": None,
            "defecto": None,
            "agenda": agenda(arq, i),
            "desvio": desvio,
            "deriva": ({"eje": eje, "por_sesion": int(delta)} if deriva else None),
            "caracteristicas": caracteristicas,
            "modificadores": calcular_modificadores(clase, caracteristicas),
            "_nota": ("Gris mutable: sus ejes se mueven durante la campaña, lo que "
                      "obliga al sistema a rastrear una evolución en vez de un rasgo fijo."
                      if deriva else None),
        })
    print(json.dumps({"_generado": "generar_personajes.py, semilla 20260901",
                      "_n": len(fichas), "personajes": fichas},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
