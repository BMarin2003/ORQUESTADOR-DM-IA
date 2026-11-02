"""
Recalcula, para las 42 campañas de Par07-27, los instrumentos que dependen SOLO de texto y contexto
sobre el texto NORMALIZADO (normalizacion.normalizar_turno), junto a los valores v1 que el motor
guardó en `turn_validation`. Un CSV por campaña en datos/datos_v2/ (par07_G1.csv, par07_G2.csv, ...).

Columnas: turn_id y, para cada instrumento, `<instr>_v1` (guardado en turn_validation) y
`<instr>_v2` (recalculado sobre texto normalizado). Excepción: `grammaticality_lt` no se guarda en
turn_validation; su v1 es LanguageTool sobre el texto crudo (recalculado aquí) y solo se calcula con
`--con-lt` en 1 de cada `--lt-cada` turnos (por defecto 10; LanguageTool es lento).

Se reutilizan (no se reimplementan) los envoltorios verificados de experimento/scripts/sensibilidad/
instrumentos_texto.py y la reconstrucción de contexto de experimento/scripts/sensibilidad/datos.py. Solo SELECT
(conexión de solo lectura); nada de LLM.

PRUEBA DE SANIDAD: en G2 la normalización es la identidad, así que v2 debe ser igual a v1. Al final
se compara y se escribe datos/datos_v2/sanidad_g2.json.

Reanudación: si el CSV de una campaña existe y está completo, se salta (con `--con-lt`, si existe sin
valores de LanguageTool, solo se completa esa parte). Escritura atómica (.tmp + rename).

    PYTHONUTF8=1 py experimento/scripts/reporte_v2/recalcular.py [--con-lt] [--lt-cada 10] [--pares 07,08] [--brazos G1,G2]
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent.parent
for _p in (AQUI, RAIZ / "experimento" / "scripts", RAIZ / "experimento" / "scripts" / "sensibilidad", RAIZ / "motor" / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                                   # noqa: E402  (experimento/scripts/sensibilidad/datos.py)
import instrumentos_texto as it                # noqa: E402  (experimento/scripts/sensibilidad/instrumentos_texto.py)
from normalizacion import normalizar_turno     # noqa: E402

DESTINO = RAIZ / "datos" / "datos_v2"

# instrumento -> decimales de comparación (0 = igualdad exacta)
INSTRUMENTOS = {
    "qn1_ttr": 3,
    "qn1_ngram_repeticion": 3,
    "qn1_legibilidad_fh": 2,
    "cl2_lugar_jaccard_similarity": 3,
    "cr2_entidad_grafo_densidad": 3,
    "cr2_n_nombres_no_reconocidos": 0,        # recuento de nombres no reconocidos
    "cr2_nombres_no_reconocidos": 0,          # bandera (0/1): ¿algún nombre no reconocido?
    "grammaticality_lt": 4,
}
SIN_LT = [k for k in INSTRUMENTOS if k != "grammaticality_lt"]
COLUMNAS = ["turn_id"] + [f"{k}_{v}" for k in INSTRUMENTOS for v in ("v1", "v2")]
_NUM_TEXTO = ["qn1_ttr", "qn1_ngram_repeticion", "qn1_legibilidad_fh",
              "cl2_lugar_jaccard_similarity", "cr2_entidad_grafo_densidad"]


# ---------------------------------------------------------------- v1 / v2
def _num(x):
    """Convierte a float, conservando None."""
    return None if x is None else float(x)


def v1_de_fila(fila):
    """Valores v1 (los guardados por el motor en turn_validation) de un turno."""
    nombres = fila.get("cr2_nombres_no_reconocidos") or []
    v1 = {k: _num(fila.get(k)) for k in _NUM_TEXTO}
    v1["cr2_n_nombres_no_reconocidos"] = len(nombres)
    v1["cr2_nombres_no_reconocidos"] = 1 if nombres else 0
    return v1


def toca_lt(turn_id, cada):
    """True si el turno entra en el muestreo de LanguageTool (1 de cada `cada` turnos)."""
    return turn_id % cada == 0


def calcular_fila(turn_id, texto, previo, ctx, v1, brazo, lt=None, normalizador=None):
    """Fila del CSV de un turno. `texto`/`previo`: dm_output crudo del turno y del anterior;
    `ctx`: Contexto con las entidades vigentes; `v1`: dict de v1_de_fila ({} si falta);
    `lt`: función texto->gramaticalidad (None = no calcular LanguageTool);
    `normalizador`: (texto, brazo) -> texto, por defecto normalizar_turno (con la identidad se
    obtiene el control «texto crudo», que debe reproducir v1)."""
    normalizador = normalizador or normalizar_turno
    norm = normalizador(texto, brazo)
    prev_norm = normalizador(previo, brazo)
    c = ctx.copia(escena_anterior=prev_norm, brazo=brazo)
    calc = it.calcular(norm, c, nombres=set(_NUM_TEXTO))
    nombres = it.nombres_no_reconocidos(norm, c)
    fila = {"turn_id": turn_id}
    for k in SIN_LT:
        fila[f"{k}_v1"] = v1.get(k)
    for k in _NUM_TEXTO:
        fila[f"{k}_v2"] = calc[k]
    fila["cr2_n_nombres_no_reconocidos_v2"] = len(nombres)
    fila["cr2_nombres_no_reconocidos_v2"] = 1 if nombres else 0
    fila["grammaticality_lt_v1"] = fila["grammaticality_lt_v2"] = None
    if lt is not None:
        crudo = (texto or "").strip()
        fila["grammaticality_lt_v1"] = lt(crudo)
        fila["grammaticality_lt_v2"] = fila["grammaticality_lt_v1"] if norm == crudo else lt(norm)
    return fila


# ---------------------------------------------------------------- sanidad
def _igual(a, b, dec):
    """Compara dos valores redondeados a `dec` decimales; dos None cuentan como iguales."""
    if a is None or b is None:
        return a is None and b is None
    return round(float(a), dec) == round(float(b), dec)


def sanidad_filas(filas, max_ejemplos=5):
    """Compara v1 y v2 fila a fila. En G2 (identidad) deben coincidir. Devuelve, por instrumento,
    n comparados, discrepancias, diferencia absoluta máxima y ejemplos."""
    out = {}
    for k, dec in INSTRUMENTOS.items():
        a, b = f"{k}_v1", f"{k}_v2"
        r = {"n": 0, "discrepancias": 0, "max_abs_dif": 0.0, "ejemplos": []}
        for f in filas:
            if a not in f and b not in f:
                continue
            v1, v2 = f.get(a), f.get(b)
            if k == "grammaticality_lt" and v1 is None and v2 is None:
                continue
            r["n"] += 1
            if not _igual(v1, v2, dec):
                r["discrepancias"] += 1
                if v1 is not None and v2 is not None:
                    r["max_abs_dif"] = max(r["max_abs_dif"], abs(float(v1) - float(v2)))
                if len(r["ejemplos"]) < max_ejemplos:
                    r["ejemplos"].append({"turn_id": f.get("turn_id"), "v1": v1, "v2": v2})
        if r["n"]:
            out[k] = r
    return out


# ---------------------------------------------------------------- CSV
def _a_celda(v):
    """Serializa un valor a celda CSV: None vacío, bool como int, float con `repr` (ida y vuelta exacta)."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return int(v)
    return repr(v) if isinstance(v, float) else v


