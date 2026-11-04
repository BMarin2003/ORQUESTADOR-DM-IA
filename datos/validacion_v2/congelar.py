"""Congela el protocolo de la validación humana v2: SHA-256 de libro de códigos, formulario, ítems, claves, scripts y
detectores. Se ejecuta UNA vez, antes de entregar el formulario. Verificar después con:  py validacion_v2/congelar.py --verificar"""
import datetime
import hashlib
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SALIDA = AQUI / "congelamiento_v2.sha256"
ARCHIVOS = [
    "validacion_v2/libro_de_codigos_v2.md", "validacion_v2/plantilla_formulario.html", "validacion_v2/formulario_v2.html",
    "validacion_v2/items.json", "validacion_v2/items_cd.json", "validacion_v2/items_final.json",
    "validacion_v2/clave.csv", "validacion_v2/clave_cd.csv", "validacion_v2/controles_clave.csv", "validacion_v2/pool_pnj.csv",
    "validacion_v2/candidatos_control.json", "validacion_v2/candidatos_control_cd.json",
    "validacion_v2/Consentimiento_informado_evaluadores.docx",
    "validacion_v2/pool_pnj.py", "validacion_v2/generar_muestra.py", "validacion_v2/candidatos_control.py",
    "validacion_v2/fijar_controles.py", "validacion_v2/ampliar_cd.py", "validacion_v2/ajustar_cd.py",
    "validacion_v2/fijar_controles_cd.py", "validacion_v2/construir_formulario.py", "validacion_v2/congelar.py",
    "scripts/instrumentos/persona2.py", "scripts/instrumentos/lexicon_persona2.json",
    "scripts/instrumentos/respuesta_accion.py", "scripts/instrumentos/lemas_es.py",
    "orquestador/reporte_validacion.py", "scripts/reporte_v2/normalizacion.py",
]


def h(ruta):
    return hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest()


if "--verificar" in sys.argv:
    malos = [l.split(None, 1)[1] for l in SALIDA.read_text(encoding="utf-8").splitlines()
             if l and not l.startswith("#") and h(l.split(None, 1)[1].strip()) != l.split(None, 1)[0]]
    print("OK: nada cambió" if not malos else f"CAMBIARON: {malos}")
    sys.exit(1 if malos else 0)
if SALIDA.exists():
    sys.exit("ABORTA: el protocolo ya está congelado; usa --verificar")
lineas = [f"# Validación humana v2 · congelado {datetime.datetime.now().astimezone().isoformat(timespec='seconds')}"]
lineas += [f"{h(r)}  {r}" for r in ARCHIVOS]
SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
