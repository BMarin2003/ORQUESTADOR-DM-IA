r"""
Pruebas puras de orquestador/mundo.py -- sin DB, sin red. Mismo patrón
que probar_router.py y probar_arbitro.py.
"""
from mundo import resolver_mundo

def lugar(kind="building", detail="sketch", descripcion=None):
    """Ubicación mínima de prueba con los campos que lee `resolver_mundo`."""
    return {"id": "loc-1", "kind": kind, "detail": detail,
            "description_canonical": descripcion, "observed_at_turn": None}

CASOS = [
    (
        "lugar inexistente -> necesita boceto, no se fija",
        dict(lugar=None, eventos_reloj=[], semillas_candidatas=[]),
        dict(lugar_necesita_boceto=True, fijar_al_responder=False,
             lugar_repite=False, necesita_llm=True),
    ),
    (
        "lugar sketch sin pregunta -> boceto de trazo grueso, no se fija (MUN-4)",
        dict(lugar=lugar(detail="sketch"), eventos_reloj=[],
             semillas_candidatas=[], escena_pregunta=False),
        dict(lugar_necesita_boceto=True, fijar_al_responder=False,
             lugar_repite=False),
    ),
    (
        "lugar sketch CON pregunta concreta -> se detalla y se fija (MUN-5)",
        dict(lugar=lugar(detail="sketch"), eventos_reloj=[],
             semillas_candidatas=[], escena_pregunta=True),
        dict(lugar_necesita_boceto=True, fijar_al_responder=True,
             lugar_repite=False),
    ),
    (
        "lugar ya observado -> repite la misma descripción, cero LLM (MUN-6)",
        dict(lugar=lugar(detail="observed", descripcion="El puente cruje."),
             eventos_reloj=[], semillas_candidatas=[], escena_pregunta=True),
        dict(lugar_repite=True, descripcion="El puente cruje.",
             lugar_necesita_boceto=False, fijar_al_responder=False,
             necesita_llm=False),
    ),
    (
        "dungeon en sketch -> exige plan completo aunque no pregunten (MUN-7)",
        dict(lugar=lugar(kind="dungeon", detail="sketch"), eventos_reloj=[],
             semillas_candidatas=[], escena_pregunta=False),
        dict(lugar_necesita_boceto=True, fijar_al_responder=True),
    ),
    (
        "dungeon YA full -> ya no vuelve a exigir plan, repite como cualquier lugar fijo",
        dict(lugar=lugar(kind="dungeon", detail="full", descripcion="Cripta trazada."),
             eventos_reloj=[], semillas_candidatas=[], escena_pregunta=False),
        dict(lugar_repite=True, lugar_necesita_boceto=False,
             fijar_al_responder=False),
    ),
    (
        "reloj disparado pasa tal cual, sin que el LLM lo juzgue (MUN-1/2)",
        dict(lugar=lugar(detail="observed", descripcion="x"),
             eventos_reloj=[{"clock_id": "c1", "agenda": "asedio"}],
             semillas_candidatas=[], escena_pregunta=False),
        dict(eventos_reloj=[{"clock_id": "c1", "agenda": "asedio"}]),
    ),
    (
        "sin reloj disparado -> lista vacía, no None",
        dict(lugar=lugar(detail="observed", descripcion="x"),
             eventos_reloj=[], semillas_candidatas=[]),
        dict(eventos_reloj=[]),
    ),
    (
        "semilla candidata más antigua se expone (MUN-3)",
        dict(lugar=lugar(detail="observed", descripcion="x"), eventos_reloj=[],
             semillas_candidatas=[{"id": "s1", "kind": "hook", "content": "..."},
                                   {"id": "s2", "kind": "threat", "content": "..."}]),
        dict(semilla_candidata={"id": "s1", "kind": "hook", "content": "..."},
             necesita_llm=True),
    ),
    (
        "sin semillas -> None, y si el lugar está fijo, necesita_llm=False",
        dict(lugar=lugar(detail="observed", descripcion="x"), eventos_reloj=[],
             semillas_candidatas=[]),
        dict(semilla_candidata=None, necesita_llm=False),
    ),
]


def main():
    """Corre CASOS contra `resolver_mundo` (determinista, sin LLM); sale con código 1 si algún caso no coincide."""
    total = len(CASOS)
    ok = 0
    for i, (desc, args, esperado) in enumerate(CASOS, 1):
        real = resolver_mundo(**args)
        paso = all(real.get(k) == v for k, v in esperado.items())
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
