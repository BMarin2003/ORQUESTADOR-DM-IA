"""Ronda A2 (solo pregunta A): inserta los 410 ítems A de items_final.json (400 de muestra + 10 controles),
la práctica guiada y la regla visible en plantilla_A2.html -> formulario_A2.html.
Los fragmentos de práctica son textos breves redactados por los autores (no provienen del corpus) y no se analizan.
    PYTHONUTF8=1 py validacion_v2/construir_formulario_A2.py
"""
import hashlib
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PREG = ("¿La narración del DM atribuye al personaje jugador, en segunda persona («tú») o por su nombre, "
        "una decisión, un pensamiento, una emoción o un acto de habla?")

PRACTICA = [
    {"id": "P1", "pj": "Kael", "accion": "Salto hacia la cornisa. {Atletismo}",
     "texto": "El cuerpo se impulsa hacia la cornisa y los dedos se aferran a la piedra húmeda justo antes de resbalar.",
     "esperada": "No", "razon": "Es una acción física y el resultado de la acción, narrado sin «tú» ni nombre. No hay decisión, pensamiento, emoción ni habla atribuida."},
    {"id": "P2", "pj": "Kael", "accion": "Decido esperar a que pase la patrulla.",
     "texto": "Decides esperar en la sombra mientras los pasos de la patrulla se alejan por el corredor.",
     "esperada": "Sí", "razon": "«Decides» atribuye una decisión en segunda persona. Cuenta aunque el jugador ya la haya declarado."},
    {"id": "P3", "pj": "Kael", "accion": "Examino las huellas del barro. {Investigación}",
     "texto": "Las huellas son recientes y desiguales; te das cuenta de que quien las dejó arrastraba una pierna.",
     "esperada": "Sí", "razon": "«Te das cuenta» atribuye un pensamiento en segunda persona. Cuenta aunque sea el resultado de una tirada."},
    {"id": "P4", "pj": "Kael", "accion": "Me asomo a la habitación. {Percepción}",
     "texto": "Ves una puerta entreabierta al fondo y oyes un goteo constante que viene del techo.",
     "esperada": "No", "razon": "Solo hay percepción («ves», «oyes»). La percepción no cuenta."},
    {"id": "P5", "pj": "Kael", "accion": "«¿Seguimos por el pasillo?»",
     "texto": "—¿Tú crees que esto es seguro? —pregunta la guardiana, sin apartar la vista del pasillo.",
     "esperada": "No", "razon": "El «tú» y el «crees» están dentro del diálogo de un PNJ. No es la narración atribuyendo algo al PJ."},
    {"id": "P6", "pj": "Kael", "accion": "«No vine a pelear», le digo al guardia. {Persuasión}",
     "texto": "Las palabras no logran convencer al guardia, que mantiene la lanza en alto y no se aparta de la puerta.",
     "esperada": "No", "razon": "El resultado de lo que dijo el jugador se narra sin «tú» ni nombre («las palabras no logran convencer»). La narración no le atribuye un acto de habla al PJ."},
    {"id": "P7", "pj": "Kael", "accion": "Le contesto que no tengo miedo.",
     "texto": "Respondes que no tienes miedo, aunque la voz te tiembla un poco al final.",
     "esperada": "Sí", "razon": "«Respondes» atribuye un acto de habla en segunda persona."},
    {"id": "P8", "pj": "Kael", "accion": "Miro la puerta del sótano.",
     "texto": "La puerta del sótano está atrancada desde dentro. Si decides forzarla, el ruido llegará hasta la taberna.",
     "esperada": "No", "razon": "«Si decides…» es un condicional: plantea una opción, no atribuye una decisión tomada."},
]

REGLA = """<h3>Regla de la pregunta A</h3>
<p><strong>Sí</strong>, solo si la narración atribuye al PJ, <strong>con «tú» o con su nombre</strong>:</p>
<ul><li>una <strong>decisión</strong> («decides», «optas»)</li><li>un <strong>pensamiento</strong> («crees», «recuerdas», «te das cuenta»)</li>
<li>una <strong>emoción</strong> nombrada («sientes miedo», «te invade la ira»)</li><li>un <strong>acto de habla</strong> («respondes», «murmuras», «pronuncias»)</li></ul>
<p>Cuenta aunque el jugador lo haya declarado y aunque venga tras una tirada.</p>
<p><strong>No</strong>, si lo único que hay es:</p>
<ul><li>percepción («ves», «oyes», «notas», «sientes frío»)</li><li>acción física o reflejo («te acercas», «tropiezas»)</li>
<li>el resultado narrado sin «tú» ni nombre («el salto alcanza la cornisa», «la vista recorre la sala», «las palabras no convencen»)</li>
<li>«tú» dentro del diálogo de un PNJ</li><li>preguntas, opciones o condicionales («si decides…»), futuro («recordarás»)</li>
<li>lo que piensan, sienten o dicen otros personajes</li></ul>"""


def main():
    items = [it for it in json.loads((AQUI / "items_final.json").read_text(encoding="utf-8")) if it["tipo"] == "persona2"]
    assert len(items) == 410, len(items)
    js = lambda x: json.dumps(x, ensure_ascii=False).replace("</", "<\\/")  # noqa: E731
    html = (AQUI / "plantilla_A2.html").read_text(encoding="utf-8")
    for marca, valor in (("__ITEMS__", js(items)), ("__PRACTICA__", js(PRACTICA)), ("__N__", str(len(items)))):
        assert html.count(marca) == 1, marca
        html = html.replace(marca, valor)
    html = html.replace("__PREG__", PREG).replace("__REGLA__", REGLA)
    assert not any(m in html for m in ("__PREG__", "__REGLA__", "__ITEMS__", "__PRACTICA__", "__N__"))
    out = AQUI / "formulario_A2.html"
    out.write_text(html, encoding="utf-8")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (AQUI / "formulario_A2.sha256").write_text(f"{h}  formulario_A2.html\n", encoding="utf-8")
    print("formulario_A2.html:", len(items), "ítems +", len(PRACTICA), "de práctica |", h)


if __name__ == "__main__":
    main()
