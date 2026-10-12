"""
Cuantifica lo que Bryan notó a ojo (28/09) leyendo una transcripción G1 al azar: turnos donde el
jugador declara una habilidad entre {llaves} que `dados.resolver_turno` NO reconoce (por ejemplo
`{Inteligencia Investigación}` en vez de `{Investigación}` sola) -- el turno queda sin tirada ese
turno, y en G1 el Árbitro decide en modo `veredicto_sin_tirada` (dm/prompt_arbitro_g1.md) si
puede juzgar sin tirar (NUN-5) o si debe pedirla ("no inventar", ver orquestador/arbitro.py). Esto
NO es que se haya dejado fuera la arbitrariedad de los dados (ver §18 -- la tirada SI condiciona la
narración cuando se reconoce) -- es una brecha de PARSEO: el texto entre llaves tiene que coincidir
exactamente con un nombre de habilidad/característica válido (`dados.VALIDAS`/`CARACTERISTICAS_NORM`)
o se rechaza sin tirar, sea cual sea la razón (nombre compuesto, mal escrito, inventado). Mismo
código para G1 y G2 (`dados.resolver_turno`, "compartido con G2" -- ver vertical_slice.py paso 3),
así que si existe, es simétrico entre brazos, no un confusor de la comparación.

No recalcula nada mecánico ya guardado -- solo vuelve a correr `dados.extraer_habilidades` +
`dados.resolver_turno` sobre el texto YA guardado en `player_buffer` (mismo que ve el motor) para
contar, turno a turno, cuántas habilidades declaradas se aceptan vs. se rechazan, y con qué texto
exacto se rechazan (para ver si son mayormente nombres compuestos tipo "Ability Skill", errores de
tipeo, o habilidades que no existen en el SRD). Solo SELECT, sin LLM.

Salida: docs/reportes/auditoria_tags_rechazados.md (resumen) y
        datos_v2/cierre/tags_rechazados.csv (un renglón por tag rechazado: brazo,par,turno,texto)
Uso: PYTHONUTF8=1 py scripts/reporte_v2/auditoria_tags_rechazados.py
"""
import csv
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
for _p in (AQUI, RAIZ / "scripts", RAIZ / "scripts" / "sensibilidad", RAIZ / "orquestador"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import datos            # noqa: E402
import dados            # noqa: E402
import pares as _pares  # noqa: E402

D2 = RAIZ / "datos_v2"
HASTA = 1400


def main():
    """Cuenta, por brazo, las habilidades entre {llaves} que `dados.resolver_turno` acepta o rechaza.

    Recorre las 21 parejas (turnos 1-1400), reaplica el parseo del motor sobre `player_buffer` ya guardado
    (solo SELECT, sin LLM) y escribe `tags_rechazados.csv` (detalle) y el informe Markdown con el resumen
    por brazo y los 40 textos rechazados más frecuentes. Un error en un turno se cuenta y se omite.
    """
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    filas_detalle = []
    resumen = {"G1": Counter(), "G2": Counter()}   # turnos_con_tags, tags_declarados, tags_aceptados, tags_rechazados, errores
    rechazados_texto = Counter()

    with datos.abrir_conexion() as conn:
        for p in _pares.todos():
            for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
                cid = p[k]
                dc = datos.DatosCampana(conn, cid, brazo, p["par"])
                tabla = dados.tabla_pj(dc.pj) if dc.pj else None
                ts = [t for t in sorted(dc.turnos) if 1 <= t <= HASTA]
                for t in ts:
                    accion = dc.accion(t)
                    if not accion or "{" not in accion:
                        continue
                    habs = dados.extraer_habilidades(accion)
                    if not habs:
                        continue
                    resumen[brazo]["turnos_con_tags"] += 1
                    resumen[brazo]["tags_declarados"] += len(habs)
                    try:
                        _, tiradas, rechazadas = dados.resolver_turno(
                            accion, str(cid), t, tabla_modificadores=tabla)
                    except Exception as e:
                        resumen[brazo]["errores"] += 1
                        print(f"  ! error en {brazo} par{p['par']} turno {t}: {e}", flush=True)
                        continue
                    resumen[brazo]["tags_aceptados"] += len(tiradas)
                    resumen[brazo]["tags_rechazados"] += len(rechazadas)
                    for h in rechazadas:
                        rechazados_texto[h.strip()] += 1
                        filas_detalle.append({"brazo": brazo, "par": p["par"], "turno": t, "texto": h.strip()})
                print(f"{brazo} par{p['par']}: ok", flush=True)

    D2.mkdir(parents=True, exist_ok=True)
    (D2 / "cierre").mkdir(parents=True, exist_ok=True)
    ruta_csv = D2 / "cierre" / "tags_rechazados.csv"
    with open(ruta_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["brazo", "par", "turno", "texto"])
        w.writeheader()
        w.writerows(filas_detalle)

    L = ["# Auditoría de tags de habilidad rechazados (28/09)", "",
         "Generado por `scripts/reporte_v2/auditoria_tags_rechazados.py`. Cuenta, sobre el texto "
         "real de `player_buffer`, cuántas habilidades declaradas entre `{llaves}` `dados.resolver_turno` "
         "acepta (tira) vs. rechaza (no tira -- ver `dados.VALIDAS`/`CARACTERISTICAS_NORM`). Mismo código "
         "para G1 y G2.", "",
         "## Resumen por brazo", "",
         "| brazo | turnos con >=1 tag | tags declarados | tags aceptados | tags rechazados | % rechazados | errores |",
         "|---|---|---|---|---|---|---|"]
    for brazo in ("G1", "G2"):
        c = resumen[brazo]
        decl = c["tags_declarados"] or 1
        L.append(f"| {brazo} | {c['turnos_con_tags']} | {c['tags_declarados']} | {c['tags_aceptados']} | "
                 f"{c['tags_rechazados']} | {100*c['tags_rechazados']/decl:.1f}% | {c['errores']} |")
    L += ["", "## Textos rechazados más frecuentes", "",
          "| texto declarado (rechazado) | veces |", "|---|---|"]
    for texto, n in rechazados_texto.most_common(40):
        L.append(f"| `{texto}` | {n} |")
    L += ["", "Detalle completo (brazo, par, turno, texto) en `datos_v2/cierre/tags_rechazados.csv`."]
    ruta_md = RAIZ / "docs" / "reportes" / "auditoria_tags_rechazados.md"
    ruta_md.parent.mkdir(parents=True, exist_ok=True)
    ruta_md.write_text("\n".join(L), encoding="utf-8")
    print(f"\n-> {ruta_csv}\n-> {ruta_md}")


if __name__ == "__main__":
    main()
