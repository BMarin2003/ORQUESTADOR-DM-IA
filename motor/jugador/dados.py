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

  Ojo (corregido 2026-10-09): G1 y G2 NO reciben la misma secuencia de
  tiradas. Cada brazo tiene su propia fila en `campaigns` (UUID distinto), y
  ese id entra en la semilla. Verificado en 21 pares con
  experimento/scripts/verificacion/verificar_dados_pareados.py: el d20 coincide en 4.9 %
  de las tiradas comparables, lo esperable por azar. Lo que sí se cumple: el
  mecanismo es el mismo, el agente no tira, y la suerte no favorece a ningún
  brazo (d20 medio G1 − G2 = +0.009; Wilcoxon p = 0.95).
"""

import hashlib
import re
import unicodedata

MODIFICADORES = {
    # nivel 3, reparto típico. Tabla de respaldo: se usa cuando no hay
    # tabla de personaje real disponible (compatibilidad con campañas
    # viejas y, por ahora, con NPC). Desde 2026-09-16, `resolver_turno()`
    # puede recibir la tabla `modificadores` real de la ficha del PJ
    # (generada en `generar_personajes.py`, por clase, con el standard
    # array de D&D 5e) -- cuando la recibe, esta tabla plana ya no se usa
    # para las 18 habilidades de abajo, solo queda de respaldo.
    "atletismo": 5, "acrobacias": 4, "sigilo": 5, "juego de manos": 4,
    "arcanos": 4, "historia": 3, "investigación": 3, "naturaleza": 2,
    "religión": 2, "perspicacia": 3, "medicina": 2, "percepción": 4,
    "supervivencia": 3, "trato con animales": 2,
    "engaño": 4, "intimidación": 4, "interpretación": 3, "persuasión": 4,
}

# Las 6 características base de D&D 5e. Son mecánica válida del SRD tanto
# para chequeos de característica pura como para salvaciones (el jugador
# declara p. ej. {Destreza} sin habilidad específica asociada) -- pero,
# a diferencia de las 18 habilidades de arriba, NO tienen una tabla plana
# de respaldo: los modificadores dependen de la clase de cada personaje
# (un Paladín y un Mago no tienen la misma Sabiduría), así que solo se
# aceptan cuando `resolver_turno()` recibe la tabla de modificadores real
# del PJ activo. Sin esa tabla (p. ej. Par 02, que sigue con el motor tal
# como estaba al detenerse), se siguen rechazando como "NO EXISTE" -- no
# tirar es preferible a tirar con un número inventado, mismo criterio que
# ya aplicaba el resto del archivo.
CARACTERISTICAS = {
    "fuerza", "destreza", "constitución",
    "inteligencia", "sabiduría", "carisma",
}


def normalizar(t):
    """Quita tildes y baja a minúsculas.

    'Persuasion' sin tilde no debe fallar la búsqueda del modificador: el
    modelo escribiría +3 por defecto en vez del +4 correcto, y eso sesga
    las tiradas sin que nadie lo note."""
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn").strip()


def _semilla(campaign_id, turn_id, etiqueta, intento=0):
    """Semilla entera determinista (SHA-256 de campaña|turno|etiqueta|intento): misma entrada, misma tirada."""
    crudo = f"{campaign_id}|{turn_id}|{etiqueta.lower()}|{intento}"
    return int(hashlib.sha256(crudo.encode()).hexdigest()[:16], 16)


def tirar(campaign_id, turn_id, etiqueta, modificador=None, ventaja=0, intento=0,
          tabla_modificadores=None):
    """Tira 1d20 + modificador. `ventaja` = +1 con ventaja, -1 con desventaja.

    `tabla_modificadores`, si se pasa, es la tabla real del PJ activo
    (`pj["modificadores"]`, de `generar_personajes.py`) y tiene prioridad
    sobre la tabla plana `MODIFICADORES` -- así cada personaje tira con
    sus propios números, no con el reparto genérico compartido."""
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
        clave = normalizar(etiqueta)
        if tabla_modificadores is not None:
            tabla_pj = {normalizar(k): v for k, v in tabla_modificadores.items()}
        else:
            tabla_pj = {}
        if clave in tabla_pj:
            mod = tabla_pj[clave]
        else:
            tabla = {normalizar(k): v for k, v in MODIFICADORES.items()}
            mod = tabla.get(clave, 3)
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
CARACTERISTICAS_NORM = {normalizar(k) for k in CARACTERISTICAS}


# --- Tiradas de combate (2026-09-19, para Par 18+) -------------------------
# En Par 07-17 el jugador declaró {Ataque}/{Iniciativa}/{Ataque mágico} ~100
# veces y el motor respondía "NO EXISTE — no se tira": sin tirada, el DM
# monolítico (G2) pedía la tirada al jugador en un meta-mensaje (106 turnos;
# G1 nunca, su Árbitro tiene salida para "sin tirada"). Ahora existen, con el
# modificador real del PJ, para los dos brazos por igual.
PROFICIENCIA = 2   # nivel 3
HABILIDAD_CONJURO = {"mago": "inteligencia", "clerigo": "sabiduria",
                     "explorador": "sabiduria", "bardo": "carisma",
                     "brujo": "carisma", "paladin": "carisma"}


def tabla_pj(pj):
    """`pj["modificadores"]` + ataque / ataque magico (solo lanzadores) /
    iniciativa, calculados de las características de la ficha (mod + competencia)."""
    car = {normalizar(k): (v - 10) // 2 for k, v in pj["caracteristicas"].items()}
    tabla = dict(pj["modificadores"])
    tabla["ataque"] = max(car["fuerza"], car["destreza"]) + PROFICIENCIA
    tabla["iniciativa"] = car["destreza"]
    conj = HABILIDAD_CONJURO.get(normalizar(pj["clase"]))
    if conj:
        tabla["ataque magico"] = car[conj] + PROFICIENCIA
    return tabla


def _combate(clave):
    """Lo que el jugador escribe -> clave de tabla_pj, o None. Acepta variantes
    como {Ataque con la daga}, {Ataque de conjuro}, {Ataque furtivo}."""
    if clave.startswith("iniciativa"):
        return "iniciativa"
    if clave.startswith("ataque"):
        return "ataque magico" if re.search(r"magic|conjuro|hechizo", clave) else "ataque"
    return None


# --- Red de seguridad contra DM fuera de personaje (2026-09-19, Par 18+) ----
# Mismo patrón que el paso [5] de verificación de los dos motores.
META_OOC = re.compile(r"\[[^\]]{20,}\]")
AVISO_META = ("\n\nAVISO DEL SISTEMA: tu respuesta anterior salió del papel (pedía una "
              "tirada al jugador o comentaba las reglas entre corchetes). Las tiradas las "
              "resuelve el sistema; el jugador nunca tira. Responde SOLO con narración "
              "dentro de la ficción, sin corchetes: resuelve la acción con el desenlace "
              "más plausible para la escena y detente donde el jugador deba decidir.")


def es_meta_ooc(narracion):
    """True si la narración contiene un fragmento entre corchetes de 20+ caracteres, señal de DM fuera de personaje."""
    return bool(META_OOC.search(narracion or ""))


def quitar_meta_ooc(narracion):
    """Último recurso tras agotar reintentos: borra los [..] y conserva el resto si
    aún es una narración (>= 80 caracteres); si no, devuelve el texto tal cual."""
    limpio = META_OOC.sub("", narracion).strip()
    return limpio if len(limpio) >= 80 else narracion


def resolver_turno(texto_jugador, campaign_id, turn_id, tabla_modificadores=None):
    """Sustituye cada {habilidad} declarada por su resultado ya tirado.

    `tabla_modificadores`, si se pasa, es `pj["modificadores"]` del
    personaje activo -- se la pasa tal cual a `tirar()`, y además habilita
    las 6 características base (ver `CARACTERISTICAS` arriba): sin esta
    tabla, {Destreza}/{Sabiduría}/etc. se siguen rechazando como antes.

    Devuelve (texto_para_el_dm, tiradas). El DM recibe el texto con
    '(resultado: N total)' en la sintaxis que ya conoce.
    """
    tiradas = []
    resultado = texto_jugador

    tabla_pj_norm = ({normalizar(k) for k in tabla_modificadores}
                      if tabla_modificadores is not None else set())

    rechazadas = []
    for i, hab in enumerate(extraer_habilidades(texto_jugador)):
        clave = normalizar(hab.split(" para ")[0])
        # Una habilidad/característica que no existe, o que existe pero no
        # tiene de dónde sacar un modificador real, NO se tira. Antes caía
        # al +3 por defecto y metía tiradas fantasma en el registro
        # mecánico: el jugador declaraba {Montar} o {Negociación} y el
        # sistema le daba un resultado como si fueran habilidades reales.
        # Las características base (Destreza, Sabiduría...) son mecánica
        # válida del SRD, pero solo se aceptan cuando hay tabla de
        # personaje real -- no tienen tabla plana de respaldo a propósito
        # (ver `CARACTERISTICAS` arriba).
        es_habilidad_valida = clave in VALIDAS
        es_caracteristica_con_pj = clave in CARACTERISTICAS_NORM and clave in tabla_pj_norm
        comb = _combate(clave)
        es_combate_con_pj = comb is not None and comb in tabla_pj_norm
        if not (es_habilidad_valida or es_caracteristica_con_pj or es_combate_con_pj):
            rechazadas.append(hab)
            resultado = resultado.replace("{" + hab + "}", hab, 1)
            continue
        # Las de combate no están por su nombre literal en la tabla ("ataque con
        # la daga"): se pasa el modificador ya resuelto, no el de la etiqueta.
        mod_combate = ({normalizar(k): v for k, v in tabla_modificadores.items()}[comb]
                       if es_combate_con_pj else None)
        t = tirar(campaign_id, turn_id, hab, modificador=mod_combate, intento=i,
                  tabla_modificadores=tabla_modificadores)
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