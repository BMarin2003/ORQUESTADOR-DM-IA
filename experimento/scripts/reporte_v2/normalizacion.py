"""
Normalización del formato de G1 para comparar G1 vs G2 con los instrumentos numéricos.

Motivo (docs/reportes/sensibilidad_baseline.md): G1 escribe cada turno con las etiquetas
«narrativa / mecanica / presion» en líneas solas y una línea de tirada («Percepción: Éxito
(10 vs CD 10)»); G2 nunca. Ese formato mueve TTR, n-gramas, Fernández-Huerta, Jaccard, el grafo
de entidades y `cr2_nombres_no_reconocidos`, así que la comparación G1 vs G2 sobre el texto crudo
mezcla estilo con formato.

`prosa()` de experimento/scripts/validacion_generar.py (hecha para el material ciego) quita las etiquetas y el
bloque «mecanica», pero solo reconoce las etiquetas en minúscula y sin adorno. Medido sobre
turnos reales deja residuos (etiquetas en negrita `**narrativa**`, «Mecanica»/«Mecánica»
capitalizadas, JSON crudo). `normalizar_turno` es más estricto; NO reemplaza a `prosa` (no se edita).

Reglas (solo G1; G2 y el lore [turno 0] quedan idénticos salvo `.strip()`):
  1. JSON crudo con clave «narrativa» -> narrativa + presion (sin mecanica).
  2. Etiquetas de línea sola (sin distinguir mayúsculas ni acento; con o sin `**`, `__`, `#`, `:`)
     -> se conservan los tramos narrativa y presion (a este último se le llama «presion» en
     G1: es prosa que el DM escribe al jugador, igual que en `prosa()`) y se descarta «mecanica».
     El texto que preceda a la primera etiqueta se conserva.
  3. Cualquier línea de tirada suelta que sobreviva (Habilidad: Éxito/Fallo/Pifia + «N vs CD M»,
     «N/M» o «CD M») se elimina.

Uso como script (mide los residuos y escribe datos/datos_v2/residuos_formato.json):
    PYTHONUTF8=1 py experimento/scripts/reporte_v2/normalizacion.py [--n 3000] [--semilla 20260920]
"""
import argparse
import collections
import json
import random
import re
import sys
import time
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
for _p in (AQUI, RAIZ / "experimento" / "scripts", RAIZ / "experimento" / "scripts" / "sensibilidad", RAIZ / "motor" / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Etiqueta de línea sola: narrativa|mecanica|presion, con acento/mayúscula/negrita/almohadilla/dos puntos.
_ETIQ = re.compile(
    r"^[ \t]*(?:[#>]+[ \t]*)?(?:\*\*|__|\*|_)?[ \t]*(narrativa|mec[aá]nica|presi[oó]n)"
    r"[ \t]*:?[ \t]*(?:\*\*|__|\*|_)?[ \t]*:?[ \t]*$", re.M | re.I)
_RE_PREFIJO_HABILIDAD = re.compile(r"^[ \t]*[A-ZÁÉÍÓÚÑ][^\n:]{1,40}:[ \t]*")
_RE_RESULTADO = re.compile(r"\b(?:[ÉE]xito|Fallo|Pifia|Acierto|Cr[ií]tico)\b", re.I)
_RE_NUM_TIRADA = re.compile(r"\d+\s*(?:vs\.?\s*(?:CD\s*)?\d+|/\s*\d+)|\bCD\s*\d+", re.I)
# «Habilidad: Éxito/Fallo (N vs CD M)» en su forma canónica.
_RE_PATRON_HABILIDAD = re.compile(
    r"[A-ZÁÉÍÓÚÑ][^\n:]{1,30}:\s*(?:Éxito|Exito|Fallo|Pifia)[^\n(]{0,15}\(\s*\d+\s*vs\.?\s*CD\s*\d+\s*\)")
_RE_ENCABEZADO = re.compile(r"^[ \t]*#{1,6}[ \t]+\S", re.M)

CATEGORIAS = ("etiquetas", "linea_tirada", "encabezados", "patron_habilidad", "json_crudo")


def _sin_acento(s):
    """Quita los diacríticos de `s` (NFD sin marcas Mn)."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _es_linea_tirada(linea):
    """True si la línea tiene forma «Habilidad: Éxito/Fallo/Pifia … N vs CD M», es decir, una línea de tirada de G1."""
    m = _RE_PREFIJO_HABILIDAD.match(linea)
    if not m:
        return False
    resto = linea[m.end():]
    return bool(_RE_RESULTADO.search(resto) and _RE_NUM_TIRADA.search(resto))


def _quitar_lineas_de_tirada(texto):
    """Elimina las líneas de tirada; si no hay ninguna devuelve el texto intacto (sin tocar el espaciado)."""
    lineas = texto.split("\n")
    quedan = [ln for ln in lineas if not _es_linea_tirada(ln)]
    if len(quedan) == len(lineas):
        return texto                                 # nada que quitar: no se toca ni el espaciado
    return re.sub(r"\n{3,}", "\n\n", "\n".join(quedan)).strip()


def _desde_json(dm):
    """Turnos en los que el modelo devolvió el JSON crudo {"narrativa","mecanica","presion"}."""
    if not dm.startswith("{"):
        return None
    try:
        obj = json.loads(dm, strict=False)
    except ValueError:
        return None
    if not isinstance(obj, dict) or "narrativa" not in obj:
        return None
    tramos = [str(obj.get(k) or "").strip() for k in ("narrativa", "presion")]
    return "\n\n".join(t for t in tramos if t)


def normalizar_turno(dm, brazo):
    """Texto del turno sin el formato de G1 (etiquetas, bloque de mecánica, líneas de tirada).
    G2 (y cualquier brazo distinto de «G1») queda idéntico salvo `.strip()`."""
    dm = (dm or "").strip()
    if brazo != "G1":
        return dm
    js = _desde_json(dm)
    if js is not None:
        return _quitar_lineas_de_tirada(js)
    partes = _ETIQ.split(dm)                          # [previo, etiqueta1, cuerpo1, etiqueta2, cuerpo2, ...]
    if len(partes) > 1:
        tramos = [partes[0].strip()]
        for etiqueta, cuerpo in zip(partes[1::2], partes[2::2]):
            if _sin_acento(etiqueta).lower() != "mecanica":
                tramos.append(cuerpo.strip())
        dm = "\n\n".join(t for t in tramos if t)
    return _quitar_lineas_de_tirada(dm)


def detectar_residuos(texto):
    """Qué restos de formato G1 quedan en `texto` (booleanos por categoría)."""
    texto = texto or ""
    return {
        "etiquetas": bool(_ETIQ.search(texto)),
        "linea_tirada": any(_es_linea_tirada(ln) for ln in texto.split("\n")),
        "encabezados": bool(_RE_ENCABEZADO.search(texto)),
        "patron_habilidad": bool(_RE_PATRON_HABILIDAD.search(texto)),
        "json_crudo": texto.lstrip().startswith("{") and '"narrativa"' in texto,
    }


def medir_residuos(textos, transformar):
    """Fracción de turnos que conservan cada categoría de residuo tras `transformar(texto)`."""
    cuenta = collections.Counter()
    n = con_algun = 0
    for t in textos:
        r = detectar_residuos(transformar(t))
        n += 1
        con_algun += any(r.values())
        for k, v in r.items():
            cuenta[k] += v
    out = {"n": n, "con_algun_residuo": con_algun,
           "fraccion_con_algun_residuo": con_algun / n if n else 0.0}
    out.update({k: cuenta[k] for k in CATEGORIAS})
    out["fraccion"] = {k: (cuenta[k] / n if n else 0.0) for k in CATEGORIAS}
    return out


def residuos_por_par(filas, transformar):
    """{par: nº de turnos con algún residuo tras `transformar`} para filas (par, texto)."""
    cuenta = collections.Counter()
    for par, texto in filas:
        if any(detectar_residuos(transformar(texto)).values()):
            cuenta[par] += 1
    return dict(cuenta)


_RE_RAYA = re.compile(r"^[ \t]*—", re.M)
_RE_COMILLAS = re.compile(r'"[^"\n]{5,}"')


def tipografia_dialogo(textos):
    """Fracción de turnos con diálogo a la española (línea que empieza por raya «—») y con
    comillas rectas: diferencia tipográfica que NO se normaliza (se reporta)."""
    textos = list(textos)
    n = len(textos)
    return {"n": n,
            "raya": sum(bool(_RE_RAYA.search(t)) for t in textos) / n if n else 0.0,
            "comillas": sum(bool(_RE_COMILLAS.search(t)) for t in textos) / n if n else 0.0}


def muestrear_turnos(conn, brazo, n=3000, semilla=20260920, primero=2, ultimo=1400):
    """Muestra aleatoria reproducible de `n` turnos (par, turno) de las campañas de `brazo` en los
    21 pares de Par07-27. Devuelve [{par, campaign_id, turn_id, dm_output}] ordenado."""
    import datos
    pares = datos.cargar_pares()
    clave = "campaign_g1" if brazo == "G1" else "campaign_g2"
    cands = [(p["par"], p[clave], t) for p in pares for t in range(primero, ultimo + 1)]
    elegidos = random.Random(semilla).sample(cands, n)
    por_camp = collections.defaultdict(list)
    for par, cid, t in elegidos:
        por_camp[(par, cid)].append(t)
    out = []
    for (par, cid), ts in por_camp.items():
        for r in conn.execute("SELECT turn_id, dm_output FROM turn_log WHERE campaign_id=%s AND turn_id = ANY(%s)",
                              (cid, ts)).fetchall():
            out.append({"par": par, "campaign_id": str(cid), "turn_id": r["turn_id"],
                        "dm_output": r["dm_output"] or ""})
    out.sort(key=lambda m: (m["par"], m["turn_id"]))
    return out


def _poblacion(conn, brazo):
    """[(par, dm_output)] de los turnos 2-1400 de todas las campañas del brazo."""
    import datos
    clave = "campaign_g1" if brazo == "G1" else "campaign_g2"
    filas = []
    for p in datos.cargar_pares():
        filas += [(p["par"], r["dm_output"] or "") for r in conn.execute(
            "SELECT dm_output FROM turn_log WHERE campaign_id=%s AND turn_id BETWEEN 2 AND 1400",
            (p[clave],)).fetchall()]
    return filas


def main():
    """Mide los residuos de formato G1 que dejan `prosa()` y `normalizar_turno` y escribe `datos/datos_v2/residuos_formato.json`.

    Usa una muestra reproducible de turnos por brazo (`--n`, `--semilla`) y la población completa de G1; también
    reporta la tipografía del diálogo (raya vs. comillas), que no se normaliza.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--semilla", type=int, default=20260920)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from validacion_generar import prosa
    import datos
    t0 = time.time()
    res = {"semilla": args.semilla, "n_muestra": args.n}
    with datos.abrir_conexion() as conn:
        g1 = [m["dm_output"] for m in muestrear_turnos(conn, "G1", args.n, args.semilla)]
        g2 = [m["dm_output"] for m in muestrear_turnos(conn, "G2", args.n, args.semilla)]
        fil_g1 = _poblacion(conn, "G1")
        pob_g1 = [t for _, t in fil_g1]
        pob_g2 = [t for _, t in _poblacion(conn, "G2")]
    variantes = {"crudo": lambda x: (x or "").strip(),
                 "prosa (validacion_generar)": lambda x: prosa(x, "G1"),
                 "normalizar_turno": lambda x: normalizar_turno(x, "G1")}
    res["muestra_g1"] = {k: medir_residuos(g1, f) for k, f in variantes.items()}
    res["muestra_g2_crudo"] = medir_residuos(g2, lambda x: (x or "").strip())
    res["poblacion_g1"] = {"n": len(pob_g1),
                           **{k: medir_residuos(pob_g1, f) for k, f in variantes.items() if k != "crudo"}}
    res["residuos_prosa_por_par"] = dict(sorted(residuos_por_par(fil_g1, lambda x: prosa(x, "G1")).items()))
    res["tipografia_dialogo"] = {"G1_normalizado": tipografia_dialogo(normalizar_turno(x, "G1") for x in pob_g1),
                                 "G2": tipografia_dialogo(x.strip() for x in pob_g2)}
    res["g2_identidad_en_muestra"] = all(normalizar_turno(x, "G2") == (x or "").strip() for x in g2)
    res["g1_difiere_de_prosa_muestra"] = sum(normalizar_turno(x, "G1") != prosa(x, "G1") for x in g1)
    res["g1_difiere_de_prosa_poblacion"] = sum(normalizar_turno(x, "G1") != prosa(x, "G1") for x in pob_g1)
    res["segundos"] = round(time.time() - t0, 1)
    destino = RAIZ / "datos" / "datos_v2"
    destino.mkdir(exist_ok=True)
    (destino / "residuos_formato.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    cab = f"{'variante':30}{'n':>7}{'algún residuo':>15}" + "".join(f"{c[:11]:>13}" for c in CATEGORIAS)
    for titulo, bloque in (("MUESTRA G1", res["muestra_g1"]), ("POBLACIÓN G1", res["poblacion_g1"])):
        print(f"\n{titulo}\n{cab}")
        for k, m in bloque.items():
            if k == "n":
                continue
            print(f"{k:30}{m['n']:>7}{m['con_algun_residuo']:>8} ({m['fraccion_con_algun_residuo']:>5.2%})"
                  + "".join(f"{m[c]:>13}" for c in CATEGORIAS))
    m = res["muestra_g2_crudo"]
    print(f"\nG2 crudo (muestra {m['n']}): con algún residuo {m['con_algun_residuo']}; "
          f"identidad de normalizar_turno = {res['g2_identidad_en_muestra']}")
    print("residuos que deja prosa() por par:", res["residuos_prosa_por_par"])
    print("tipografía del diálogo (población):", res["tipografia_dialogo"])
    print(f"G1: normalizar_turno difiere de prosa en {res['g1_difiere_de_prosa_muestra']} de la muestra "
          f"y {res['g1_difiere_de_prosa_poblacion']} de la población; {res['segundos']} s")


if __name__ == "__main__":
    main()
