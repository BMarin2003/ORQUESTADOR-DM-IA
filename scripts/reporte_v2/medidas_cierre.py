"""
Medidas DESCRIPTIVAS adicionales para el cierre de brechas (27 parejas, 54 campañas, turnos 1-1400, texto normalizado). Deterministas, solo SELECT, sin LLM.
NO tienen prueba de sensibilidad (A2): son medidas simples y transparentes, y así se declaran.
  rep_frases   fracción de turnos con una frase (>= 6 palabras) que aparece idéntica >= 3 veces en la campaña (límite inferior de las fórmulas evasivas y de la monotonía)
  nolatin      fracción de turnos con caracteres de otro alfabeto o U+FFFD (fallos de codificación / idioma)
  sd_ttr, sd_fh  desviación de la media de TTR y de Fernández-Huerta entre los 7 bloques de 200 turnos (estabilidad de estilo dentro de la campaña)
  t_pnj        turno de la primera mención de un PNJ no vivo (cl2_pnj_inactivo_actua v2); vacío si nunca
  n_npc, n_lugares, n_facciones, n_misiones, n_objetos   entidades registradas hasta el turno 1400 (proxy de emergencia; el motor de G1 tiene un agente extra que también las crea)
  mtld_campana, mattr_campana, mtld_bloque_media, mattr_bloque_media   diversidad léxica independiente de la longitud (McCarthy & Jarvis 2010; Covington & McFall 2010) sobre el texto concatenado; complementan a qn1_ttr
  sz_media, sd_sz   legibilidad de Szigriszt-Pazos (media de la campaña, turnos >= 2) y su variación entre bloques; complementa a Fernández-Huerta
  palabras_turno   mediana de palabras por turno (necesaria para leer el TTR por turno)
  ttr100, ngram100, frac_100   control de longitud: TTR y repetición de bigramas sobre las primeras 100 palabras de cada turno con >= 100 palabras, y la fracción de turnos que entra
  seg_turno    mediana de segundos entre turnos consecutivos (created_at; <= 900 s; incluye al jugador LLM y la extracción, y las corridas fueron concurrentes)
Salidas: datos_v2/cierre/por_campana.csv y bloques.csv (brazo, par, bloque, indicador...).
    PYTHONUTF8=1 py scripts/reporte_v2/medidas_cierre.py
"""
import csv
import re
import statistics as st
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos                                   # noqa: E402
import instrumentos_texto as it                # noqa: E402
import pares as _pares                         # noqa: E402
import recalcular as rc                        # noqa: E402
from normalizacion import normalizar_turno     # noqa: E402

D2 = RAIZ / "datos_v2"
DESTINO = D2 / "cierre"
NO_LATINO = re.compile("[Ͱ-᷿⺀-鿿ꀀ-퟿�]")
FRASES = re.compile(r"(?<=[.!?…])\s+|\n+")
HASTA, BLOQUE = 1400, 200
IND_BLOQUE = [("qn1_ttr", "num"), ("qn1_legibilidad_fh", "num"), ("qn1_ngram_repeticion", "num"), ("cl2_lugar_jaccard_similarity", "num"),
              ("cr2_nombres_no_reconocidos", "num"), ("cr1_veredicto_contradice_narracion", "bool"), ("cl2_pnj_inactivo_actua", "bool"),
              ("primaria", "p2"), ("secundaria", "p2")]


def norm_frase(f):
    """Frase en minúsculas y con espacios colapsados, para contar repeticiones exactas."""
    return re.sub(r"\s+", " ", f.strip().lower())


def frases_largas(texto):
    """Frases normalizadas de `texto` con al menos 6 palabras (candidatas a `rep_frases`)."""
    return [norm_frase(f) for f in FRASES.split(texto) if len(f.split()) >= 6]


def columna(par, brazo, fuente, nombre):
    """{turn_id: valor} de un indicador ya recalculado (CSV `num`, `bool` o `p2`), limitado a turnos <= `HASTA`.

    Las fuentes `num` y `bool` usan la columna `<nombre>_v2` (texto normalizado); `p2` usa `nombre` tal cual.
    """
    ruta = (D2 if fuente == "num" else D2 / ("booleanos" if fuente == "bool" else "persona2")) / rc.nombre_csv(par, brazo)
    col = nombre + "_v2" if fuente != "p2" else nombre
    return {r["turn_id"]: r[col] for r in rc.leer_csv(ruta) if r.get(col) is not None and r["turn_id"] <= HASTA}


