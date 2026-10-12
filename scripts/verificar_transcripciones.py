#!/usr/bin/env python3
"""
Integridad de las transcripciones Par 07-17. Tres fuentes, cruzadas:
  1. Postgres (turn_log, turn_validation, state_deltas): verdad de referencia.
  2. El .md exportado: debe ser EXACTAMENTE lo que sale de turn_log (byte a byte).
  3. Las bitacoras por corrida (logs/par_NN_real_g?_*.md): cada turno debe haberse
     completado en UNA sola corrida (dos = turno aplicado dos veces) y su narracion
     debe coincidir con la de Postgres (detecta turnos perdidos o reescritos en las costuras).

Uso: python scripts/verificar_transcripciones.py [--pares 07,08] [--arm ambos|G2|G1]
                                                  [--dir transcripciones/par07-17]
Sale con codigo 1 si algun chequeo DURO falla.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
import db  # noqa: E402
import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# "null"/"none" sueltos NO: "Kaelum Null" es un nombre inventado legitimo (Par11 G1).
ARTEFACTOS = re.compile(
    r"<think|</think|```|Traceback|engine_overloaded|HTTP 4\d\d|\[ERROR|El DM no respondi|"
    r"�|\bundefined\b|as an AI|como (?:una )?IA\b", re.I)
JSON_CRUDO = re.compile(r'^\s*\{\s*"narrativa"', re.M)   # G1: el narrador devolvio JSON y no se parseo
META_OOC = re.compile(r"\s*\[")                         # DM fuera de personaje: "[Para resolver... necesito una tirada]"
ASIATICO = re.compile(r"[぀-ヿ一-鿿가-힯Ѐ-ӿ]")  # kana, CJK, hangul, cirilico
EN = re.compile(r"\b(?:the|and|with|you|your|his|her)\b", re.I)
ES = re.compile(r"\b(?:el|la|los|las|de|que|y|en|un|una|con)\b", re.I)
CIERRE = ".!?…»”\"')*_`]"
CORTO = 100          # dm_output de un turno normal por debajo de esto = sospechoso
ENCABEZADO_FRAG = re.compile(r"^## Turno (\d+) — ", re.M)
ESTADO_DESPUES = re.compile(r"^### \[\d+\] ESTADO DESPUÉS", re.M)


def norm(s):
    return re.sub(r"\s+", "", s or "")


def ruta_transcripcion(titulo, limite, carpeta):
    return carpeta / f"transcripcion_{titulo.replace(' ', '_').replace('·', '-')}_1-{limite}.md"


def cuerpo_esperado(turnos):
    """Mismo formato que scripts/exportar_transcripcion.py (cuerpo tras el encabezado)."""
    out = []
    for t in turnos:
        out.append(f"## Turno {t['turn_id']}\n\n")
        for e in (t["player_buffer"] or []):
            out.append(f"**Jugador:** {e.get('text', '') if isinstance(e, dict) else e}\n\n")
        out.append(f"{t['dm_output'] or ''}\n\n")
    return "".join(out)


def fragmentos(par, brazo, cid):
    marca = cid[:8]
    pat = f"par_{par}_real_{brazo.lower()}_*_{marca}_turnos_*.md"
    return sorted((RAIZ / "logs").rglob(pat), key=lambda p: p.stem.rsplit("_", 2)[-2:])


def cruzar_fragmentos(par, brazo, cid, turnos_db):
    """-> dict con cobertura de turnos completos por fragmento, dobles, sin cobertura, desajustes."""
    dm = {t["turn_id"]: norm(t["dm_output"]) for t in turnos_db}
    completos = {}   # turno -> [fragmento,...]
    desajuste, huerfanos, costuras, n_frag = [], 0, [], 0
    for f in fragmentos(par, brazo, cid):
        txt = f.read_text(encoding="utf-8", errors="replace")
        cab = list(ENCABEZADO_FRAG.finditer(txt))
        if not cab:
            continue
        n_frag += 1
        primero = None
        for i, m in enumerate(cab):
            fin = cab[i + 1].start() if i + 1 < len(cab) else len(txt)
            sec, n = txt[m.start():fin], int(m.group(1))
            if not ESTADO_DESPUES.search(sec):
                huerfanos += 1          # turno interrumpido: nunca se escribio a Postgres
                continue
            completos.setdefault(n, []).append(f.name)
            if primero is None:
                primero = n
            citas = norm("".join(l[1:] for l in sec.splitlines() if l.startswith(">")))
            if n in dm and dm[n][:80] not in citas:
                desajuste.append(n)
        if primero is not None:
            costuras.append(primero)
    dobles = sorted(n for n, fs in completos.items() if len(fs) > 1)
    sin_log = sorted(n for n in dm if n >= 1 and n not in completos)
    return {"fragmentos": n_frag, "costuras": costuras[1:], "dobles": dobles, "sin_log": sin_log,
            "desajuste": sorted(desajuste), "huerfanos": huerfanos}


def verificar(conn, e, brazo, carpeta):
    cid = e["campaign_g2" if brazo == "G2" else "campaign_g1"]
    camp = conn.execute("SELECT title, current_turn FROM campaigns WHERE id=%s", (cid,)).fetchone()
    turnos = conn.execute("SELECT turn_id, player_buffer, dm_output, gate_passed, created_at FROM turn_log "
                          "WHERE campaign_id=%s ORDER BY turn_id", (cid,)).fetchall()
    ids = [t["turn_id"] for t in turnos]
    duro, aviso, info = [], [], {}

    # --- A. estructura en Postgres
    esperado = list(range(0, camp["current_turn"] + 1))
    if ids != esperado:
        faltan = sorted(set(esperado) - set(ids))
        duro.append(f"turn_log no es 0..{camp['current_turn']} contiguo (faltan {faltan[:8]}, "
                    f"duplicados {[k for k, v in Counter(ids).items() if v > 1][:8]})")
    tv = {r["turn_id"] for r in conn.execute("SELECT turn_id FROM turn_validation WHERE campaign_id=%s", (cid,))}
    if tv != set(range(1, camp["current_turn"] + 1)):
        duro.append(f"turn_validation no cubre 1..{camp['current_turn']} (n={len(tv)})")
    a_medias = sum(conn.execute(f"SELECT count(*) AS n FROM {t} WHERE campaign_id=%s AND turn_id>%s",
                                (cid, camp["current_turn"])).fetchone()["n"]
                   for t in ("state_deltas", "turn_validation", "turn_log"))
    if a_medias:
        duro.append(f"{a_medias} fila(s) escritas para un turno > current_turn")
    dup_delta = conn.execute(
        "SELECT count(*) AS n FROM (SELECT 1 FROM state_deltas WHERE campaign_id=%s "
        "GROUP BY turn_id, entity_type, entity_id, field_name, new_value, source, evidence HAVING count(*)>1) x",
        (cid,)).fetchone()["n"]
    if dup_delta:
        duro.append(f"{dup_delta} grupo(s) de state_deltas identicos en el mismo turno (posible doble aplicacion)")

    # --- B. contenido de los turnos
    normales = [t for t in turnos if t["turn_id"] >= 1]
    vacios = [t["turn_id"] for t in normales if not (t["dm_output"] or "").strip()]
    cortos = [t["turn_id"] for t in normales if 0 < len((t["dm_output"] or "").strip()) < CORTO]
    sin_cierre = [t["turn_id"] for t in normales if (t["dm_output"] or "").strip()
                  and (t["dm_output"] or "").rstrip()[-1] not in CIERRE]
    artef = [t["turn_id"] for t in normales if ARTEFACTOS.search(t["dm_output"] or "")]
    asia = [t["turn_id"] for t in normales if ASIATICO.search(t["dm_output"] or "")]
    ingles = [t["turn_id"] for t in normales
              if len(EN.findall(t["dm_output"] or "")) >= 8
              and len(EN.findall(t["dm_output"] or "")) > len(ES.findall(t["dm_output"] or ""))]
    sin_jug = [t["turn_id"] for t in normales
               if not any((x.get("text", "") if isinstance(x, dict) else str(x)).strip()
                          for x in (t["player_buffer"] or []))]
    jug_txt = lambda t: " ".join((x.get("text", "") if isinstance(x, dict) else str(x))
                                 for x in (t["player_buffer"] or []))
    artef_j = [t["turn_id"] for t in normales if ARTEFACTOS.search(jug_txt(t))]
    json_crudo = [t["turn_id"] for t in normales if JSON_CRUDO.search(t["dm_output"] or "")]
    meta = [t["turn_id"] for t in normales if META_OOC.match(t["dm_output"] or "")]
    asia_j = [t["turn_id"] for t in normales if ASIATICO.search(jug_txt(t))]
    if vacios:
        duro.append(f"dm_output vacio en turnos {vacios[:8]}")
    if artef:
        duro.append(f"artefactos tecnicos en dm_output (turnos {artef[:8]}, n={len(artef)})")
    if artef_j:
        duro.append(f"artefactos tecnicos en el buffer del jugador (turnos {artef_j[:8]}, n={len(artef_j)})")
    if json_crudo:
        aviso.append(f"JSON crudo del narrador guardado como narracion en {len(json_crudo)} turno(s) {json_crudo[:6]}")
    if meta:
        aviso.append(f"{len(meta)} turno(s) con meta-comentario entre corchetes (DM fuera de personaje) {meta[:6]}")
    if asia_j:
        aviso.append(f"caracteres CJK/cirilicos en el buffer del jugador, turnos {asia_j[:6]}")
    if asia:
        aviso.append(f"caracteres CJK/cirilicos en {len(asia)} turno(s) {asia[:6]}")
    if ingles:
        aviso.append(f"{len(ingles)} turno(s) posiblemente en ingles {ingles[:6]}")
    if sin_jug:
        aviso.append(f"{len(sin_jug)} turno(s) sin texto del jugador {sin_jug[:6]}")
    if cortos:
        aviso.append(f"{len(cortos)} dm_output < {CORTO} caracteres {cortos[:6]}")
    dup_dm = [k for k, v in Counter(norm(t["dm_output"]) for t in normales).items() if v > 1 and k]
    dup_j = sum(1 for a, b in zip(normales, normales[1:]) if jug_txt(a).strip() and jug_txt(a) == jug_txt(b))
    info.update(json_crudo=len(json_crudo), meta_corchetes=len(meta), otro_alfabeto=len(asia), sin_cierre=len(sin_cierre), dm_duplicados=len(dup_dm), jugador_repetido_consecutivo=dup_j,
                gate_falso=sum(1 for t in normales if t["gate_passed"] is False),
                desordenado_por_fecha=sum(1 for a, b in zip(turnos, turnos[1:]) if b["created_at"] < a["created_at"]))
    largos = sorted(len(t["dm_output"] or "") for t in normales)
    info["dm_chars"] = f"mediana {largos[len(largos)//2]}  p1 {largos[len(largos)//100]}  max {largos[-1]}"

    # --- C. el .md exportado == turn_log, byte a byte
    ruta = ruta_transcripcion(camp["title"], camp["current_turn"], carpeta)
    if not ruta.exists():
        duro.append(f"no existe el archivo {ruta.name}")
    else:
        try:
            txt = ruta.read_text(encoding="utf-8")
        except UnicodeDecodeError as ex:
            txt = None
            duro.append(f"el .md no es UTF-8 valido: {ex}")
        if txt is not None:
            cuerpo = txt.split("\n---\n\n", 1)[1] if "\n---\n\n" in txt else ""
            if cuerpo != cuerpo_esperado(turnos):
                duro.append("el cuerpo del .md NO coincide con turn_log (re-exportar)")
            n_cab = len(re.findall(r"^## Turno \d+$", txt, re.M))
            if n_cab != len(turnos):
                aviso.append(f"{n_cab} encabezados '## Turno N' vs {len(turnos)} turnos (un dm_output contiene un encabezado falso)")
            info["md_bytes"] = ruta.stat().st_size

    # --- D. costuras entre corridas (bitacoras)
    fr = cruzar_fragmentos(e["par"], brazo, cid, turnos)
    if fr["dobles"]:
        duro.append(f"{len(fr['dobles'])} turno(s) completados en 2+ corridas {fr['dobles'][:8]}")
    if fr["desajuste"]:
        duro.append(f"{len(fr['desajuste'])} turno(s) cuya narracion del log difiere de Postgres {fr['desajuste'][:8]}")
    if fr["sin_log"]:
        aviso.append(f"{len(fr['sin_log'])} turno(s) sin bitacora que los respalde (p.ej. {fr['sin_log'][:6]})")
    by = {t["turn_id"]: t for t in turnos}
    malas = [s for s in fr["costuras"] if s - 1 in by and s in by and
             (norm(by[s]["dm_output"]) == norm(by[s - 1]["dm_output"]) or
              (jug_txt(by[s]).strip() and jug_txt(by[s]) == jug_txt(by[s - 1])))]
    if malas:
        duro.append(f"costura(s) con turno repetido en {malas}")
    return {"par": e["par"], "brazo": brazo, "n": len(turnos), "duro": duro, "aviso": aviso,
            "info": info, "frag": fr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", default="")
    ap.add_argument("--arm", choices=["ambos", "G2", "G1"], default="ambos")
    ap.add_argument("--dir", default="transcripciones/par07-17")
    ap.add_argument("--ids", default="docs/ids_par07-17.json")
    args = ap.parse_args()
    carpeta = RAIZ / args.dir
    pares = {p.strip().zfill(2) for p in args.pares.split(",") if p.strip()}
    ids = [e for e in json.loads((RAIZ / args.ids).read_text(encoding="utf-8"))
           if not pares or e["par"] in pares]
    hay_duro = False
    with psycopg.connect(db.DSN, row_factory=dict_row) as conn:
        for e in ids:
            for brazo in ("G2", "G1"):
                if args.arm not in ("ambos", brazo):
                    continue
                r = verificar(conn, e, brazo, carpeta)
                f = r["frag"]
                estado = "FALLA" if r["duro"] else ("AVISOS" if r["aviso"] else "OK")
                hay_duro |= bool(r["duro"])
                print(f"Par{r['par']} {brazo}  {estado:6}  {r['n']} turnos · {f['fragmentos']} corridas · "
                      f"costuras en turnos {f['costuras']} · {f['huerfanos']} turno(s) interrumpido(s) descartados")
                for m in r["duro"]:
                    print(f"      ✗ {m}")
                for m in r["aviso"]:
                    print(f"      ! {m}")
                print(f"      · {r['info']}")
    sys.exit(1 if hay_duro else 0)


if __name__ == "__main__":
    main()
