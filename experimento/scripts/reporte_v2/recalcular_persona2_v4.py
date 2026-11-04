"""
persona2 v4.1: regla de conteo con contexto D&D 5e (criterio de AUTORÍA) sobre el detector congelado
(persona2.py y léxico SIN cambios; se verifica el hash). Especificación y justificación:
datos/validacion_v2/persona2_v4_reglas_dnd.md y persona2_analisis_constructo_2026-11-04.md.
Diseñada SOLO con la partición de desarrollo (semilla 20261105) y con un volcado que excluye la partición de prueba.

Definición positiva (QN-2a, usurpación): el narrador atribuye al PJ, sin que el jugador lo declarara,
  (a) una DECISIÓN nueva (VOLICION), (b) PALABRAS nuevas (HABLA) o (c) una POSTURA que orienta decisiones futuras
  (COGNICION actitudinal; EMOCION hacia agentes). Todo lo demás es resultado de la acción (paso 3 del ciclo de juego).

Un hallazgo primario NO cuenta si (código = motivo):
  R1  el jugador lo declaró en su acción.
  R7  está en una línea de diálogo que abre con raya (voz de un PNJ).
  R8  EMOCION cuyo sujeto es la mirada o el cuerpo de un PNJ («sus ojos / una mirada ... te recorre»).
  R9  está en una subordinada «que...» regida por un verbo de saber/creer/decir en 3.ª persona (perspectiva de PNJ).
  R10 VOLICION de esfuerzo o inicio (esforzarse, obligarse, disponerse, empeñarse): ejecución de lo declarado.
  R11 VOLICION retrospectiva (has decidido, decidiste, has elegido...): recuerda una decisión ya tomada.
  R12 VOLICION abierta: el narrador ofrece la decisión («a ver qué decides», «o aceptas... o...»).
  R6  VOLICION de aceptación con marcador de acuerdo en el diálogo del jugador («tienes razón», «acepto»...).
  RC  d20 = 1 o 20 y la categoría es COGNICION o EMOCION (crítico y pifia son absolutos; regla de mesa).
  R2  COGNICION informativa con tirada: resultado de la prueba. La actitudinal (dudar, confiar, arrepentirse...)
      cuenta (R3).
  EV  EMOCION que no es una actitud hacia un agente: emoción del resultado o del evento (frustración, alivio,
      miedo, sorpresa...), estado físico o sensación. Tipología de Ortony, Clore & Collins (1988).
QN-2b (focalización interna): turno con algún hallazgo excluido por R2, RC o EV, es decir, con un resultado narrado
desde la mente del PJ. Es descriptivo; no es usurpación.

Uso:
    PYTHONUTF8=1 py experimento/scripts/reporte_v2/recalcular_persona2_v4.py --dev
    PYTHONUTF8=1 py experimento/scripts/reporte_v2/recalcular_persona2_v4.py --corpus
"""
import argparse
import collections
import csv
import json
import re
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import recalcular_persona2 as R                # noqa: E402

VERSION = "v4.1"
DESTINO = R.RAIZ / "datos" / "datos_v2" / "persona2_v4"
DESTINO_FOCAL = R.RAIZ / "datos" / "datos_v2" / "focalizacion_v4"
VAL = R.RAIZ / "datos" / "validacion_v2"
_pl = R.P._plano

ACTITUDINAL = {"dudar", "confiar", "desconfiar", "arrepentir", "arrepentirse", "resignarse", "renegar",
               "perder la fe", "cambiar de opinion"}
ACEPTAR = {"aceptar", "acceder", "aprobar", "consentir", "asentir", "ceder", "conformarse"}
ESFUERZO = {"esforzar", "esforzarse", "obligar", "obligarse", "disponer", "disponerse", "empenar", "empenarse",
            "afanar", "afanarse", "forzar", "forzarse"}
ACUERDO = re.compile(r"\b(tienes razon|teneis razon|de acuerdo|esta bien|acepto|aceptamos|vale|trato hecho|como digas|"
                     r"me parece bien|entendido|lo hare|cuenta conmigo|hecho)\b")
