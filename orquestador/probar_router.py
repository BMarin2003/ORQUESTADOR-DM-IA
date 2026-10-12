r"""
Pruebas del Router — sin base de datos, sin red, sin costo.

router.py es una función pura a propósito: esto se puede correr en
cualquier máquina, en milisegundos, tantas veces como se quiera mientras
se ajusta el algoritmo.

Uso:
  py orquestador\probar_router.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "orquestador"))
from router import clasificar_turno  # noqa: E402

CASOS = [
    dict(
        nombre="corchetes → fuera_de_rol, pisa todo lo demás",
        args=dict(buffer='[¿cómo funciona la ventaja?] "Ordulf" atacar',
                   npcs_presentes=["Ordulf Bec"]),
        espera=dict(modo="fuera_de_rol", requiere_arbitro=True,
                    pnj_que_responden=[], altera_estado=False),
    ),
    dict(
        nombre="tirada + PNJ nombrado → en_rol, consecuente",
        args=dict(
            buffer='Le muestro el papeleo a Brea. Persuasión (resultado: 17 total)',
            npcs_presentes=["Sargento Brea"]),
        espera=dict(modo="en_rol", requiere_arbitro=True,
                    pnj_que_responden=["Sargento Brea"], altera_estado=True,
                    peso="consecuente"),
    ),
    dict(
        nombre="un solo PNJ presente, sin nombrarlo → responde igual",
        args=dict(buffer="Me acerco un poco más, como si fuéramos confidentes.",
                   npcs_presentes=["Sargento Brea"]),
        espera=dict(modo="en_rol", pnj_que_responden=["Sargento Brea"],
                    altera_estado=False),
    ),
    dict(
        nombre="varios PNJ, ninguno nombrado → responde el último que habló",
        args=dict(buffer="Sigo caminando sin decir nada.",
                   npcs_presentes=["Sargento Brea", "Ordulf Bec"],
                   ultimo_pnj_hablo="Ordulf Bec"),
        espera=dict(modo="en_rol", pnj_que_responden=["Ordulf Bec"]),
    ),
    dict(
        nombre="nada interpela, sin viñeta reciente → ambiental",
        args=dict(buffer="Miro el paisaje mientras caminamos.",
                   npcs_presentes=["Sargento Brea", "Ordulf Bec"],
                   ultimo_pnj_hablo=None, historial_modos=("en_rol", "en_rol")),
        espera=dict(modo="ambiental", requiere_arbitro=False,
                    pnj_que_responden=[]),
    ),
    dict(
        nombre="nada interpela, viñeta hace 1 turno → silencio (enfriamiento)",
        args=dict(buffer="Sigo caminando en silencio.",
                   npcs_presentes=["Sargento Brea", "Ordulf Bec"],
                   ultimo_pnj_hablo=None, historial_modos=("en_rol", "ambiental")),
        espera=dict(modo="silencio"),
    ),
    dict(
        nombre="verbo de intención sin tirada → altera_estado igual",
        args=dict(buffer="Le entrego el mapa a Brea sin decir nada.",
                   npcs_presentes=["Sargento Brea"]),
        espera=dict(modo="en_rol", altera_estado=True, requiere_arbitro=True),
    ),
    dict(
        nombre="pregunta sin PNJ nombrado ni tirada → sigue siendo en_rol",
        args=dict(buffer="¿Qué es ese olor?",
                   npcs_presentes=["Sargento Brea"]),
        espera=dict(modo="en_rol", pnj_que_responden=["Sargento Brea"]),
    ),
    dict(
        nombre="buffer corto, sin PNJ, sin tirada → trivial",
        args=dict(buffer="Asiento.", npcs_presentes=[]),
        espera=dict(peso="trivial"),
    ),
]


def main():
    """Corre CASOS contra `clasificar_turno` (router determinista, sin LLM); sale con código 1 si algún caso no coincide."""
    fallos = 0
    for i, caso in enumerate(CASOS, 1):
        resultado = clasificar_turno(**caso["args"])
        ok = all(resultado.get(k) == v for k, v in caso["espera"].items())
        marca = "✓" if ok else "✗"
        print(f"[{i}] {marca} {caso['nombre']}")
        if not ok:
            fallos += 1
            print(f"    esperado (parcial): {caso['espera']}")
            print(f"    obtenido:           {resultado}")

    print(f"\n{len(CASOS) - fallos}/{len(CASOS)} casos correctos")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
