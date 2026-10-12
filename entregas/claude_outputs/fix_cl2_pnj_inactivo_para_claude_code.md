# Parche pendiente para `orquestador/reporte_validacion.py` — aplicar cuando no estés escribiendo activamente ese archivo

Contexto: se encontró que `cl2_pnj_inactivo_actua` (chequeo en vivo de
`vertical_slice.py`/`vertical_slice_g1.py`) dispara con la sola presencia
LITERAL del nombre de un PNJ inactivo en la narración, sin distinguir si el
PNJ aparece como sujeto de una acción (error real de continuidad) o solo
referenciado/recordado (narrativamente legítimo). Como G1 sostiene
referencias a su elenco por más tiempo que G2 (ver Papalampidi C), esto
puede estar inflando el hallazgo de G1 sin que sea un error real.

**No toca `vertical_slice.py`/`vertical_slice_g1.py` ni el schema de
`turn_validation`** — es 100% aditivo en `reporte_validacion.py` (post-hoc),
así que se puede aplicar y correr retroactivamente sobre Par 01-06 sin
regenerar nada, y no interfiere con la generación en curso de Par 07-17.

## 1. Agregar antes de `# --------------------------------------------------------------------- main` (después de `imprimir_grafo_lema`)

```python
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
```

## 2. En `main()`, justo antes de `print(f"\n{'='*74}\n")` al final (después de la llamada a `imprimir_grafo_lema`)

```python
    imprimir_pnj_inactivo_refinado(
        pnj_inactivo_refinado(filas_validacion, turnos_por_id, camp.entidades()))
```

`filas_validacion` y `turnos_por_id` ya existen como variables en `main()` en ese punto — no hace falta declarar nada nuevo, solo reusar.

## Verificación ya hecha

El archivo completo con este parche ya se compiló sin errores (`python3 -m py_compile`) antes de proponerlo. Es seguro aplicarlo tal cual.

## Después de aplicarlo

Correr de nuevo `reporte_validacion.py` sobre las 6 campañas de Par 04/05/06
(o al menos Par 06 G1, el caso más extremo con 161 turnos marcados) para ver
qué proporción del hallazgo sobrevive la reclasificación. Ese resultado
decide si `cl2_pnj_inactivo_actua` se cita en la tesis como debilidad de G1
tal cual, o con el matiz de "X% de las menciones son acción real, Y% son
referencia retrospectiva".