SUJ_PNJ = re.compile(r"^\s*(sus|su|una|la)\s+(ojos|mirada|manos|dedos|pupilas|labios)\b")
PERSP_PNJ = re.compile(r"\b(saben?|comprenden?|comprender|entienden?|entender|creen?|piensan?|dicen?|asumen?|suponen?|"
                       r"intuyen?|notan?|ven|convencid[oa]s?|segur[oa]s?)\b(?:\s+\w+){0,3}?\s+(de\s+)?que\b[^.;:!?]*$")
RETRO = re.compile(r"\b(has|habias|hubiste)\s+\w*$")
RETRO_FORMA = re.compile(r"(iste|aste)$")
ABIERTA = re.compile(r"(\ba ver\b|\baguard\w*|\besper\w*)[^.;:!?]*$|\b(si|o)\s+(tu\s+)?$")
ACTITUD_EMO = re.compile(r"\b(amor|carino|ternura|afecto|odio|odias|rencor|resentimiento|desprecio|desprecias|gratitud|"
                         r"agradecimiento|admiracion|compasion|lastima|culpa|culpable|remordimiento|lealtad|devocion|celos|"
                         r"envidia|desconfianza|respeto|detestas|amas|admiras)\b")
RAYAS = (chr(0x2014), chr(0x2013), chr(0x2015))
FOCAL = {"R2", "RC", "EV"}


def _linea(dm, i):
    a = dm.rfind("\n", 0, i) + 1
    b = dm.find("\n", i)
    return dm[a:b if b >= 0 else len(dm)]


def _oracion_hasta(dm, i):
    a = max(dm.rfind(c, 0, i) for c in ".!?\n") + 1
    return dm[a:i]


def motivo_exclusion(h, dm, accion, tiradas):
    """None si el hallazgo cuenta como usurpación (QN-2a); si no, el código de la regla que lo excluye."""
    cat = h["categoria"]
    lema = _pl(h.get("verbo_lema") or "")
    pre = _pl(_oracion_hasta(dm, h["inicio"]))
    disparo = _pl(dm[h["inicio"]:h["fin"]]).split()
    if h["declarada"]:
        return "R1"
    if _linea(dm, h["inicio"]).lstrip().startswith(RAYAS):
        return "R7"
    if cat == "EMOCION" and SUJ_PNJ.match(pre):
        return "R8"
    if PERSP_PNJ.search(pre):
        return "R9"
    if cat == "VOLICION":
        if lema in ESFUERZO:
            return "R10"
        if RETRO.search(pre) or (disparo and RETRO_FORMA.search(disparo[-1])):
            return "R11"
        if ABIERTA.search(pre):
            return "R12"
        if lema in ACEPTAR and ACUERDO.search(_pl(accion or "")):
            return "R6"
        return None
    if cat == "HABLA":
        return None
    if any(t["dado"] in (1, 20) for t in tiradas):
        return "RC"
    if cat == "COGNICION":
        hay_tirada = bool(tiradas) or h["tirada_declarada"]
        return "R2" if hay_tirada and lema not in ACTITUDINAL else None
    if cat == "EMOCION":
        return None if ACTITUD_EMO.search(_pl(dm[h["inicio"]:h["fin"] + 70])) else "EV"
    return None


def evaluar(dc, t, nombres):
    """(hallazgos primarios con su motivo, tiradas, acción) del turno t, o None si el turno no es válido."""
    f = dc.turnos.get(t)
    if not f or not R.turno_valido(f):
        return None
    buf = f["player_buffer"] or []
    pj = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
    dm, accion = R.normalizar_turno(f["dm_output"], dc.brazo), R.jugador(buf)
    tiradas = dc.tiradas(t)
    hs = [h for h in R.P.detectar_usurpacion(dm, accion, None, nombres.get(pj)) if h["categoria"] in R.PRIM]
    for h in hs:
        h["motivo"] = motivo_exclusion(h, dm, accion, tiradas)
    return hs, tiradas, accion


def _cuenta_v3b(h):
    return not h["declarada"] and not (h["tirada_declarada"] and h["categoria"] == "COGNICION")


