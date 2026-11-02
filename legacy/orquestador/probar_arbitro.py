r"""
Pruebas puras del Árbitro (sin DB, sin red) — mismo patrón que
orquestador/probar_router.py: cada caso es (descripción, args, esperado
parcial). Se corren con `python3 orquestador/probar_arbitro.py`.
"""
from arbitro import resolver_veredicto

CASOS = [
    (
        "tirada de éxito sin PNJ (banda neutra por defecto)",
        dict(buffer="Intento saltar el foso. (resultado: 17, dado: 1d20+3)",
             altera_estado=True, banda_disposicion=None),
        dict(necesita_juicio=False, veredicto="éxito", cd=15, resultado=17),
    ),
    (
        "tirada de fallo sin PNJ",
        dict(buffer="Intento saltar el foso. (resultado: 12, dado: 1d20+3)",
             altera_estado=True, banda_disposicion=None),
        dict(necesita_juicio=False, veredicto="fallo", cd=15, resultado=12),
    ),
    (
        "tirada exacta en el límite = éxito (>=, no >)",
        dict(buffer="(resultado: 15, dado: 1d20)",
             altera_estado=True, banda_disposicion="cold"),
        dict(necesita_juicio=False, veredicto="éxito", cd=15, resultado=15),
    ),
    (
        "PNJ hostil sube la CD a 20 (+5)",
        dict(buffer="Intento convencerlo. (resultado: 17, dado: 1d20+2)",
             altera_estado=True, banda_disposicion="hostile"),
        dict(necesita_juicio=False, veredicto="fallo", cd=20, resultado=17),
    ),
    (
        "PNJ wary (banda agrupada con hostile) también +5",
        dict(buffer="(resultado: 19, dado: 1d20)",
             altera_estado=True, banda_disposicion="wary"),
        dict(necesita_juicio=False, veredicto="fallo", cd=20, resultado=19),
    ),
    (
        "PNJ leal baja la CD a 10 (-5)",
        dict(buffer="(resultado: 11, dado: 1d20)",
             altera_estado=True, banda_disposicion="loyal"),
        dict(necesita_juicio=False, veredicto="éxito", cd=10, resultado=11),
    ),
    (
        "PNJ devoted (agrupado con loyal) también -5",
        dict(buffer="(resultado: 11, dado: 1d20)",
             altera_estado=True, banda_disposicion="devoted"),
        dict(necesita_juicio=False, veredicto="éxito", cd=10, resultado=11),
    ),
    (
        "bandas neutral y cordial no modifican (0)",
        dict(buffer="(resultado: 15, dado: 1d20)",
             altera_estado=True, banda_disposicion="cordial"),
        dict(necesita_juicio=False, veredicto="éxito", cd=15, resultado=15),
    ),
    (
        "sin tirada + altera_estado=True -> necesita juicio (NUN-5)",
        dict(buffer="Intento una idea que no estaba prevista, sin tirar dados.",
             altera_estado=True, banda_disposicion=None),
        dict(necesita_juicio=True),
    ),
    (
        "sin tirada + altera_estado=False -> None (no hay nada que resolver)",
        dict(buffer="Miro alrededor de la taberna.",
             altera_estado=False, banda_disposicion=None),
        None,
    ),
    (
        "recurso_consumido y correccion_al_jugador quedan None (ENT-4 diferido)",
        dict(buffer="(resultado: 20, dado: 1d20)",
             altera_estado=True, banda_disposicion=None),
        dict(recurso_consumido=None, correccion_al_jugador=None),
    ),
]


def main():
    """Corre CASOS contra `resolver_veredicto` (determinista, sin LLM); sale con código 1 si algún caso no coincide."""
    total = len(CASOS)
    ok = 0
    for i, (desc, args, esperado) in enumerate(CASOS, 1):
        real = resolver_veredicto(**args)
        if esperado is None:
            paso = real is None
        else:
            paso = real is not None and all(
                real.get(k) == v for k, v in esperado.items()
            )
        marca = "✓" if paso else "✗"
        if paso:
            ok += 1
        print(f"{marca} [{i}/{total}] {desc}")
        if not paso:
            print(f"    esperado⊇{esperado}\n    real={real}")
    print(f"\n{ok}/{total} pruebas pasaron")
    raise SystemExit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
