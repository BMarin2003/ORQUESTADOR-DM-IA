"""
Contexto ampliado para enchufar los instrumentos A4b/c al arnés de sensibilidad sin editarlo.

`instrumentos_texto.Contexto` no tiene sitio para la acción del jugador, el nulo de la campaña ni
la referencia del escenario. Esta subclase (dataclass) añade tres campos con valor por defecto;
`Contexto.copia()` usa dataclasses.replace, así que los conserva cuando una perturbación copia el
contexto.
"""
import sys
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_SENS = AQUI.parent / "sensibilidad"
if str(_SENS) not in sys.path:
    sys.path.insert(0, str(_SENS))

import instrumentos_texto as it   # noqa: E402


@dataclass
class ContextoA4bc(it.Contexto):
    """Contexto del arnés ampliado con el pool de acciones, el turno, el escenario y el modelo de anclaje."""
    pool: object = None        # respuesta_accion.PoolAcciones de la campaña
    turno: int = 0             # turno de la respuesta (inicio de la ventana en instrumentos de ventana)
    escenario: object = None   # anclaje_escenario.Escenario del par
    modelo: object = None      # anclaje_escenario.ModeloAnclaje (idf de las 42 campañas)


def crear(pool=None, turno=0, escenario=None, modelo=None, brazo="G2", **kw):
    """Construye un ContextoA4bc con valores neutros (PJ, sin entidades ni estados PNJ) que `kw` puede sobrescribir."""
    base = dict(pj_nombre="PJ", entidades=[], estados_pnj={})
    base.update(kw)
    return ContextoA4bc(pool=pool, turno=turno, escenario=escenario, modelo=modelo, brazo=brazo, **base)
