r"""
VERTICAL SLICE — un turno completo, de punta a punta.

Conecta por primera vez las piezas que hasta ahora solo se probaron aisladas:

    estado (Postgres)
      → contexto de escena
        → JUGADOR agéntico          Hermes-3
          → dados deterministas
            → DM                    Gemma 4 31B
              → EXTRACTOR           Gemma 4 31B
                → apply_delta
                  → estado nuevo

Cada paso verifica lo que produce antes de pasar al siguiente. Es donde
salen los bugs de integración: en esta sesión, seis fallos silenciosos solo
aparecieron ejecutando, y el primero de este script fue que `SET LOCAL` no
admite parámetros en Postgres.

Uso:
  py orquestador\vertical_slice.py
  py orquestador\vertical_slice.py --turnos 3
  py orquestador\vertical_slice.py --pj PJ18 --seco     (sin escribir en la base)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "jugador"))
sys.path.insert(0, str(RAIZ / "orquestador"))
import dados          # noqa: E402
import db as bd       # noqa: E402

BASE = "https://api.deepinfra.com/v1/openai"
MODELO_DM = os.environ.get("DMIA_MODELO", "google/gemma-4-31B-it")
MODELO_JUGADOR = os.environ.get("DMIA_MODELO_JUGADOR",
                                "NousResearch/Hermes-3-Llama-3.1-70B")

PENSAMIENTO = re.compile(r"<think>.*?</think>", re.S | re.I)
VALLA = re.compile(r"^\s*```[a-z]*\s*$", re.M)


def llamar(modelo, system, user, max_tokens=600, temp=0.8, json_mode=False):
    key = os.environ.get("DEEPINFRA_API_KEY")
    cuerpo = {"model": modelo,
              "messages": [{"role": "system", "content": system},
                           {"role": "user", "content": user}],
              "temperature": temp, "max_tokens": max_tokens,
              "chat_template_kwargs": {"enable_thinking": False}}
    if json_mode:
        cuerpo["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        det = e.read().decode()[:200]
        if any(k in det for k in ("chat_template_kwargs", "response_format")) or e.code == 422:
            cuerpo.pop("chat_template_kwargs", None)
            cuerpo.pop("response_format", None)
            req = urllib.request.Request(
                f"{BASE}/chat/completions", data=json.dumps(cuerpo).encode(),
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read().decode())
        else:
            print(f"    HTTP {e.code}: {det}", file=sys.stderr)
            return None
    txt = VALLA.sub("", PENSAMIENTO.sub("", d["choices"][0]["message"]["content"] or "")).strip()
    u = d.get("usage", {})
    return {"texto": txt, "tin": u.get("prompt_tokens") or 0,
            "tout": u.get("completion_tokens") or 0,
            "ms": round((time.time() - t0) * 1000)}


def parsear_json(texto):
    limpio = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    try:
        return json.loads(limpio)
    except Exception:
        m = re.search(r"\{.*\}", limpio, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None


def paso(n, titulo):
    print(f"\n{'─'*74}\n[{n}] {titulo}\n{'─'*74}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pj", default="PJ02")
    ap.add_argument("--turnos", type=int, default=1)
    ap.add_argument("--seco", action="store_true",
                    help="no escribe en la base; solo muestra qué haría")
    args = ap.parse_args()

    # Comprobar TODO lo necesario antes de gastar una sola llamada. La
    # primera versión descubría que DMIA_MODELO estaba vacío en el paso 4,
    # después de pagar el jugador y los dados.
    faltan = [v for v in ("DEEPINFRA_API_KEY", "DMIA_MODELO") if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Falta en el entorno: {', '.join(faltan)}\n"
                 f"  DEEPINFRA_API_KEY  la clave de la API\n"
                 f"  DMIA_MODELO        p.ej. google/gemma-4-31B-it\n"
                 f"Carga el .env y comprueba que las variables tienen valor.")
    for nombre, ruta in (("prompt del jugador", RAIZ / "jugador" / "prompt.md"),
                         ("prompt de G2", RAIZ / "dm" / "prompt_g2.md"),
                         ("prompt del extractor", RAIZ / "extractor" / "prompt.md"),
                         ("contrato", RAIZ / "extractor" / "contrato.json"),
                         ("personajes", RAIZ / "jugador" / "personajes_jugadores.json")):
        if not ruta.exists():
            sys.exit(f"No encuentro el {nombre}: {ruta}")

    # ------------------------------------------------------------ 0. estado
    import psycopg
    with psycopg.connect(bd.DSN) as c:
        r = c.execute("SELECT id, title FROM campaigns ORDER BY created_at LIMIT 1").fetchone()
    if not r:
        sys.exit("No hay campañas en la base. Carga fixtures/seed.sql")
    camp = bd.Campaña(r[0])
    cab = camp.cabecera()

    pjs = json.loads((RAIZ / "jugador" / "personajes_jugadores.json")
                     .read_text(encoding="utf-8"))["personajes"]
    pj = next(p for p in pjs if p["id"] == args.pj)

    prompt_jugador = (RAIZ / "jugador" / "prompt.md").read_text(encoding="utf-8")
    prompt_dm = (RAIZ / "dm" / "prompt_g2.md").read_text(encoding="utf-8")
    prompt_extractor = (RAIZ / "extractor" / "prompt.md").read_text(encoding="utf-8")
    contrato = json.loads((RAIZ / "extractor" / "contrato.json")
                          .read_text(encoding="utf-8"))

    print(f"\n{'='*74}\nVERTICAL SLICE · {cab['title']} · {cab['architecture']}")
    print(f"  DM      {MODELO_DM}")
    print(f"  jugador {MODELO_JUGADOR}  ({pj['nombre']}, desvío {pj['desvio']})")
    print(f"  turno   {cab['current_turn'] + 1}"
          + ("   [SECO — no se escribe nada]" if args.seco else ""))
    print("=" * 74)

    presentes = ["Sargento Brea"]
    coste = {"tin": 0, "tout": 0}

    for i in range(args.turnos):
        turn_id = cab["current_turn"] + 1 + i

        # ------------------------------------------------- 1. estado y escena
        paso(1, "ESTADO Y CONTEXTO (desde Postgres)")
        # game_day se refresca cada turno -- antes `cab` se leía una sola
        # vez fuera del bucle y quedaba desactualizado si un turno movía
        # el día de juego (nunca pasaba porque ese camino estaba roto,
        # ver el fix del paso 8; ahora que funciona, sí puede cambiar).
        cab["game_day"] = camp.cabecera()["game_day"]
        antes = camp.estado_pnj(presentes[0])
        print(f"  {antes['name']}: {antes['status']}, aprecio {antes['affinity']} "
              f"({antes['banda']}), {antes['hechos']} hechos conocidos")
        # MUN-1/2 compartido (ver db.eventos_reloj_turno): lo que un reloj
        # disparó el turno anterior se narra AHORA, al abrir este turno.
        eventos_reloj = camp.eventos_reloj_turno(turn_id - 1) if turn_id > 1 else []
        ctx = camp.contexto_escena(presentes, eventos_reloj)
        ents = camp.entidades()
        print(f"  {len(ents)} entidades · contexto de {len(ctx)} caracteres")

        ultimo = camp.escena_actual()
        escena = (ultimo["dm_output"] if ultimo else
                  "Estás en la cabecera del puente de Vado de Ceniza. La Sargento "
                  "Brea revisa el paso de un carro cargado de sacos. Al verte, "
                  "levanta la vista y espera a que digas algo.")

        # ------------------------------------------------------- 2. jugador
        paso(2, f"JUGADOR — {pj['nombre']}")
        ficha = ficha_jugador(pj)
        r = llamar(MODELO_JUGADOR, prompt_jugador,
                   f"{ficha}\n\nEL DM ACABA DE DECIR\n{escena}\n\n¿Qué haces?",
                   max_tokens=300)
        if not r:
            sys.exit("El jugador no respondió")
        coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
        accion = r["texto"]
        print(f"  {r['ms']} ms\n")
        for l in accion.splitlines():
            if l.strip():
                print(f"    {l}")

        # --------------------------------------------------------- 3. dados
        paso(3, "DADOS (deterministas, del sistema)")
        buffer_txt, tiradas, rechazadas = dados.resolver_turno(
            accion, str(camp.campaign_id), turn_id)
        if not tiradas and not rechazadas:
            print("  sin tiradas declaradas")
        for t in tiradas:
            print(f"  {t['etiqueta']}: {t['dado']}+{t['modificador']}={t['total']}"
                  + ("  CRÍTICO" if t["critico"] else "  PIFIA" if t["pifia"] else ""))
        for h in rechazadas:
            print(f"  {h}: NO EXISTE — no se tira")

        # ------------------------------------------------------------ 4. DM
        paso(4, "DM")
        cb = cab.get("content_boundaries") or {}
        rojas = cb.get("hard_lines") or []
        velos = cb.get("veils") or []
        limites = ("\nLÍMITES DE CONTENIDO\n"
                   + f"  líneas rojas (NUNCA aparecen): {', '.join(rojas) if rojas else 'ninguna declarada'}\n"
                   + f"  velos (se cortan en negro): {', '.join(velos) if velos else 'ninguno'}\n"
                   + "  No escales el material más allá de lo que el estado describe.\n"
                   + "  Si la base dice 'desalojo de puestos', es un desalojo de\n"
                   + "  puestos: no lo conviertas en algo peor.\n")
        user_dm = (f"CONFIGURACIÓN\n  tono: {cab['world_tone']} · registro: "
                   f"{cab['party_register']} · visibilidad de reglas: "
                   f"{cab['rules_visibility']}\n{limites}{ctx}\n"
                   f"ESCENA ACTUAL\n{escena}\n\n"
                   f"TURNO DEL JUGADOR\n{buffer_txt}")
        r = llamar(MODELO_DM, prompt_dm, user_dm, max_tokens=500, temp=0.8)
        if not r:
            sys.exit("El DM no respondió")
        coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
        narracion = r["texto"]
        print(f"  {r['ms']} ms\n")
        for l in narracion.splitlines():
            if l.strip():
                print(f"    {l}")

        # ---------------------------------------------------- 5. verificación
        paso(5, "VERIFICACIÓN DE LA NARRACIÓN")
        problemas = []
        # El DM metió "[Tirada de Percepción necesaria... resuelvo la
        # reacción de la PNJ]" pese a tenerlo prohibido. El verificador
        # anterior no lo veía.
        if re.search(r"\[[^\]]{20,}\]", narracion):
            problemas.append("meta-comentario entre corchetes")
        if re.search(r"\b(tirada de \w+ necesaria|resuelvo la|como DM|"
                     r"seg[úu]n las reglas|no obstante,? al haber)\b",
                     narracion, re.I):
            problemas.append("comenta sus propias reglas")
        for t in tiradas:
            if t["pifia"] and re.search(r"\b(logras|consigues|aciertas|lo convences)\b",
                                        narracion, re.I):
                problemas.append(f"pifia en {t['etiqueta']} pero narra éxito")
        if re.search(rf"\b{re.escape(pj['nombre'])}\s+(piensa|siente|decide|comprende)",
                     narracion, re.I):
            problemas.append("narra pensamientos del PJ (viola la regla de oro)")
        print("  " + ("\n  ".join(f"⚠ {p}" for p in problemas)
                      if problemas else "sin problemas detectados"))

        # ---------------------------------------------------- 6. extractor
        paso(6, "EXTRACTOR")
        lista = "\n".join(f"  {e['nombre']:26s} {e['tipo']}" for e in ents)
        user_ex = (f"ENTIDADES EXISTENTES\n{lista}\n{ctx}\n"
                   f"TURNO\n{pj['nombre']}: {accion}\nDM: {narracion}")
        r = llamar(MODELO_DM, prompt_extractor, user_ex,
                   max_tokens=800, temp=0, json_mode=True)
        if not r:
            sys.exit("El extractor no respondió")
        coste["tin"] += r["tin"]; coste["tout"] += r["tout"]
        salida = parsear_json(r["texto"]) or {"events": [], "deltas": []}
        eventos = salida.get("events") or []
        deltas = salida.get("deltas") or []
        creaciones = salida.get("creaciones") or []
        print(f"  {r['ms']} ms · {len(eventos)} eventos · {len(deltas)} deltas"
              f" · {len(creaciones)} creaciones")

        # ------------------------------------------- 7. validar antes de escribir
        paso(7, "VALIDACIÓN DE LO EXTRAÍDO")
        completo = f"{accion} {narracion}"
        validos_ev, validos_d = [], []
        for e in eventos:
            ev = e.get("evidence", "") or ""
            if e.get("event_kind") not in contrato["event_kinds"]:
                print(f"  ✗ event_kind desconocido: {e.get('event_kind')}")
            elif ev not in completo:
                print(f"  ✗ evidencia no literal: «{ev[:50]}»")
            else:
                validos_ev.append(e)
                print(f"  ✓ evento {e['entity']} · {e['event_kind']}")
        for d in deltas:
            ev = d.get("evidence", "") or ""
            campos = contrato["campos_directos"].get(d.get("entity_type"), {})
            if d.get("field") not in campos:
                print(f"  ✗ campo fuera de lista blanca: "
                      f"{d.get('entity_type')}.{d.get('field')}")
            elif ev not in completo:
                print(f"  ✗ evidencia no literal: «{ev[:50]}»")
            else:
                validos_d.append(d)
                print(f"  ✓ delta {d['entity']} · {d['entity_type']}.{d['field']}"
                      f" = {d.get('value')}")
        CREABLES = {"npc", "location", "item", "faction", "quest"}
        GENERICOS = re.compile(r"^\s*(?:el|la|los|las|un|una|unos|unas)\s+\w+\s*$", re.I)
        validos_c = []
        for cr in creaciones:
            ev = cr.get("evidence", "") or ""
            nom = (cr.get("name") or "").strip()
            if cr.get("entity_type") not in CREABLES:
                print(f"  ✗ tipo no creable: {cr.get('entity_type')}")
            elif len(nom) < 3 or GENERICOS.match(nom):
                print(f"  ✗ nombre genérico, es atrezzo: «{nom}»")
            elif ev not in completo:
                print(f"  ✗ evidencia no literal: «{ev[:50]}»")
            elif len(validos_c) >= 1:
                print(f"  ✗ tope de 1 creación por turno, descartada: «{nom}»")
            else:
                validos_c.append(cr)
                print(f"  ✓ creación {cr['entity_type']}: {nom}")

        if not validos_ev and not validos_d and not validos_c:
            print("  nada que escribir (correcto si el turno no cambió el mundo)")

        # -------------------------------------------------------- 8. escribir
        paso(8, "ESCRITURA" + ("  [SECO — omitida]" if args.seco else ""))
        if not args.seco:
            camp.registrar_turno(turn_id, [{"pc": pj["id"], "text": accion}],
                                 narracion,
                                 bool(validos_ev or validos_d or validos_c))
            # Las creaciones van PRIMERO: un delta puede referirse a algo
            # que este mismo turno acaba de introducir.
            for cr in validos_c:
                padre = (camp.id_de("location", cr["dentro_de"])
                         if cr.get("dentro_de") else None)
                res = camp.crear(cr["entity_type"], cr["name"], turn_id,
                                 cr["evidence"], padre, None,
                                 cr.get("descripcion"))
                print(f"  → {res['motivo']}: {cr['entity_type']} {cr['name']}")
            for e in validos_ev:
                nid = camp.id_de("npc", e["entity"])
                if not nid:
                    print(f"  ✗ PNJ inexistente: {e['entity']}")
                    continue
                res = camp.resolver_evento(nid, e["event_kind"])
                if not res:
                    print(f"  ✗ evento sin magnitud: {e['event_kind']}")
                    continue
                nuevo = float(antes["affinity"] or 0) + float(res["d_affinity"])
                did = camp.aplicar("npc", nid, "affinity", nuevo, turn_id,
                                   "extracted", e["evidence"])
                print(f"  → delta {did}: {e['entity']} affinity "
                      f"{antes['affinity']} → {nuevo:.1f}  ({res['band']})")
                print(f"     {res['outcome'][:66]}")
            dias_transcurridos = 0
            for d in validos_d:
                # "world" no es una fila (id_de() no lo mapea a ninguna
                # tabla -- game_day vive en `campaigns`, apply_delta ya
                # lo sabe y no necesita entity_id). Llamar a id_de() con
                # "world" antes de este chequeo reventaba con KeyError;
                # nunca se disparó porque el extractor nunca había
                # emitido este delta todavía, pero el camino estaba roto.
                if d["entity_type"] == "world":
                    eid = None
                else:
                    eid = camp.id_de(d["entity_type"], d["entity"])
                    if not eid:
                        print(f"  ✗ entidad inexistente: {d['entity']}")
                        continue
                did = camp.aplicar(d["entity_type"], eid, d["field"],
                                   d["value"], turn_id, "extracted", d["evidence"])
                v = str(d["value"])
                print(f"  → delta {did}: {d['entity']}.{d['field']} = "
                      f"{v[:56]}{'…' if len(v) > 56 else ''}")
                if d.get("witnessed") and d["field"] == "status":
                    for p in camp.propagar("npc", eid, d["field"], d["value"],
                                           turn_id, True):
                        print(f"  → propagado a {p['faction_name']}: {p['motivo']}")
                if d["entity_type"] == "world" and d["field"] == "game_day":
                    dias_transcurridos = int(d["value"]) - int(cab["game_day"])

            # MUN-1/2, compartido con G1 (ver db.avanzar_relojes): si el
            # extractor marcó que pasaron días de juego, los relojes de
            # facción avanzan aquí mismo -- aritmética, no juicio del DM.
            # Lo que dispare se narra en el turno SIGUIENTE (paso 1 de la
            # próxima iteración lo recoge vía eventos_reloj_turno()).
            if dias_transcurridos > 0:
                # avanzar_relojes() devuelve columnas crudas de
                # advance_clocks() (clock_id, faction_id, agenda, event) --
                # sin el nombre de la facción, a diferencia de
                # eventos_reloj_turno() que sí hace el JOIN. No hace
                # falta el nombre aquí, solo confirmar qué disparó.
                disparados = camp.avanzar_relojes(dias_transcurridos, turn_id)
                for ev in disparados:
                    print(f"  ⏰ reloj disparado: agenda «{ev['agenda']}» "
                          f"(facción {ev['faction_id']})")
        else:
            print("  (nada escrito)")

        # ------------------------------------------------------ 9. comprobar
        paso(9, "ESTADO DESPUÉS")
        despues = camp.estado_pnj(presentes[0])
        cambio = (antes["affinity"] != despues["affinity"]
                  or antes["status"] != despues["status"]
                  or antes["hechos"] != despues["hechos"])
        print(f"  {despues['name']}: {despues['status']}, aprecio "
              f"{despues['affinity']} ({despues['banda']}), "
              f"{despues['hechos']} hechos, "
              f"{despues['secretos_revelados']} secretos revelados")
        print(f"  {'ESTADO MODIFICADO' if cambio else 'sin cambios de estado'}")
        cab["current_turn"] = turn_id

    print(f"\n{'='*74}")
    print(f"  {coste['tin']}→{coste['tout']} tokens · "
          f"${(coste['tin']*0.09 + coste['tout']*0.34)/1e6:.4f}")


def ficha_jugador(pj):
    p = pj["personalidad"]
    def b(v, neg, pos):
        return neg if v < -40 else pos if v > 40 else "equilibrado"
    def bd_(v):
        if v <= 30:
            return ("Si el DM plantea algo urgente, VAS. Atiendes primero lo "
                    "que se te pide.")
        if v <= 60:
            return "Atiendes lo urgente, pero te tomas un momento para lo tuyo."
        return "Lo urgente del DM es una opción más. Lo tuyo va primero."
    t = f"""TU FICHA
  {pj['nombre']}, {pj['arquetipo'].lower()}. {pj['clase']} nivel {pj['nivel']}.
    trato        {b(p['warmth'], 'frío y calculador', 'cálido y afectuoso')}
    franqueza    {b(p['candor'], 'disimulado', 'franco')}
    principios   {b(p['principle'], 'pragmático', 'principista')}
    temple       {b(p['boldness'], 'cauto', 'audaz')}

TUS OBJETIVOS PROPIOS
""" + "\n".join(f"  - {o}" for o in pj["agenda"]) + f"""

CÓMO TE TOMAS LO QUE EL DM PLANTEA
  {bd_(pj['desvio'])}
"""
    ej = pj.get("ejemplares")
    if ej:
        t += f"""
ASÍ JUEGAS TÚ
  Cuando te piden algo urgente:   {ej['urgente']}
  Cuando ves algo tuyo:           {ej['propio']}
  Cuando no pasa nada:            {ej['vacia']}
"""
    return t


if __name__ == "__main__":
    main()