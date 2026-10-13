"""
Paso 1 del instrumento EXPLORATORIO cl2_recall_semantico (ver comun.py): llena medicion_oraciones
(tabla ADITIVA de motor/migrations/002_medicion_semantica.sql, que este script aplica si falta) con una fila
por ORACIÓN de la narración normalizada (turnos 1..1400) de las 54 campañas, con su vector bge-m3 de
1024 dimensiones.

Solo ESCRIBE en medicion_oraciones. No toca turn_log, state_deltas, narrative_chunks ni ninguna tabla
del corpus. Reanuda: una campaña que ya tiene filas se salta (usa
--forzar para borrarlas y rehacerlas). Registra en docs/reportes/semantico/manifiesto_embeddings.json
el modelo, su commit exacto, la regla de división y, por campaña, el número de oraciones y el SHA-256
de su contenido (para comprobar después que otra corrida embebió exactamente los mismos textos).

Requisitos (una vez):   py -m pip install sentence-transformers huggingface_hub
La primera ejecución descarga BAAI/bge-m3 (~2.3 GB). En CPU tarda horas para el corpus completo:
conviene correr primero --solo-contar (no carga el modelo) y luego un par de prueba con --pares 07.

    $env:PYTHONUTF8="1"; py experimento/scripts/semantico/embeber_corpus.py --solo-contar
    $env:PYTHONUTF8="1"; py experimento/scripts/semantico/embeber_corpus.py --pares 07
    $env:PYTHONUTF8="1"; py experimento/scripts/semantico/embeber_corpus.py            # las 27 parejas
Para deshacer todo:  DROP TABLE medicion_oraciones;   (ningún otro script la usa)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comun as C                              # noqa: E402
import db as bd                                # noqa: E402  (motor/orquestador/db.py)
import pares as _pares                         # noqa: E402  (experimento/scripts/reporte_v2/pares.py -- las 27 parejas)
from normalizacion import normalizar_turno     # noqa: E402  (experimento/scripts/reporte_v2/normalizacion.py)

LOTE_INSERT = 1000


def oraciones_de_campana(camp, brazo):
    """[(turn_id, oración)] de la narración normalizada, turnos DESDE..HASTA, en orden."""
    out = []
    for t in camp.turnos_narracion():
        if C.DESDE <= t["turn_id"] <= C.HASTA:
            for o in C.dividir_oraciones(normalizar_turno(t["dm_output"], brazo)):
                out.append((int(t["turn_id"]), o))
    return out


def huella(filas):
    """SHA-256 del contenido a embeber de una campaña, para detectar si cambió desde que se embebió."""
    h = hashlib.sha256()
    for t, o in filas:
        h.update(f"{t}\t{o}\n".encode("utf-8"))
    return h.hexdigest()


def asegurar_tabla(camp):
    """Aplica motor/migrations/002_medicion_semantica.sql si la tabla todavía no existe (es idempotente)."""
    with camp._conn() as c:
        if c.execute("SELECT to_regclass(%s) AS t", (C.TABLA,)).fetchone()["t"] is None:
            c.execute(C.MIGRACION.read_text(encoding="utf-8"))
            print(f"Tabla {C.TABLA} creada ({C.MIGRACION.name})", flush=True)


def filas_existentes(camp):
    """Cuenta las filas de embeddings ya guardadas para la campaña."""
    with camp._conn() as c:
        camp._tx(c)
        return c.execute(f"SELECT count(*) AS n FROM {C.TABLA} WHERE campaign_id=%s", (camp.campaign_id,)).fetchone()["n"]


def borrar(camp):
    """Borra todos los embeddings de la campaña (para --forzar)."""
    with camp._conn() as c:
        camp._tx(c)
        c.execute(f"DELETE FROM {C.TABLA} WHERE campaign_id=%s", (camp.campaign_id,))


def numerar(filas):
    """(turn_id, oración) -> (turn_id, n_oracion, oración), con n_oracion = orden dentro del turno."""
    out, previo, k = [], None, 0
    for t, o in filas:
        k = k + 1 if t == previo else 0
        previo = t
        out.append((t, k, o))
    return out


def insertar(camp, filas, vectores, modelo):
    """Una transacción por campaña: o entran todas sus oraciones o ninguna (reanudación limpia)."""
    with camp._conn() as c:
        camp._tx(c)
        tenant = camp._tenant
        numeradas = numerar(filas)
        with c.cursor() as cur:
            for i in range(0, len(numeradas), LOTE_INSERT):
                cur.executemany(
                    f"INSERT INTO {C.TABLA} (tenant_id, campaign_id, turn_id, n_oracion, content, embedding, modelo) "
                    "VALUES (%s, %s, %s, %s, %s, %s::vector, %s)",
                    [(tenant, camp.campaign_id, t, k, o, C.vec_literal(v), modelo)
                     for (t, k, o), v in zip(numeradas[i:i + LOTE_INSERT], vectores[i:i + LOTE_INSERT])])


def leer_manifiesto():
    """Lee el manifiesto de embeddings; dict vacío si no existe."""
    if C.MANIFIESTO.exists():
        return json.loads(C.MANIFIESTO.read_text(encoding="utf-8"))
    return {}


def guardar_manifiesto(m):
    """Escribe el manifiesto con claves ordenadas, para que el archivo sea estable entre corridas."""
    C.SALIDA_DOCS.mkdir(parents=True, exist_ok=True)
    C.MANIFIESTO.write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def main(argv=None, embedder=None):
    """Embebe las oraciones de narración de las campañas y las guarda en pgvector, con un manifiesto que fija la revisión del modelo y la versión del divisor.

    Se niega a mezclar versiones del modelo o del divisor. --forzar rehace campañas ya embebidas; --solo-contar solo cuenta oraciones sin cargar el modelo.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--pares", help="lista separada por comas (p. ej. 07,08); por defecto las 27")
    ap.add_argument("--forzar", action="store_true", help="borra y rehace las campañas que ya tienen filas")
    ap.add_argument("--solo-contar", action="store_true", help="cuenta oraciones por campaña sin cargar el modelo ni escribir")
    ap.add_argument("--revision", help="commit de BAAI/bge-m3 (por defecto: el del manifiesto, o el actual la primera vez)")
    ap.add_argument("--dispositivo", default="cpu")
    ap.add_argument("--lote", type=int, default=64)
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    pares = _pares.todos()
    if a.pares:
        pedidos = {p.strip().zfill(2) for p in a.pares.split(",")}
        pares = [p for p in pares if p["par"] in pedidos]

    if a.solo_contar:
        total = 0
        for p in pares:
            for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
                n = len(oraciones_de_campana(bd.Campaña(p[k]), brazo))
                total += n
                print(f"Par{p['par']} {brazo}: {n} oraciones", flush=True)
        print(f"TOTAL {total} oraciones ({total * C.DIM * 4 / 1e9:.2f} GB de vectores en float32)")
        return

    man = leer_manifiesto()
    revision = a.revision or man.get("revision") or C.resolver_revision()
    if man.get("revision") and man["revision"] != revision:
        sys.exit(f"El manifiesto fija {C.MODELO}@{man['revision']}; pediste {revision}. No se mezclan versiones del modelo.")
    if man.get("divisor") and man["divisor"] != C.VERSION_DIVISOR:
        sys.exit(f"El manifiesto usa el divisor {man['divisor']} y el código {C.VERSION_DIVISOR}: hay que re-embeber todo (--forzar).")
    if embedder is None:
        try:
            import torch
            torch.set_num_threads(os.cpu_count() or 1)
        except ImportError:
            pass
        embedder = C.Embedder(revision=revision, dispositivo=a.dispositivo, lote=a.lote)
    man.update({"modelo": C.MODELO, "revision": revision, "dim": C.DIM, "divisor": C.VERSION_DIVISOR,
                "turnos": [C.DESDE, C.HASTA], "texto": "normalizar_turno(dm_output, brazo)", "tabla": C.TABLA})
    man.setdefault("campanas", {})
    if pares:
        asegurar_tabla(bd.Campaña(pares[0]["campaign_g1"]))

    for p in pares:
        for brazo, k in (("G1", "campaign_g1"), ("G2", "campaign_g2")):
            camp = bd.Campaña(p[k])
            etiqueta = f"Par{p['par']} {brazo}"
            ya = filas_existentes(camp)
            if ya and not a.forzar:
                print(f"{etiqueta}: ya tiene {ya} filas, se salta", flush=True)
                continue
            if ya:
                borrar(camp)
            filas = oraciones_de_campana(camp, brazo)
            t0 = time.time()
            vectores = embedder([o for _, o in filas])
            t1 = time.time()
            insertar(camp, filas, vectores, f"{C.MODELO}@{revision}")
            man["campanas"][p[k]] = {"par": p["par"], "brazo": brazo, "oraciones": len(filas), "sha256": huella(filas),
                                     "fecha": dt.datetime.now().isoformat(timespec="seconds")}
            guardar_manifiesto(man)
            print(f"{etiqueta}: {len(filas)} oraciones, embebidas en {t1 - t0:.0f} s, insertadas en {time.time() - t1:.0f} s", flush=True)
    print(f"Listo. Manifiesto: {C.MANIFIESTO}")


if __name__ == "__main__":
    main()