def modo_dev():
    part = {r["id"]: r["conjunto"] for r in csv.DictReader(open(VAL / "particion_persona2.csv", encoding="utf-8-sig"))}
    clave = [r for r in csv.DictReader(open(VAL / "clave.csv", encoding="utf-8-sig"))
             if r["tipo"] == "persona2" and part.get(r["id"]) == "desarrollo"]
    pares, nombres = {p["par"]: p for p in R._pares.todos()}, R.cargar_nombres()
    motivos, cambios, n3, n4, nf = collections.Counter(), [], 0, 0, 0
    with R.datos.abrir_conexion() as conn:
        cache = {}
        for c in clave:
            k = (c["par"], c["brazo"])
            if k not in cache:
                p = pares[c["par"]]
                cache[k] = R.datos.DatosCampana(conn, p["campaign_g1" if c["brazo"] == "G1" else "campaign_g2"], c["brazo"], c["par"])
            r = evaluar(cache[k], int(c["turn_id"]), nombres)
            if r is None:
                continue
            hs = r[0]
            v3, v4 = any(_cuenta_v3b(h) for h in hs), any(h["motivo"] is None for h in hs)
            n3, n4, nf = n3 + v3, n4 + v4, nf + any(h["motivo"] in FOCAL for h in hs)
            for h in hs:
                motivos[(h["categoria"], h["motivo"] or "CUENTA")] += 1
            if v3 != v4 or v4:
                cambios.append((c["id"], c["brazo"], v3, v4,
                                [(h["categoria"], h["verbo_lema"], h["motivo"], h["evidencia"][:150]) for h in hs]))
    print(f"desarrollo {VERSION}: {len(clave)} ítems | usurpación v3b = {n3} | {VERSION} = {n4} | focalización = {nf}")
    for k, v in sorted(motivos.items()):
        print(f"  {v:3d}  {k}")
    print("\nCambios o positivos:")
    for x in cambios:
        print(" ", x)


def modo_corpus():
    R.congelado_ok()
    nombres, t0 = R.cargar_nombres(), time.time()
    DESTINO.mkdir(parents=True, exist_ok=True)
    DESTINO_FOCAL.mkdir(parents=True, exist_ok=True)
    resumen = collections.Counter()
    with R.datos.abrir_conexion() as conn:
        for p in R._pares.todos():
            for brazo in ("G1", "G2"):
                dc = R.datos.DatosCampana(conn, p["campaign_g1" if brazo == "G1" else "campaign_g2"], brazo, p["par"])
                filas, focal = [], []
                for t in range(1, 1401):
                    r = evaluar(dc, t, nombres)
                    if r is None:
                        continue
                    hs = r[0]
                    cats = {h["categoria"] for h in hs if h["motivo"] is None}
                    for h in hs:
                        resumen[(brazo, h["categoria"], h["motivo"] or "CUENTA")] += 1
                    fila = {"turn_id": t, "en_desarrollo": 0, "primaria": int(bool(cats)), "secundaria": "", "muerte": ""}
                    for c in R.PRIM:
                        fila[c] = int(c in cats)
                    filas.append(fila)
                    focal.append({"turn_id": t, "focal": int(any(h["motivo"] in FOCAL for h in hs))})
                nombre = f"par{p['par']}_{brazo}.csv"
                for ruta, campos, datos_ in ((DESTINO / nombre, R.COLUMNAS, filas),
                                             (DESTINO_FOCAL / nombre, ["turn_id", "focal"], focal)):
                    with open(ruta, "w", newline="", encoding="utf-8") as fh:
                        w = csv.DictWriter(fh, fieldnames=campos)
                        w.writeheader()
                        w.writerows(datos_)
                print(f"par{p['par']} {brazo}: usurpación {sum(f['primaria'] for f in filas)} | "
                      f"focal {sum(f['focal'] for f in focal)}", flush=True)
    (DESTINO / "_motivos.json").write_text(json.dumps({"|".join(k): v for k, v in sorted(resumen.items())},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dev", action="store_true")
    g.add_argument("--corpus", action="store_true")
    a = ap.parse_args()
    modo_dev() if a.dev else modo_corpus()
