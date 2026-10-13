"""
DIAGNÓSTICO POSTERIOR (no pre-registrado) sobre Jericho recall y relojes reconocidos, complemento de correr_jericho_relojes.py.
Ese A2 comprueba la mecánica (100 % por construcción: se inserta o se quita el léxico exacto). Aquí se acota lo que sí importa para H1e: ¿el «reconocido» distingue un turno con
evento de uno cualquiera?
  1. NULO ALEATORIO (Jericho): cada delta real se evalúa con el mismo léxico pero movido a un turno al azar de la misma campaña (≥ 5 turnos del real), K veces. Recall real vs recall por azar.
  2. NULO ALEATORIO (relojes): cada reloj se evalúa con su mismo vocabulario en una ventana al azar (disparo simulado), K veces.
  3. PALABRAS FUNCIONALES en el vocabulario de los relojes (_texto_reloj incluye toda palabra de 4+ letras de la agenda, «antes», «para», «sobre»…): fracción de relojes reconocidos SOLO por
     palabras funcionales (con spaCy es stop words), y reconocimiento (real y por azar) si se quitan esas palabras del vocabulario.
Solo lectura; texto normalizado; semilla fija.   PYTHONUTF8=1 py experimento/scripts/sensibilidad/diagnostico_jericho_relojes.py
"""
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import correr_jericho_relojes as J   # noqa: E402  (mismas cargas y mismas funciones reales del instrumento)
from spacy.lang.es.stop_words import STOP_WORDS   # noqa: E402

RV, K, SEMILLA = J.RV, 20, 20260921
SALIDA = J.RAIZ / "docs" / "reportes" / "sensibilidad_jericho_relojes_diagnostico.md"


def _coincide(palabras, textos):
    """Misma regla que RV.relojes_no_reconocidos: palabra completa, sin distinguir mayúsculas, en cualquiera de los textos."""
    return any(re.search(r"\b" + re.escape(w) + r"\b", t, re.I) for w in palabras for t in textos)


def pct(a, b):
    """Formatea a/b como porcentaje; guion largo si b es 0."""
    return f"{100 * a / b:.1f} %" if b else "—"


