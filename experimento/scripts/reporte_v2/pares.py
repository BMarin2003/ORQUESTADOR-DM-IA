"""Las 27 parejas del diseño (Par01-27). `datos.cargar_pares()` NO se toca: devuelve Par07-27 y de él depende la muestra congelada de A2 y A4b/c."""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent.parent
sys.path[:0] = [str(RAIZ / "experimento" / "scripts" / "sensibilidad"), str(RAIZ / "motor" / "orquestador")]
import datos  # noqa: E402


def todos():
    """Las 27 parejas (Par01-27) ordenadas por par: Par01-06 desde `ids_par01-06.json` (lote v0) más `datos.cargar_pares()` (Par07-27)."""
    extra = [{"par": e["par"], "lote": "v0", "lugar": e.get("lugar"), "campaign_g1": e["campaign_g1"], "campaign_g2": e["campaign_g2"]}
             for e in json.loads((RAIZ / "docs" / "ids_par01-06.json").read_text(encoding="utf-8"))]
    return sorted(extra + datos.cargar_pares(), key=lambda p: p["par"])
