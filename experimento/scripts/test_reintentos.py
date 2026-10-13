#!/usr/bin/env python3
"""
Prueba (sin red, respuestas simuladas) del reintento de llamar() en G2 y G1:
  - 429 "Model busy" dos veces y luego OK  -> reintenta y devuelve texto
  - 402 (sin saldo)                        -> NO reintenta (1 llamada), devuelve None
  - 429 para siempre                       -> se rinde tras 30 reintentos (31 llamadas), None
Uso: python experimento/scripts/test_reintentos.py
"""
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "motor" / "orquestador"))
import vertical_slice as g2  # noqa: E402
import vertical_slice_g1 as g1  # noqa: E402


class Resp:
    def __init__(self, body): self._b = body
    def read(self): return self._b
    def __enter__(self): return self
    def __exit__(self, *a): return False


def http_error(code):
    return urllib.error.HTTPError("http://x", code, "err", {},
                                  io.BytesIO(b'{"error":{"message":"Model busy, retry later"}}'))


OK = json.dumps({"choices": [{"message": {"content": "hola"}}],
                 "usage": {"prompt_tokens": 1, "completion_tokens": 1}}).encode()


def correr(mod, respuestas):
    llamadas = []

    def fake_urlopen(req, timeout=None):
        llamadas.append(1)
        r = respuestas(len(llamadas))
        if isinstance(r, Exception):
            raise r
        return Resp(r)

    real_open, real_sleep = urllib.request.urlopen, time.sleep
    urllib.request.urlopen, time.sleep = fake_urlopen, lambda s: None
    try:
        out = mod.llamar("m", "s", "u")
    finally:
        urllib.request.urlopen, time.sleep = real_open, real_sleep
    return out, len(llamadas)


for nombre, mod in (("G2", g2), ("G1", g1)):
    out, n = correr(mod, lambda i: http_error(429) if i <= 2 else OK)
    assert out and out["texto"] == "hola" and n == 3, (nombre, "429x2 luego OK", out, n)

    out, n = correr(mod, lambda i: http_error(402))
    assert out is None and n == 1, (nombre, "402 no debe reintentarse", out, n)

    out, n = correr(mod, lambda i: http_error(429))
    assert out is None and n == 31, (nombre, "429 eterno debe rendirse a las 31", out, n)
    print(f"{nombre}: OK (429 reintenta y se recupera; 402 fatal inmediato; 429 eterno se rinde tras 30)")