def _de_celda(c):
    """Inversa de `_a_celda`: celda vacía a None, entero si lo parece, si no float."""
    if c == "":
        return None
    return int(c) if c.lstrip("-").isdigit() else float(c)


def escribir_csv(ruta, filas):
    """Escribe el CSV de una campaña de forma atómica (archivo .tmp y `os.replace`), para que una interrupción no deje un CSV a medias."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(ruta.suffix + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNAS)
        for f in filas:
            w.writerow([_a_celda(f.get(c)) for c in COLUMNAS])
    os.replace(tmp, ruta)


def leer_csv(ruta):
    """Lee el CSV de una campaña como lista de dicts con celdas ya tipadas."""
    with open(ruta, newline="", encoding="utf-8") as fh:
        return [{k: _de_celda(v) for k, v in row.items()} for row in csv.DictReader(fh)]


def csv_completo(ruta, n_esperado):
    """True si el CSV existe, se puede leer y tiene exactamente `n_esperado` filas (base de la reanudación)."""
    ruta = Path(ruta)
    if not ruta.exists():
        return False
    try:
        return len(leer_csv(ruta)) == n_esperado
    except (OSError, ValueError, csv.Error):
        return False


def csv_tiene_lt(ruta):
    """True si el CSV ya trae algún valor de LanguageTool."""
    return any(f.get("grammaticality_lt_v1") is not None for f in leer_csv(ruta))


# ---------------------------------------------------------------- LanguageTool con caché
class LTConCache:
    """LanguageTool (reporte_validacion.grammaticality_lt) con caché en disco propia
    (datos/datos_v2/_lt_cache.json). La caché de experimento/scripts/sensibilidad se lee como respaldo, sin escribirla."""

    def __init__(self, ruta=None):
        """Carga la caché propia (`ruta`, por defecto `datos/datos_v2/_lt_cache.json`) y, como respaldo de solo lectura, la de `experimento/scripts/sensibilidad`."""
        self.ruta = Path(ruta or DESTINO / "_lt_cache.json")
        try:
            self.mem = json.loads(self.ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.mem = {}
        try:
            self.previa = it._lt_cargar()
        except Exception:
            self.previa = {}
        self.nuevas = 0
        self.llamadas = 0

    def __call__(self, texto):
        """Gramaticalidad LanguageTool de `texto`, indexada por SHA-1 del texto; solo llama a la herramienta si no está en ninguna caché.

        Raises:
            RuntimeError: si LanguageTool no está disponible.
        """
        k = hashlib.sha1(texto.encode("utf-8")).hexdigest()
        if k in self.mem:
            return self.mem[k]
        if k in self.previa:
            self.mem[k] = self.previa[k]
            return self.mem[k]
        tool = it._rv._herramienta_lt()
        if tool is None:
            raise RuntimeError("LanguageTool no disponible")
        self.llamadas += 1
        self.mem[k] = it._rv.grammaticality_lt(texto, tool)
        self.nuevas += 1
        if self.nuevas % 100 == 0:
            self.guardar()
        return self.mem[k]

    def guardar(self):
        """Persiste la caché de forma atómica (archivo .tmp y `os.replace`)."""
        self.ruta.parent.mkdir(exist_ok=True)
        tmp = self.ruta.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.mem), encoding="utf-8")
        os.replace(tmp, self.ruta)


# ---------------------------------------------------------------- campaña
def nombre_csv(par, brazo):
    """Nombre del CSV de una campaña, p. ej. `par07_G1.csv`."""
    return f"par{par}_{brazo}.csv"


def procesar_campana(conn, par, brazo, campaign_id, destino, con_lt=False, lt_cada=10, hasta=1400,
                     lt_fn=None, forzar=False, normalizador=None):
    """Devuelve las filas calculadas o None si el CSV ya existía completo (reanudación)."""
    destino = Path(destino)
    ruta = destino / nombre_csv(par, brazo)
    existe = (not forzar) and csv_completo(ruta, hasta)
    if existe and not (con_lt and not csv_tiene_lt(ruta)):
        return None
    dc = datos.DatosCampana(conn, campaign_id, brazo, par)
    lt = None
    if con_lt:
        lt = lt_fn or LTConCache()
    if existe:                                       # solo falta LanguageTool
        filas = leer_csv(ruta)
        for f in filas:
            t = f["turn_id"]
            if toca_lt(t, lt_cada):
                crudo = dc.texto(t).strip()
                norm = (normalizador or normalizar_turno)(dc.texto(t), brazo)
                f["grammaticality_lt_v1"] = lt(crudo)
                f["grammaticality_lt_v2"] = f["grammaticality_lt_v1"] if norm == crudo else lt(norm)
        escribir_csv(ruta, filas)
        return filas
    v1 = {t: v1_de_fila(r) for t, r in datos.guardado_en_turn_validation(
        conn, campaign_id, range(1, hasta + 1)).items()}
    base = it.Contexto(pj_nombre=dc.pj_nombre, entidades=[], estados_pnj={}, brazo=brazo)
    filas = []
    for t in range(1, hasta + 1):
        if t not in dc.turnos:
            continue
        ctx = base.copia(entidades=dc._entidades_en(t))
        usa_lt = lt if (lt is not None and toca_lt(t, lt_cada)) else None
        # el lore (turno 0) no es formato de G1: previo = texto tal cual (normalizar_turno solo lo
        # recorta salvo en G1; el lore no trae etiquetas, así que el resultado es el mismo)
        filas.append(calcular_fila(t, dc.texto(t), dc.texto(t - 1), ctx, v1.get(t, {}), brazo, lt=usa_lt,
                                   normalizador=normalizador))
    escribir_csv(ruta, filas)
    if lt is not None and hasattr(lt, "guardar"):
        lt.guardar()
    return filas


# ---------------------------------------------------------------- principal
def main():
    """Recalcula los instrumentos v1/v2 de las campañas de `pares.todos()` y, al final, ejecuta la prueba de sanidad de G2.

    Opciones: `--con-lt`/`--lt-cada` (LanguageTool, lento), `--pares`, `--brazos`, `--hasta`, `--forzar` y
    `--control-g1-crudo` (solo el control de G1 sobre texto crudo). Las campañas con CSV completo se saltan.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--con-lt", action="store_true", help="incluye LanguageTool (LENTO)")
    ap.add_argument("--lt-cada", type=int, default=10, help="LanguageTool en 1 de cada N turnos")
    ap.add_argument("--pares", default="", help="lista de pares, p. ej. 07,08 (por defecto todos)")
    ap.add_argument("--brazos", default="G1,G2")
    ap.add_argument("--hasta", type=int, default=1400)
    ap.add_argument("--forzar", action="store_true", help="recalcula aunque exista el CSV")
    ap.add_argument("--control-g1-crudo", action="store_true",
                    help="solo el control: recalcular G1 sobre texto crudo debe reproducir v1")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    filtro = {p for p in args.pares.split(",") if p}
    brazos = [b for b in args.brazos.split(",") if b]
    import pares as _pares
    pares = [p for p in _pares.todos() if not filtro or p["par"] in filtro]
    if args.control_g1_crudo:
        control_g1_crudo(pares, args.hasta)
        return
    tareas = [(p, b) for p in pares for b in brazos]
    lt = LTConCache() if args.con_lt else None
    t0 = time.time()
    hechas = saltadas = 0
    with datos.abrir_conexion() as conn:
        for i, (p, b) in enumerate(tareas, 1):
            cid = p["campaign_g1" if b == "G1" else "campaign_g2"]
            t1 = time.time()
            filas = procesar_campana(conn, p["par"], b, cid, DESTINO, con_lt=args.con_lt,
                                     lt_cada=args.lt_cada, hasta=args.hasta, lt_fn=lt, forzar=args.forzar)
            if filas is None:
                saltadas += 1
                print(f"[{i:2}/{len(tareas)}] par{p['par']} {b}: ya existe, se salta", flush=True)
                continue
            hechas += 1
            transcurrido = time.time() - t0
            restante = transcurrido / hechas * (len(tareas) - i)
            print(f"[{i:2}/{len(tareas)}] par{p['par']} {b}: {len(filas)} turnos en {time.time() - t1:5.1f}s "
                  f"(total {transcurrido / 60:5.1f} min, quedan ~{restante / 60:4.1f} min)", flush=True)
    print(f"\n{hechas} campañas calculadas, {saltadas} saltadas, {time.time() - t0:.0f} s")
    sanidad_g2(pares, brazos)


