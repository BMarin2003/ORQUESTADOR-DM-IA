"""
A2 para tres instrumentos NUEVOS (qn1_legibilidad_sz, ventana_mtld, ventana_mattr): extensión POSTERIOR de la línea base, con informe propio.
La línea base (docs/reportes/sensibilidad_baseline.*, hash 735308b3…) no se toca ni se reescribe: sus expectativas se escribieron antes de correr y esto se añade después.

EXPECTATIVAS (fijadas aquí ANTES de correr; se imprime y guarda su SHA-256; no se editan tras ver resultados):
  qn1_legibilidad_sz  P6 = sin_cambio            barajar palabras conserva sílabas, palabras y frases: invariante exacto (igual que qn1_legibilidad_fh)
                      P11a_inyeccion = sin_cambio, P11b_eliminacion = sin_cambio
                                                 intención del diseño: la legibilidad no debería depender del formato de G1. SE PREDICE QUE INCUMPLE en G2/P11a igual
                                                 que Fernández-Huerta (el formato añade palabras y frases): es el artefacto de formato ya documentado, no un control
                                                 que deba pasar «por construcción».
  ventana_mtld, ventana_mattr   P9 = sin_cambio  permutar el orden de los 8 turnos NO es invariante exacto (ambas procesan el texto en secuencia), solo debe
                                                 no introducir sesgo sistemático entre ventanas; control estadístico, no matemático.
Ninguna celda de estas puede promover un instrumento: no hay celda confirmatoria posible para legibilidad, y para MTLD/MATTR falta una perturbación de ventana que
inyecte repetición (decisión aparte).

    PYTHONUTF8=1 py scripts/sensibilidad/correr_extension_sz_mtld.py
"""
import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
import correr_sensibilidad as cs      # noqa: E402
import perturbaciones as pt           # noqa: E402

EXPECTATIVAS = {
    "P6|qn1_legibilidad_sz": "sin_cambio",
    "P11a_inyeccion|qn1_legibilidad_sz": "sin_cambio",
    "P11b_eliminacion|qn1_legibilidad_sz": "sin_cambio",
    "P9|ventana_mtld": "sin_cambio",
    "P9|ventana_mattr": "sin_cambio",
}
HASH = hashlib.sha256(json.dumps(EXPECTATIVAS, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
SALIDA = RAIZ / "docs" / "reportes" / "sensibilidad_ext_sz_mtld"


def main():
    """Corre la línea base de correr_sensibilidad sobre las perturbaciones extra de qn1_legibilidad_sz y ventana_mtld/mattr.

    Fija y guarda el SHA-256 de las expectativas antes de correr, las registra en perturbaciones y
    comprueba que el hash de la tabla ESPERADO original no cambió; el informe se escribe aparte de la línea base."""
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"SHA-256 de las expectativas de la extensión (fijadas antes de correr): {HASH}", flush=True)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    (SALIDA.parent / "sensibilidad_ext_sz_mtld_expectativas.json").write_text(
        json.dumps({"sha256": HASH, "expectativas": EXPECTATIVAS}, indent=1, ensure_ascii=False), encoding="utf-8")
    hash_base = pt.hash_esperado(original=True)
    for clave, direccion in EXPECTATIVAS.items():
        pid, instrumento = clave.split("|")
        pt.registrar_esperado(pid, instrumento, direccion)
    assert pt.hash_esperado(original=True) == hash_base, "la tabla pre-especificada original cambió"
    print(f"hash de la tabla ESPERADO original intacto: {hash_base}", flush=True)
    return cs.main(["--salida", str(SALIDA)])


if __name__ == "__main__":
    main()
