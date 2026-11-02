"""
Validación humana v2 -- candidatos a ítems de CONTROL (los autores eligen 5 Sí + 5 No por detector y fijan la respuesta).

10 candidatos por celda (detector x respuesta esperada), fuera de la muestra (clave.csv) y de la validación anterior,
priorizando casos claros: persona2 Sí con hallazgo de confianza alta; persona2 No en turnos cortos; PNJ Sí con el PNJ
inactivo sujeto de un verbo de habla o con cita; PNJ No con el nombre junto a cadáver/cuerpo/muerte/recuerdo.
Salida: validacion_v2/candidatos_control.md (para los autores) y candidatos_control.json
    PYTHONUTF8=1 py validacion_v2/candidatos_control.py
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import generar_muestra as G                                   # noqa: E402
import persona2 as P                                          # noqa: E402

RNG = random.Random(G.SEMILLA + 1)
HABLA = re.compile(r"\b(dice|responde|murmura|grita|ordena|susurra|pregunta|sentencia|exclama|replica|añade)\b|[«\"—]")
RETRO = re.compile(r"\b(cad[aá]ver|tumba|muerte de|recuerd\w*|memoria|ausencia de|fantasma|restos de|desaparici[oó]n de|captura de|la ca[ií]da de|lo que le pas[oó]|qu[eé] fue de)\b", re.I)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    campanas = [{"par": p["par"], "brazo": b, "campaign_id": str(p[k])}
                for p in G._pares.todos() for b, k in (("G1", "campaign_g1"), ("G2", "campaign_g2"))]
    vistos = G.ya_etiquetados()
    with open(AQUI / "clave.csv", newline="", encoding="utf-8") as fh:
        vistos |= {(r["campaign_id"], int(r["turn_id"])) for r in csv.DictReader(fh)}
    p2_si, p2_no, pnj_si, _, pnj_nomenc = G.pools(campanas, vistos)
    for v in (p2_si, p2_no, pnj_si, pnj_nomenc):
        v.sort(key=lambda r: (r["campaign_id"], r["turn_id"]))
        RNG.shuffle(v)
    nombres = G.cargar_nombres()
    cache, out = {}, {"persona2_si": [], "persona2_no": [], "pnj_si": [], "pnj_no": []}
    with G.datos.abrir_conexion() as conn:
        def turno(r):
            cid = r["campaign_id"]
            if cid not in cache:
                cache[cid] = G.datos.DatosCampana(conn, cid, r["brazo"], r["par"])
            f = cache[cid].turnos[r["turn_id"]]
            buf = f["player_buffer"] or []
            pc = buf[0].get("pc") if buf and isinstance(buf[0], dict) else None
            return (nombres.get(pc) or cache[cid].pj_nombre, G.jugador(buf), G.normalizar_turno(f["dm_output"], r["brazo"]))

        for r in p2_si:
            if len(out["persona2_si"]) == 10:
                break
            pj, acc, tx = turno(r)
            hs = [h for h in P.detectar_usurpacion(tx, acc, None, pj)
                  if h["categoria"] in ("VOLICION", "COGNICION", "EMOCION", "HABLA") and h["confianza"] == "alta"]
            if hs and len(tx.split()) <= 160:
                out["persona2_si"].append(dict(r, pj=pj, accion=acc, texto=tx, esperada="Sí",
                                               evidencia=f"{hs[0]['categoria']}: «{tx[hs[0]['inicio']:hs[0]['fin']]}» — {hs[0]['evidencia']}"))
        for r in p2_no:
            if len(out["persona2_no"]) == 10:
                break
            pj, acc, tx = turno(r)
            if len(tx.split()) <= 90:
                out["persona2_no"].append(dict(r, pj=pj, accion=acc, texto=tx, esperada="No", evidencia="detector sin hallazgos; turno corto"))
        for cel, pool, regla, esp in (("pnj_si", pnj_si, HABLA, "Sí"),):
            for r in pool:
                if len(out[cel]) == 10:
                    break
                pj, acc, tx = turno(r)
                cand = r["detector_pnj"] if esp == "Sí" else r["mencionados"]
                ina = {x[0] for x in r["inactivos"]}
                for nm in sorted(n for n in cand if n in ina):
                    ors = [o for o in re.split(r"(?<=[.!?])\s+", tx) if nm in o]
                    if ors and ((any if esp == "Sí" else all)(regla.search(o) for o in ors)):
                        out[cel].append(dict(r, pj=pj, accion=acc, texto=tx, esperada=esp, pnj=nm,
                                             hecho=G.hecho(nm, r["inactivos"]), evidencia=" | ".join(ors)[:400]))
                        break
        for r in pnj_nomenc:
            if len(out["pnj_no"]) == 10:
                break
            pj, acc, tx = turno(r)
            nm = RNG.choice(sorted(x[0] for x in r["inactivos"]))
            if nm in tx or len(tx.split()) > 120:
                continue
            out["pnj_no"].append(dict(r, pj=pj, accion=acc, texto=tx, esperada="No", pnj=nm,
                                      hecho=G.hecho(nm, r["inactivos"]), evidencia="el PNJ no aparece en el turno"))
    for v in out.values():
        for r in v:
            r.pop("inactivos", None); r.pop("mencionados", None); r.pop("detector_pnj", None)
    (AQUI / "candidatos_control.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(AQUI / "candidatos_control.md", "w", encoding="utf-8") as fh:
        fh.write("# Candidatos a ítems de control — validación v2\n\nElegir 5 «Sí» y 5 «No» por detector. Marcar [x] y confirmar o corregir la respuesta esperada.\n")
        for cel, v in out.items():
            fh.write(f"\n## {cel} ({len(v)} candidatos)\n")
            for k, r in enumerate(v, 1):
                fh.write(f"\n### [ ] {cel}-{k:02d} · par{r['par']} {r['brazo']} turno {r['turn_id']} · esperada: **{r['esperada']}**\n\n")
                if r.get("hecho"):
                    fh.write(f"**Hecho:** {r['hecho']}\n\n")
                fh.write(f"**PJ:** {r['pj']}\n\n**Acción del jugador:**\n> {r['accion'].replace(chr(10), ' ')}\n\n**Turno del DM:**\n> {r['texto'].replace(chr(10), chr(10) + '> ')}\n\n*Evidencia:* {r['evidencia']}\n")
    print({k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()
