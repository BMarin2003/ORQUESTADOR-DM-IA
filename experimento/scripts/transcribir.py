r"""
Transcribe audio con Whisper Large V3 en DeepInfra.

Usa la misma cuenta y saldo que ya está configurado. Coste: $0.00045/minuto,
o sea ~$0.03 por los 68 minutos de las dos reuniones.

Los .ogg ya vienen convertidos a 16 kHz mono — que es a lo que Whisper
remuestrea internamente de todas formas — así que 42 MB pasan a 5 MB sin
pérdida útil de información.

Uso:
  py transcribir.py audio\Tesis2_s1_m4a.ogg
  py transcribir.py audio\*.ogg
  py transcribir.py audio\reunion.ogg --trocear 600   # si falla por tamaño
"""

import argparse
import glob
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ENDPOINT = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3"


def multipart(campos, archivo):
    """Construye un cuerpo multipart/form-data sin dependencias externas."""
    limite = uuid.uuid4().hex
    cuerpo = b""
    for k, v in campos.items():
        cuerpo += (f"--{limite}\r\n"
                   f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n').encode()
    nombre = Path(archivo).name
    tipo = mimetypes.guess_type(nombre)[0] or "application/octet-stream"
    cuerpo += (f"--{limite}\r\n"
               f'Content-Disposition: form-data; name="audio"; filename="{nombre}"\r\n'
               f"Content-Type: {tipo}\r\n\r\n").encode()
    cuerpo += Path(archivo).read_bytes()
    cuerpo += f"\r\n--{limite}--\r\n".encode()
    return cuerpo, f"multipart/form-data; boundary={limite}"


def transcribir(key, ruta, idioma="es"):
    """Transcribe un archivo de audio con la API de DeepInfra; devuelve el JSON de respuesta con el tiempo de proceso, o None si falla (413: sugiere --trocear)."""
    cuerpo, ctype = multipart({"language": idioma, "task": "transcribe"}, ruta)
    req = urllib.request.Request(
        ENDPOINT, data=cuerpo,
        headers={"Authorization": f"bearer {key}", "Content-Type": ctype},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detalle = e.read().decode()[:300]
        print(f"  HTTP {e.code}: {detalle}", file=sys.stderr)
        if e.code == 413:
            print("  → Archivo demasiado grande. Reintenta con --trocear 600",
                  file=sys.stderr)
        return None
    d["_segundos_proceso"] = round(time.time() - t0, 1)
    return d


def trocear(ruta, segundos):
    """Parte el audio en trozos con ffmpeg. Devuelve las rutas."""
    salida = Path(ruta).parent / f"{Path(ruta).stem}_trozos"
    salida.mkdir(exist_ok=True)
    patron = str(salida / "parte_%03d.ogg")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "segment",
         "-segment_time", str(segundos), "-c", "copy", patron, "-y"],
        check=True)
    return sorted(str(p) for p in salida.glob("parte_*.ogg"))


def formatear(d, desplazamiento=0.0):
    """Texto con marcas de tiempo por segmento."""
    lineas = []
    for s in d.get("segments", []):
        t = s.get("start", 0) + desplazamiento
        m, seg = divmod(int(t), 60)
        h, m = divmod(m, 60)
        marca = f"[{h:02d}:{m:02d}:{seg:02d}]" if h else f"[{m:02d}:{seg:02d}]"
        lineas.append(f"{marca} {s.get('text', '').strip()}")
    return "\n".join(lineas) if lineas else d.get("text", "")


def main():
    """Transcribe los archivos indicados (admite comodines), troceándolos si se pide, y escribe cada transcripción en un .txt junto al audio con una estimación del costo. Requiere DEEPINFRA_API_KEY en el entorno."""
    ap = argparse.ArgumentParser()
    ap.add_argument("archivos", nargs="+")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--trocear", type=int, default=0,
                    help="segundos por trozo; 0 = archivo entero")
    args = ap.parse_args()

    key = os.environ.get("DEEPINFRA_API_KEY")
    if not key:
        sys.exit("Falta DEEPINFRA_API_KEY. Carga el .env primero.")

    rutas = []
    for patron in args.archivos:
        rutas.extend(glob.glob(patron) or [patron])

    for ruta in rutas:
        if not Path(ruta).exists():
            print(f"No existe: {ruta}", file=sys.stderr)
            continue

        mb = Path(ruta).stat().st_size / 1e6
        print(f"\n{Path(ruta).name}  ({mb:.1f} MB)")

        partes = trocear(ruta, args.trocear) if args.trocear else [ruta]
        if len(partes) > 1:
            print(f"  troceado en {len(partes)} partes de {args.trocear}s")

        completo, desplazamiento, total_seg = [], 0.0, 0.0
        for i, parte in enumerate(partes):
            if len(partes) > 1:
                print(f"  parte {i+1}/{len(partes)}...", end=" ", flush=True)
            d = transcribir(key, parte, args.idioma)
            if d is None:
                print("FALLÓ")
                break
            completo.append(formatear(d, desplazamiento))
            dur = d.get("input_length_ms", 0) / 1000 or args.trocear
            desplazamiento += dur
            total_seg += dur
            if len(partes) > 1:
                print(f"ok ({d['_segundos_proceso']}s)")

        if not completo:
            continue

        destino = Path(ruta).with_suffix(".txt")
        destino.write_text("\n".join(completo), encoding="utf-8")
        palabras = sum(len(t.split()) for t in completo)
        print(f"  → {destino}  ({palabras} palabras, "
              f"~${total_seg/60*0.00045:.4f})")


if __name__ == "__main__":
    main()