def main():
    """Diagnóstico posterior (no pre-registrado): compara el recall real de Jericho y relojes con el que da el mismo léxico en turnos al azar.

    Estima además cuántos relojes se reconocen solo por palabras funcionales; escribe el informe en SALIDA.
    Comprueba antes que la función de coincidencia propia reproduce al instrumento real."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = random.Random(SEMILLA)
    pares = J._pares.todos()
    real = defaultdict(lambda: [0, 0])      # (familia, brazo) -> [reconocidos, evaluables]
    azar = defaultdict(lambda: [0, 0])
    rel_real, rel_azar, sin_func, azar_c = [0, 0], [0, 0], [0, 0], [0, 0]
    solo_func, claves, control = 0, Counter(), [0, 0]
    for p in pares:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            tpi, relojes, deltas = J._cargar_campana(p[k], brazo)
            turnos = sorted(tpi)
            for d in deltas:
                ok = J._real_jericho(d, tpi)
                if ok is None:
                    continue
                fam = f"{d['entity_type']}.{d['field_name']}"
                real[(fam, brazo)][0] += ok
                real[(fam, brazo)][1] += 1
                cand = [t for t in turnos if abs(t - d["turn_id"]) >= 5 and t + 1 in tpi]
                for _ in range(K):
                    azar[(fam, brazo)][0] += bool(J._real_jericho(dict(d, turn_id=rng.choice(cand)), tpi))
                    azar[(fam, brazo)][1] += 1
            if p["lote"] != "v2":                                                # los relojes solo existen en Par18-27
                continue
            for r in relojes:
                vocab = RV._texto_reloj(r)
                ok = J._real_reloj(r, tpi)
                textos = [tpi.get(t) or "" for t in range(r["fired_at_turn"] + 1, r["fired_at_turn"] + 3)]
                control[1] += 1
                control[0] += (_coincide(vocab, textos) == ok)                  # la función compartida reproduce al instrumento real con el vocabulario completo
                rel_real[0] += ok
                rel_real[1] += 1
                ventanas = [rng.choice([t for t in turnos if t + 2 in tpi and abs(t - r["fired_at_turn"]) >= 5]) for _ in range(K)]
                funcional = {w for w in vocab if w.lower() in STOP_WORDS}
                contenido = vocab - funcional                                   # incluye el nombre completo de la facción y las palabras de contenido de la agenda
                for t1 in ventanas:
                    tx = [tpi.get(t) or "" for t in range(t1 + 1, t1 + 3)]
                    rel_azar[0] += _coincide(vocab, tx)
                    rel_azar[1] += 1
                    azar_c[0] += _coincide(contenido, tx)
                    azar_c[1] += 1
                sin_func[0] += _coincide(contenido, textos)
                sin_func[1] += 1
                if ok and not _coincide(contenido, textos):
                    solo_func += 1
                if ok:
                    for w in vocab:
                        if _coincide({w}, textos):
                            claves[w.lower()] += 1
    assert control[0] == control[1], f"la función de coincidencia compartida no reproduce al instrumento real: {control}"
    L = ["# Diagnóstico posterior: Jericho recall y relojes (no pre-registrado)", "",
         "Complementa `sensibilidad_jericho_relojes.md` (A2 mecánico, 100 % por construcción). Texto normalizado, semilla 20260921, K = 20 réplicas al azar por evento.", "",
         "## 1. Jericho recall: recall real frente al recall que da el mismo léxico en un turno cualquiera", "",
         "| familia | brazo | eventos evaluables | recall real | recall por azar | diferencia |", "|---|---|---|---|---|---|"]
    for (fam, brazo) in sorted(real):
        a, n = real[(fam, brazo)]
        b, m = azar[(fam, brazo)]
        L.append(f"| {fam} | {brazo} | {n} | {pct(a, n)} | {pct(b, m)} | {100 * (a / n - b / m):+.1f} pp |")
    ta, tn = sum(v[0] for v in real.values()), sum(v[1] for v in real.values())
    tb, tm = sum(v[0] for v in azar.values()), sum(v[1] for v in azar.values())
    L += [f"| **todas** | ambos | {tn} | {pct(ta, tn)} | {pct(tb, tm)} | {100 * (ta / tn - tb / tm):+.1f} pp |", "",
          "## 2. Relojes reconocidos (Par18-27)", "",
          f"- Reconocidos de verdad: {rel_real[0]} de {rel_real[1]} ({pct(*rel_real)}). Por azar (mismo vocabulario, ventana de 2 turnos al azar): {pct(*rel_azar)}.",
          f"- Con solo palabras de contenido (sin las palabras funcionales del vocabulario): reconocidos {sin_func[0]} de {sin_func[1]} ({pct(*sin_func)}); por azar con ese vocabulario: {pct(*azar_c)}.",
          f"- Relojes reconocidos ÚNICAMENTE por palabras funcionales: {solo_func} de {rel_real[0]} reconocidos ({pct(solo_func, rel_real[0])}).",
          f"- Comprobación: la función de coincidencia de este script reproduce al instrumento real en {control[0]} de {control[1]} relojes.", "",
          "Claves que más reconocen relojes (una vez por reloj reconocido):", "", "| clave | relojes | palabra funcional |", "|---|---|---|"]
    L += [f"| {w} | {n} | {'sí' if w in STOP_WORDS else 'no'} |" for w, n in claves.most_common(12)]
    L += ["", "**Lectura.** Si el recall real no supera al del azar por un margen claro, el reconocimiento léxico no distingue un turno con evento de uno cualquiera y no sirve como medida de "
          "coherencia longitudinal; el A2 mecánico solo demuestra que el instrumento lee la ventana y responde al léxico, no que ese léxico signifique que el evento se narró.", ""]
    SALIDA.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
