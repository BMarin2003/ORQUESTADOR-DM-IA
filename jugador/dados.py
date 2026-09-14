"""
Dados deterministas.

Por qué el agente NO tira:
  Si el jugador agéntico escribe "(resultado: 18)", va a sesgar alto — no por
  malicia, sino porque los modelos favorecen resultados narrativamente
  convenientes. Eso contaminaría las 54 campañas de forma invisible y por
  igual, haciendo que las tiradas dejen de ser aleatorias sin que nadie lo
  note.

  El agente declara la acción y la habilidad. El sistema tira.

Por qué sembrado:
  Con (campaña, turno, habilidad) como semilla, la misma campaña produce las
  mismas tiradas al reejecutarse. Eso hace las campañas reproducibles y
  permite reprocesar sin que cambien los resultados mecánicos.

  Y crucialmente: **ambos brazos del par reciben la misma secuencia de
  tiradas**, porque comparten campaign_id. Si G1 y G2 divergen, no es porque
  a uno le fueran mejor los dados.
"""

import hashlib
import re
import unicodedata

MODIFICADORES = {
    # nivel 3, reparto típico. En producción sale de la ficha real.
    "atletismo": 5, "acrobacias": 4, "sigilo": 5, "juego de manos": 4,
    "arcanos": 4, "historia": 3, "investigación": 3, "naturaleza": 2,
    "religión": 2, "perspicacia": 3, "medicina": 2, "percepción": 4,
    "supervivencia": 3, "trato con animales": 2,
    "engaño": 4, "intimidación": 4, "interpretación": 3, "persuasión": 4,
}


def normalizar(t):
    """Quita tildes y baja a minúsculas.

    'Persuasion' sin tilde no debe fallar la búsqueda del modificador: el
    modelo escribiría +3 por defecto en vez del +4 correcto, y eso sesga
    las tiradas sin que nadie lo note."""
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn").strip()


def _semilla(campaign_id, turn_id, etiqueta, intento=0):
    crudo = f"{campaign_id}|{turn_id}|{etiqueta.lower()}|{intento}"
    return int(hashlib.sha256(crudo.encode()).hexdigest()[:16], 16)


def tirar(campaign_id, turn_id, etiqueta, modificador=None, ventaja=0, intento=0):
    """Tira 1d20 + modificador. `ventaja` = +1 con ventaja, -1 con desventaja."""
    s = _semilla(campaign_id, turn_id, etiqueta, intento)
    d1 = (s % 20) + 1
    d2 = ((s >> 32) % 20) + 1
    if ventaja > 0:
        dado, par = max(d1, d2), (d1, d2)
    elif ventaja < 0:
        dado, par = min(d1, d2), (d1, d2)
    else:
        dado, par = d1, (d1,)

    if modificador is None:
        tabla = {normalizar(k): v for k, v in MODIFICADORES.items()}
        mod = tabla.get(normalizar(etiqueta), 3)
    else:
        mod = modificador
    return {
        "etiqueta": etiqueta,
        "dado": dado,
        "dados": par,
        "modificador": mod,
        "total": dado + mod,
        "critico": dado == 20,
        "pifia": dado == 1,
    }


PATRON_HABILIDAD = re.compile(r"\{([^}]{2,40})\}")


def extraer_habilidades(texto):
    """Las {llaves} con que el jugador declara qué quiere tirar."""
    return [m.strip() for m in PATRON_HABILIDAD.findall(texto)]


VALIDAS = {normalizar(k) for k in MODIFICADORES}


def resolver_turno(texto_jugador, campaign_id, turn_id):
    """Sustituye cada {habilidad} declarada por su resultado ya tirado.

    Devuelve (texto_para_el_dm, tiradas). El DM recibe el texto con
    '(resultado: N total)' en la sintaxis que ya conoce.
    """
    tiradas = []
    resultado = texto_jugador

    rechazadas = []
    for i, hab in enumerate(extraer_habilidades(texto_jugador)):
        # Una habilidad que no existe NO se tira. Antes caía al +3 por
        # defecto y metía tiradas fantasma en el registro mecánico: el
        # jugador declaraba {Montar} o {Negociación} y el sistema le daba
        # un resultado como si fueran habilidades reales.
        if normalizar(hab.split(" para ")[0]) not in VALIDAS:
            rechazadas.append(hab)
            resultado = resultado.replace("{" + hab + "}", hab, 1)
            continue
        t = tirar(campaign_id, turn_id, hab, intento=i)
        tiradas.append(t)
        marca = f"{hab} (resultado: {t['total']} total"
        if t["critico"]:
            marca += ", crítico"
        elif t["pifia"]:
            marca += ", pifia"
        marca += ")"
        resultado = resultado.replace("{" + hab + "}", marca, 1)

    return resultado, tiradas, rechazadas


PATRON_NUMERO_INVENTADO = re.compile(
    r"\(\s*resultado\s*:\s*\d+|"          # el jugador escribió su propio total
    r"\bsaco\s+un\s+\d+|\bsaqué\s+un\s+\d+|"
    r"\btiro\s+un\s+\d+|\bd20\s*[:=]\s*\d+", re.I)


def detecta_dado_inventado(texto):
    """El jugador nunca debe escribir un número de tirada."""
    return bool(PATRON_NUMERO_INVENTADO.search(texto))