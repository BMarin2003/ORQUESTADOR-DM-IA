#!/usr/bin/env python3
r"""
SONDEO 1 — Las dos pruebas que pueden obligar a rediseñar.

1A COMPOSICIÓN
   Al Narrador se le dan tres fragmentos (veredicto del Árbitro, línea
   TEXTUAL del Actor, boceto del Mundo) y se mira si produce un párrafo o
   un collage. Si sale collage, G1 pierde por ingeniería y no por
   arquitectura — y eso es un confundido en el corazón del experimento.

1B ACTOR A vs B
   A = prompt largo con las once reglas de magnitud; el modelo juzga.
   B = prompt corto con la línea de `outcome` ya resuelta por la tabla.
   Decide si el juicio de reacción vive en el modelo o en la base.

Verificaciones automáticas (lo demás se lee a ojo):
   · ¿la cita del Actor aparece LITERAL en la salida del Narrador?
   · ¿se contradijo el veredicto mecánico?
   · ¿narró acciones del PJ? (violación de la regla de oro)

Uso:
   py sondeos\sondeo_1.py --modelo google/gemma-4-31B-it
   py sondeos\sondeo_1.py --modelo google/gemma-4-31B-it --solo 1a
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

BASE = "https://api.deepinfra.com/v1/openai"

# ---------------------------------------------------------------- 1A insumos
# Turno T07 de los fixtures: Kael ofrece dos coronas a la Sargento Brea.
# Brea tiene principle +95 → la oferta ES la ofensa.

BUFFER_T07 = '''Kael: "Sargento. Dos coronas y usted no vio a nadie cruzar anoche."
Kael: Le ofrezco las monedas con la palma abierta.'''

FRAGMENTOS_T07 = '''ORDEN DE INTERVENCIÓN
  1. Brea

VEREDICTO DEL ÁRBITRO
  accion: intento de soborno a guardia
  tirada: Persuasión, resultado 12 vs CD 20 (hostil +5 por la naturaleza del acto)
  resultado: FALLO
  consecuencia: la oferta queda registrada por el PNJ como agravio

LÍNEA DEL ACTOR — va TEXTUAL, sin parafrasear
  "Guarda eso, muchacho. Guárdalo antes de que lo vea alguien y tenga que hacer algo al respecto."

  entrega: no sube la voz — por eso mismo es peor. Baja la vista a la mano
           de Kael y la deja ahí un segundo largo antes de hablar. Al
           terminar da media vuelta y sigue su ronda sin mirar atrás.
  se_niega_a: mencionar que tiene la orden de desalojo sin ejecutar

BOCETO DEL MUNDO
  lugar: Vado de Ceniza, cabecera del puente de piedra
  detalle: media mañana, tránsito de carros, olor a río y brea
  nota: el Gremio cobra el paso por cabeza y por bestia; hay guardia propia cerca'''

CITA_ESPERADA = "Guarda eso, muchacho. Guárdalo antes de que lo vea alguien y tenga que hacer algo al respecto."

PROMPT_NARRADOR = '''Escribes lo que el jugador lee. Eres el ÚNICO que produce prosa.

Recibes fragmentos de otros roles. No los pegues: escribe un texto continuo
que los contenga. Nadie debe poder señalar dónde termina uno y empieza otro.

FRAGMENTOS QUE RECIBES
  veredicto del árbitro    → tradúcelo a consecuencia narrada. Si dijo
                             fallo, no narres éxito bajo ninguna forma.
  linea + entrega del actor → la línea va TEXTUAL entre comillas, sin
                             parafrasear ni una palabra. Tú escribes lo que
                             la rodea: el gesto, la pausa, hacia dónde mira.
  boceto del mundo         → intégralo como descripción, no como lista.
  orden de intervención    → respétalo. Esto se lee como un libro: hay una
                             secuencia.

REGLA DE ORO
  Careces de autoridad para narrar al personaje jugador. Nunca describas sus
  acciones, diálogo, pensamientos o emociones. Tras describir la reacción del
  entorno o los PNJ, detente.

CÓMO ESCRIBES
  Máximo 2 párrafos. Prosa sensorial. Entorno y reacciones.
  Sin relleno conversacional ni meta-comentarios sobre tus reglas.
  Tono del mundo: mixto. Registro del jugador: mixto. Contraste permitido.

SALIDA
  Solo la narrativa. Sin encabezados, sin HUD, sin explicaciones.'''

# ---------------------------------------------------------------- 1B insumos
# Mismo evento, dos PNJ opuestos. A = el modelo juzga. B = la tabla decide.

FICHA_BREA = '''Sargento Brea, enana, guardia del puente. No pertenece al Gremio.
Cuarenta y tantos, cicatriz que le cruza la ceja, cota limpia aunque remendada.
Rasgos: directa, incómodamente honesta, leal a la gente antes que al cargo.
Contradicción interna: su deber es cumplir las órdenes del Gremio y sabe que
el Gremio está podrido. No se ha ido porque irse sería dejar el puesto a
alguien peor.
Voz: frases cortas. Dice lo que piensa antes de calcular si conviene. Si algo
le parece mal lo dice en el momento y delante de quien sea. Usa "muchacho" y
"muchacha" con todo el mundo.
Ideal: la palabra dada vale más que el contrato firmado.
Defecto: rígida, no miente ni cuando mentir salvaría a alguien.
Carácter: de principios.  Temple: audaz.
Disposición actual hacia el grupo: cordial.'''

FICHA_ORDULF = '''Ordulf Bec, humano, recaudador del peaje, tercera generación.
Sesenta años, manos manchadas de tinta, anillo del Gremio demasiado apretado.
Rasgos: meticuloso, rencoroso, servil hacia arriba.
Contradicción interna: ansía que lo traten como a un señor y solo sabe
conseguir que lo traten como a un cobrador.
Voz: formalidad excesiva con todo el mundo. Dice "vuestra merced" incluso al
insultar. Menciona agravios viejos como si fueran cortesías. Nunca alza la
voz. Nunca dice "no" directamente: dice "sería irregular".
Ideal: el que paga pasa, el que no paga no pasa. Eso es todo el orden que hay.
Defecto: no olvida un desaire de estatus, los anota mentalmente con fecha.
Carácter: suspicaz.  Temple: corriente.
Disposición actual hacia el grupo: fría.'''

ACTOR_BASE = '''Eres este personaje. No lo describes desde fuera: lo eres.

Recibes su ficha. NO recibes estado del mundo que él no conozca — si no está
en tu ficha, tu personaje no lo sabe. No lo deduzcas.

Careces de autoridad para narrar al personaje jugador: no describas sus
acciones, palabras ni emociones.

Las líneas rojas y velos sobrescriben todo. Sin relleno conversacional.

SALIDA — JSON exacto, nada más:
{"linea": "tu diálogo textual", "entrega": "tono y gesto", "se_niega_a": "qué no revelas"}'''

ACTOR_REGLAS_A = '''
TU REACCIÓN
  La magnitud de lo que te hacen depende de quién eres, no de la gravedad
  aparente del acto:
    Si eres de principios y te ofrecen un soborno, la oferta ES la ofensa.
    Te ofendes aunque el grupo sea aliado: te acaban de decir quién creen
    que eres. Rechazas sin negociar y lo recuerdas.
    Si eres suspicaz o sin escrúpulos, no te ofendes. Si rechazas es por
    insuficiente, no por indigno: contraofertas o insinúas el precio correcto.
    Si eres audaz y te amenazan, no te amilanas: sube tu respeto por
    atreverse, baja tu aprecio.
    Si eres temeroso, cedes y temes; ese miedo contamina la relación.
    Si tocan lo que amas, vale igual sea quien seas.
  Tu techo de confianza no lo superas nunca, por mucho que se lo ganen.
  Si eres de principios y te traicionan con pruebas, ese techo queda fijado
  para siempre: puedes volver a tratarlos con corrección, nunca a confiar.
  La confianza cae más rápido de lo que sube.
  Tus secretos se revelan solo bajo su condición declarada.'''

# Salidas reales de resolve_event() contra la base de fixtures.
OUTCOME_BREA = "La oferta ES la ofensa. Se ofende aunque el grupo sea aliado: le acaban de decir quién creen que es. Rechaza sin negociar y lo recuerda."
OUTCOME_ORDULF = "NO se ofende. Si rechaza es por insuficiente, no por indigno. Contraoferta o insinúa el precio correcto."

TURNO_SOBORNO = '''Kael: "Dos coronas y usted no vio a nadie cruzar anoche."
Kael: Le ofrece las monedas con la palma abierta.'''


def llamar(key, modelo, system, user, max_tokens=600, temp=0.7):
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps({
            "model": modelo,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temp,
            "max_tokens": max_tokens,
        }).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        sys.exit(1)
    return {
        "texto": d["choices"][0]["message"]["content"],
        "tokens_in": d.get("usage", {}).get("prompt_tokens"),
        "tokens_out": d.get("usage", {}).get("completion_tokens"),
        "ms": round((time.time() - t0) * 1000),
    }


def revisar_1a(texto):
    """Comprobaciones deterministas. El juicio de 'párrafo vs collage' es tuyo."""
    checks = {}
    checks["cita_literal"] = CITA_ESPERADA in texto
    # Fuzzy: ¿está la cita aunque con comillas distintas?
    nucleo = "Guarda eso, muchacho"
    checks["cita_aproximada"] = nucleo in texto
    # ¿Narró éxito habiendo fallo?
    exito = re.search(r"\b(acepta|toma las monedas|guarda las monedas|convence|accede)\b",
                      texto, re.I)
    checks["no_contradijo_veredicto"] = exito is None
    # ¿Narró al PJ? Busca a Kael como sujeto de acción o emoción.
    pj = re.search(r"\bKael\s+(siente|piensa|decide|comprende|se da cuenta|asiente|guarda|retira|baja)",
                   texto, re.I)
    checks["no_narro_al_pj"] = pj is None
    checks["parrafos"] = len([p for p in texto.split("\n\n") if p.strip()])
    checks["dentro_de_2_parrafos"] = checks["parrafos"] <= 2
    return checks


def revisar_1b(texto, esperado_ofendido):
    """¿La reacción va en la dirección correcta según la personalidad?"""
    try:
        limpio = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
        obj = json.loads(limpio)
        linea = obj.get("linea", "")
        parseable = True
    except Exception:
        linea = texto
        parseable = False

    ofensa = re.search(r"\b(insult|ofend|verg[üu]enza|indign|c[oó]mo se atreve|qui[eé]n te crees|guarda eso|no me compr)",
                       linea, re.I)
    regateo = re.search(r"\b(poco|m[aá]s|insuficiente|cuatro|cinco|diez|el doble|precio|tarifa|irregular)",
                        linea, re.I)
    return {
        "json_parseable": parseable,
        "linea": linea[:200],
        "senal_ofensa": bool(ofensa),
        "senal_regateo": bool(regateo),
        "direccion_correcta": bool(ofensa) if esperado_ofendido else bool(regateo),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--solo", choices=["1a", "1b"], default=None)
    ap.add_argument("--repeticiones", type=int, default=2)
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        print("Falta DEEPINFRA_API_KEY", file=sys.stderr)
        sys.exit(1)

    salida = {"modelo": args.modelo, "fecha": datetime.now().isoformat(), "pruebas": []}

    # ---------------------------------------------------------------- 1A
    if args.solo in (None, "1a"):
        print("\n" + "=" * 70)
        print("1A · COMPOSICIÓN — ¿párrafo o collage?")
        print("=" * 70)
        user = f"BUFFER DEL JUGADOR\n{BUFFER_T07}\n\n{FRAGMENTOS_T07}"
        for i in range(args.repeticiones):
            r = llamar(key, args.modelo, PROMPT_NARRADOR, user)
            c = revisar_1a(r["texto"])
            print(f"\n--- intento {i+1} · {r['ms']} ms · "
                  f"{r['tokens_in']}→{r['tokens_out']} tokens ---")
            print(r["texto"])
            print(f"\n  cita literal        {'SÍ' if c['cita_literal'] else 'NO'}"
                  f"{'' if c['cita_literal'] else '  (aproximada: ' + ('sí' if c['cita_aproximada'] else 'no') + ')'}")
            print(f"  no contradijo       {'SÍ' if c['no_contradijo_veredicto'] else 'NO ← narró éxito con fallo'}")
            print(f"  no narró al PJ      {'SÍ' if c['no_narro_al_pj'] else 'NO ← violó la regla de oro'}")
            print(f"  párrafos            {c['parrafos']}")
            salida["pruebas"].append({"prueba": "1A", "intento": i + 1, **r, "checks": c})

    # ---------------------------------------------------------------- 1B
    if args.solo in (None, "1b"):
        print("\n" + "=" * 70)
        print("1B · ACTOR — prompt largo (A) vs outcome resuelto (B)")
        print("=" * 70)
        casos = [
            ("Brea  (de principios, debe OFENDERSE)", FICHA_BREA, OUTCOME_BREA, True),
            ("Ordulf (suspicaz, debe REGATEAR)", FICHA_ORDULF, OUTCOME_ORDULF, False),
        ]
        for nombre, ficha, outcome, ofend in casos:
            for variante in ("A", "B"):
                if variante == "A":
                    system = ACTOR_BASE + ACTOR_REGLAS_A
                    user = f"TU FICHA\n{ficha}\n\nTURNO\n{TURNO_SOBORNO}"
                else:
                    system = ACTOR_BASE
                    user = (f"TU FICHA\n{ficha}\n\nCÓMO REACCIONAS ANTE ESTO\n{outcome}\n\n"
                            f"TURNO\n{TURNO_SOBORNO}")
                r = llamar(key, args.modelo, system, user, max_tokens=300)
                c = revisar_1b(r["texto"], ofend)
                print(f"\n--- {nombre} · variante {variante} · {r['ms']} ms · "
                      f"{r['tokens_in']}→{r['tokens_out']} ---")
                print(f'  «{c["linea"]}»')
                print(f"  json ok             {'SÍ' if c['json_parseable'] else 'NO'}")
                print(f"  dirección correcta  {'SÍ' if c['direccion_correcta'] else 'NO ←'}")
                salida["pruebas"].append({"prueba": f"1B-{variante}", "caso": nombre,
                                          **r, "checks": c})

    destino = f"sondeo1_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(salida, f, indent=2, ensure_ascii=False)

    tin = sum(p.get("tokens_in") or 0 for p in salida["pruebas"])
    tout = sum(p.get("tokens_out") or 0 for p in salida["pruebas"])
    print(f"\n{'=' * 70}")
    print(f"Salidas en {destino}")
    print(f"Consumo: {tin} in + {tout} out ≈ ${(tin*0.09 + tout*0.34)/1_000_000:.4f}")
    print("\nLo automático está arriba. Lo que decide 1A lo juzgas tú leyendo:")
    print("  ¿se lee como un párrafo escrito por una persona, o se nota")
    print("  dónde termina el veredicto y empieza el diálogo?")


if __name__ == "__main__":
    main()