def main():
    """Calcula las medidas descriptivas de cierre por campaña y por bloque de 200 turnos (solo SELECT, sin LLM).

    Incluye repetición de frases, caracteres no latinos, estabilidad de estilo, MTLD/MATTR, Szigriszt-Pazos,
    control de longitud a 100 palabras, turno del primer PNJ no vivo, segundos por turno y entidades registradas.
    Escribe `por_campana.csv`, `bloques.csv` y `top_frases.csv` en `datos_v2/cierre/`.
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    DESTINO.mkdir(parents=True, exist_ok=True)
    camp, bloques, top = [], [], []
    with datos.abrir_conexion() as conn:
        for p in _pares.todos():
            for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
                cid = p[k]
                dc = datos.DatosCampana(conn, cid, brazo, p["par"])
                ts = [t for t in sorted(dc.turnos) if 1 <= t <= HASTA]
                norm = {t: normalizar_turno(dc.turnos[t]["dm_output"], brazo) for t in ts}
                cuenta = Counter(f for t in ts for f in set(frases_largas(norm[t])))
                top += [{"brazo": brazo, "par": p["par"], "frase": f, "veces": n} for f, n in cuenta.most_common(3) if n >= 3]
                rep = {t: any(cuenta[f] >= 3 for f in set(frases_largas(norm[t]))) for t in ts}
                nol = {t: bool(NO_LATINO.search(norm[t])) for t in ts}
                cols = {(n, f): columna(p["par"], brazo, f, n) for n, f in IND_BLOQUE}
                cols[("rep_frases", "x")] = {t: float(v) for t, v in rep.items()}
                cols[("nolatin", "x")] = {t: float(v) for t, v in nol.items()}
                sz = {t: it.szigriszt_pazos(norm[t]) for t in ts}                       # Szigriszt-Pazos por turno; no está en turn_validation, se calcula del texto
                cols[("qn1_legibilidad_sz", "x")] = {t: v for t, v in sz.items() if v is not None}
                por_bloque = {}
                for (n, _), serie in cols.items():
                    for b in range(7):
                        v = [serie[t] for t in range(b * BLOQUE + 1, (b + 1) * BLOQUE + 1) if t in serie]
                        por_bloque.setdefault(n, []).append(sum(v) / len(v) if v else None)
                        bloques.append({"brazo": brazo, "par": p["par"], "bloque": b + 1, "indicador": n, "valor": por_bloque[n][-1]})
                pal = {t: it._palabras(norm[t]) for t in ts}                      # MTLD y MATTR sobre el texto concatenado del bloque y de la campaña (no por turno)
                mtld_b, mattr_b = [], []
                for b in range(7):
                    txt = [w for t in ts if b * BLOQUE < t <= (b + 1) * BLOQUE for w in pal[t]]
                    mtld_b.append(it.mtld(txt)); mattr_b.append(it.mattr(txt))
                    bloques.append({"brazo": brazo, "par": p["par"], "bloque": b + 1, "indicador": "mtld", "valor": mtld_b[-1]})
                    bloques.append({"brazo": brazo, "par": p["par"], "bloque": b + 1, "indicador": "mattr", "valor": mattr_b[-1]})
                todo = [w for t in ts for w in pal[t]]
                c100 = [pal[t][:100] for t in ts if t >= 2 and len(pal[t]) >= 100]             # control de longitud: primeras 100 palabras de cada turno (turnos >= 2)
                n_t2 = sum(1 for t in ts if t >= 2)
                pnj = cols[("cl2_pnj_inactivo_actua", "bool")]
                t_pnj = next((t for t in sorted(pnj) if pnj[t] == 1), "")
                ca = [r["created_at"] for r in conn.execute("SELECT created_at FROM turn_log WHERE campaign_id=%s AND turn_id BETWEEN 1 AND %s ORDER BY turn_id", (cid, HASTA)).fetchall()]
                gaps = [(b - a).total_seconds() for a, b in zip(ca, ca[1:])]
                gaps = [g for g in gaps if 0 <= g <= 900]
                n_ent = {tabla: conn.execute(f"SELECT count(*) AS n FROM {tabla} WHERE campaign_id=%s AND created_at_turn <= %s", (cid, HASTA)).fetchone()["n"]
                         for tabla in ("npcs", "locations", "factions", "quests", "items")}
                camp.append({"brazo": brazo, "par": p["par"],
                             "rep_frases": sum(rep.values()) / len(ts), "rep_max": max(cuenta.values()) if cuenta else 0,
                             "nolatin": sum(nol.values()) / len(ts), "n_turnos_nolatin": sum(nol.values()),
                             "sd_ttr": st.pstdev([x for x in por_bloque["qn1_ttr"] if x is not None]),
                             "sd_fh": st.pstdev([x for x in por_bloque["qn1_legibilidad_fh"] if x is not None]),
                             "sz_media": st.mean(v for t, v in sz.items() if v is not None and t >= 2),
                             "sd_sz": st.pstdev([x for x in por_bloque["qn1_legibilidad_sz"] if x is not None]),
                             "mtld_campana": it.mtld(todo), "mattr_campana": it.mattr(todo),
                             "mtld_bloque_media": st.mean(x for x in mtld_b if x is not None), "mattr_bloque_media": st.mean(x for x in mattr_b if x is not None),
                             "palabras_turno": st.median(len(pal[t]) for t in ts),
                             "ttr100": st.mean(len(set(w)) / 100 for w in c100) if c100 else "",
                             "ngram100": st.mean(1 - len(set(zip(w, w[1:]))) / 99 for w in c100) if c100 else "",
                             "frac_100": len(c100) / n_t2 if n_t2 else "",
                             "t_pnj": t_pnj, "seg_turno": st.median(gaps) if gaps else "",
                             "n_npc": n_ent["npcs"], "n_lugares": n_ent["locations"], "n_facciones": n_ent["factions"],
                             "n_misiones": n_ent["quests"], "n_objetos": n_ent["items"]})
                print(f"par{p['par']} {brazo}: rep {camp[-1]['rep_frases']:.3f} nolatin {camp[-1]['n_turnos_nolatin']} seg/turno {camp[-1]['seg_turno']}", flush=True)
    for nombre, filas in (("por_campana.csv", camp), ("bloques.csv", bloques)):
        with open(DESTINO / nombre, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    if top:
        with open(DESTINO / "top_frases.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(top[0])); w.writeheader(); w.writerows(top)
    print("escrito", DESTINO)


if __name__ == "__main__":
    main()
