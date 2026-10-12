"""Diagnóstico del caso atípico OE-2 (docs/resultados/por_campana_largo.csv:
par=06, brazo=G2, papalampidi_C=0.0 -- el mínimo de los 27 G2, el único caso
citado en analisis-brechas-deep-research-v2-corregido-2026-09-21.md como
"perdida total del rastreo de entidades principales").

NO reimplementa nada: llama a coherencia_entidad_C() tal cual vive en
orquestador/reporte_validacion.py (mismo principio que scripts/sensibilidad/
-- nunca dos copias de la misma fórmula que puedan divergir). Solo imprime
el detalle por protagonista (nombre, Ci, sección primera/última mención)
para poder leer manualmente los turnos relevantes y decidir si es un caso
genuino de "PNJ abandonado narrativamente" (consistente con las otras
métricas CL-2 de esta misma fila: PNJ inactivo mencionado / PNJ inactivo
como sujeto, que en G2 llegan a 15.94% y 73.52 por 1000 turnos de máximo)
o un artefacto del matching literal de nombres (sin resolución de
correferencia, límite ya documentado del instrumento).

Uso (desde la raíz del repo, con el entorno que sí tiene psycopg y acceso
a Postgres -- este diagnóstico NO corre desde el sandbox de Claude porque
DATABASE_URL apunta a 127.0.0.1, no accesible desde ahí):

    python scripts/reporte_v2/diagnostico_caso_atipico_oe2.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path[:0] = [str(RAIZ / "orquestador"), str(RAIZ / "scripts" / "reporte_v2")]

import db as bd                                    # noqa: E402
from reporte_validacion import coherencia_entidad_C  # noqa: E402
import pares as _pares                              # noqa: E402


def main():
    """Imprime el detalle por protagonista de `coherencia_entidad_C` en la campaña G2 de la pareja 06 (el mínimo, C = 0).

    Muestra Ci, sección de primera y última mención y los turnos aproximados de cada una, para leer a mano el
    pasaje y decidir si es abandono narrativo genuino o un artefacto del emparejamiento literal de nombres.
    Requiere acceso a Postgres (`DATABASE_URL`).
    """
    par = next(p for p in _pares.todos() if str(p["par"]).zfill(2) == "06")
    campaign_id = par["campaign_g2"]
    print(f"par06 / G2 -> campaign_id={campaign_id}")

    camp = bd.Campaña(campaign_id)
    turnos = camp.turnos_narracion()
    entidades = camp.entidades()
    print(f"n_turnos={len(turnos)}  n_entidades(character/npc)="
          f"{sum(1 for e in entidades if e['tipo'] in ('character', 'npc'))}")

    C, L_efectivo, detalle = coherencia_entidad_C(turnos, entidades)
    print(f"\nC={C}  L_efectivo={L_efectivo}")
    print("\nProtagonistas (top-3 por menciones literales) y su span:")
    for nombre, Ci, sf, sl in detalle:
        print(f"  {nombre!r}: Ci={Ci}  primera_sección={sf}  "
              f"última_sección={sl}  (de {L_efectivo} secciones)")
        # turno de la primera y última sección para poder leer el pasaje real
        n = len(turnos)
        ini_primera = (sf * n) // L_efectivo
        fin_ultima = ((sl + 1) * n) // L_efectivo - 1
        print(f"    -> turnos aprox. [{turnos[ini_primera]['turn_id']} .. "
              f"{turnos[min(fin_ultima, n - 1)]['turn_id']}]")

    if not detalle:
        print("\n(sin protagonistas con menciones -- revisar entidades() "
              "y _top_protagonistas() manualmente)")


if __name__ == "__main__":
    main()