def control_g1_crudo(pares, hasta=1400):
    """Control del recálculo en G1: con texto crudo (normalizador identidad) el contexto
    reconstruido debe reproducir lo guardado por el motor (v1). No escribe en datos/datos_v2/ salvo el
    resumen JSON; los CSV intermedios van a una carpeta temporal."""
    import tempfile
    filas = []
    with tempfile.TemporaryDirectory() as tmp, datos.abrir_conexion() as conn:
        for p in pares:
            filas += procesar_campana(conn, p["par"], "G1", p["campaign_g1"], tmp, hasta=hasta,
                                      normalizador=lambda x, brazo: (x or "").strip())
    s = sanidad_filas(filas)
    (DESTINO / "control_g1_crudo.json").write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nCONTROL G1 (texto crudo recalculado = v1 guardado): {len(filas)} turnos de {len(pares)} campañas")
    for k, r in s.items():
        print(f"  {k:32} comparados {r['n']:6}  discrepancias {r['discrepancias']:5}  max|dif| {r['max_abs_dif']:.4g}")
    return s


def sanidad_g2(pares, brazos=("G1", "G2")):
    """Prueba de sanidad en G2: como la normalización es la identidad, v1 debe ser igual a v2.

    Escribe `datos/datos_v2/sanidad_g2.json` e imprime las discrepancias por instrumento; no hace nada si G2 no está en `brazos`
    o no hay CSV.
    """
    if "G2" not in brazos:
        return
    filas = []
    for p in pares:
        ruta = DESTINO / nombre_csv(p["par"], "G2")
        if ruta.exists():
            filas += leer_csv(ruta)
    if not filas:
        return
    s = sanidad_filas(filas)
    (DESTINO / "sanidad_g2.json").write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nSANIDAD G2 (v1 = v2): {len(filas)} turnos de {len(pares)} campañas")
    for k, r in s.items():
        print(f"  {k:32} comparados {r['n']:6}  discrepancias {r['discrepancias']:5}  max|dif| {r['max_abs_dif']:.4g}")
        for e in r["ejemplos"][:3]:
            print(f"      ej.: {e}")


if __name__ == "__main__":
    main()
