"""¿Reciben G1 y G2 de un mismo par la misma secuencia de tiradas?

La tesis (p153, p197, p262, p278, p438) lo afirma, y jugador/dados.py lo
justifica con "porque comparten campaign_id". Pero cada brazo tiene su propia
fila en `campaigns` (UUID distinto), y la semilla es sha256(campaign_id|turn|habilidad).

Prueba empírica, solo lectura: en los turnos donde ambos brazos tiraron la MISMA
habilidad en el MISMO turno, ¿coincide el d20 natural?
  - semilla compartida -> coincide ~100 %
  - semillas independientes -> coincide ~5 % (1/20)

    $env:PYTHONUTF8="1"; py scripts/verificacion/verificar_dados_pareados.py
"""
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LOGS = RAIZ / "logs"
RX_TURNO = re.compile(r"^## Turno (\d+)\b")
RX_TIRADA = re.compile(r"^\s{2}([^\s:][^:]{1,40}):\s*(\d{1,2})\s*[+-]\s*\d+\s*=\s*-?\d+")


def norm(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower())
                   if unicodedata.category(c) != "Mn").strip()


def tiradas(ruta):
    """{(turno, habilidad): primer d20 natural} a partir de la sección [3] DADOS."""
    out, turno, en_dados = {}, None, False
    with open(ruta, encoding="utf-8", errors="replace") as f:
        for linea in f:
            m = RX_TURNO.match(linea)
            if m:
                turno, en_dados = int(m.group(1)), False
                continue
            if linea.startswith("### "):
                en_dados = "DADOS" in linea
                continue
            if en_dados and turno is not None:
                t = RX_TIRADA.match(linea)
                if t:
                    clave = (turno, norm(t.group(1)))
                    out.setdefault(clave, int(t.group(2)))
    return out


def main():
    archivos = sorted(LOGS.rglob("*_bitacora_completa.md"))
    pares = {}
    for a in archivos:
        m = re.match(r"par(\d+)_(g[12])_", a.name)
        if m:
            pares.setdefault(int(m.group(1)), {})[m.group(2)] = a
    tot_comunes = tot_iguales = 0
    medias = []
    print("par | tiradas G1 | tiradas G2 | mismo turno+habilidad | d20 igual | %")
    for p in sorted(pares):
        if set(pares[p]) != {"g1", "g2"}:
            continue
        t1, t2 = tiradas(pares[p]["g1"]), tiradas(pares[p]["g2"])
        comunes = set(t1) & set(t2)
        iguales = sum(t1[k] == t2[k] for k in comunes)
        tot_comunes += len(comunes)
        tot_iguales += iguales
        pct = 100 * iguales / len(comunes) if comunes else float("nan")
        print(f"{p:02d} | {len(t1)} | {len(t2)} | {len(comunes)} | {iguales} | {pct:.1f}")
        medias.append((p, sum(t1.values()) / len(t1), sum(t2.values()) / len(t2)))
    pct = 100 * tot_iguales / tot_comunes if tot_comunes else float("nan")
    print(f"\nTOTAL: {tot_iguales}/{tot_comunes} = {pct:.1f} % (azar = 5.0 %, semilla compartida = 100 %)")

    # ¿La suerte favoreció sistemáticamente a un brazo? d20 natural medio por brazo y par.
    from scipy.stats import wilcoxon
    print("\npar | d20 medio G1 | d20 medio G2 | dif")
    for p, m1, m2 in medias:
        print(f"{p:02d} | {m1:.2f} | {m2:.2f} | {m1 - m2:+.2f}")
    difs = [m1 - m2 for _, m1, m2 in medias]
    g1_mayor = sum(d > 0 for d in difs)
    print(f"\nG1 con mejor suerte en {g1_mayor}/{len(difs)} pares; "
          f"media dif = {sum(difs) / len(difs):+.3f}; Wilcoxon bilateral p = {wilcoxon(difs).pvalue:.3f}")


if __name__ == "__main__":
    main()
