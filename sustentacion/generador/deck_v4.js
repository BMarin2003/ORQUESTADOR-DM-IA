// Deck de sustentación v4: enfoque en metodología y sistema, con analogías cotidianas
// para un jurado ajeno a D&D. Reutiliza tema, utilidades y respaldo de deck.js.
// Uso: igual que deck.js, pero con sustentacion/generador/deck_v4.js
const path = require("path");
const D = require("./deck.js");
const { pres, THEME, X, INK, G1, G2, HOT, MUTED, LINE, SOFT, G1T, G2T, HOTT, W, T, box, label, arrow, chip, content, stat, iconDot, motifG1, motifG2, gridHip } = D;

const OUT = path.join(__dirname, "..", "propuestas", "Sustentacion_v4.pptx");
const HF = THEME.headFontFace;
const small = (s, text, y, o = {}) => T(s, text, { x: 0.6, y, w: 12.1, h: 0.35, fontSize: 12, color: MUTED, ...o });
const kick = (s, text, x, y, w, color = X.accent4) => T(s, text.toUpperCase(), { x, y, w, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color });
// Franja de analogía: siempre igual, para que el jurado la reconozca
async function analogia(s, text, y = 6.2) {
  box(s, 0.6, y, 12.1, 0.62, { fill: SOFT, line: SOFT });
  await iconDot(s, "FaLightbulb", 0.75, y + 0.11, 0.4, "FFFFFF", X.dk1);
  T(s, text, { x: 1.3, y, w: 11.2, h: 0.62, valign: "middle", fontSize: 14, italic: true });
}

pres.addSection({ title: "Exposición" });

// 1 · Portada
function v01() {
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Exposición" });
  T(s, "SUSTENTACIÓN DE TESIS", { x: 0.7, y: 0.6, w: 7.5, h: 0.35, fontSize: 12, bold: true, charSpacing: 3, color: X.accent4 });
  T(s, "Comparación de la coherencia narrativa en campañas de Dungeons & Dragons generadas por sistemas multiagente versus sistemas monolíticos", {
    x: 0.7, y: 1.2, w: 7.6, h: 2.9, fontFace: HF, fontSize: 32, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.05 });
  T(s, [
    { text: "Marin Yupanqui, Bryan Arturo", options: { breakLine: true } },
    { text: "Mostacero Cieza, Luis David", options: { breakLine: true } },
    { text: "Asesor: Dr. Cueva Chávez, Walter Manuel", options: { color: X.accent4 } },
  ], { x: 0.7, y: 4.55, w: 7.5, h: 1.2, color: "FFFFFF", paraSpaceAfter: 4 });
  T(s, "Universidad Privada Antenor Orrego · Escuela de Ingeniería de Sistemas e Inteligencia Artificial · Trujillo, 2026", { x: 0.7, y: 6.55, w: 11.9, h: 0.35, fontSize: 11, color: X.accent4 });
  motifG1(s, 9.05, 1.75, 1.9, G1); motifG2(s, 9.6, 4.45, 0.8, G2);
  T(s, "G1 · multiagente", { x: 8.6, y: 3.95, w: 2.8, h: 0.35, align: "center", fontSize: 12, color: G1, bold: true });
  T(s, "G2 · monolítico", { x: 8.6, y: 5.4, w: 2.8, h: 0.35, align: "center", fontSize: 12, color: G2, bold: true });
  s.addNotes("[0:00–0:30] Buenos días, señores miembros del jurado. Somos Bryan Marin y Luis Mostacero, y presentamos nuestra tesis, asesorada por el Dr. Walter Cueva. Comparamos dos formas de construir un narrador artificial para historias interactivas: un sistema que reparte el trabajo entre varios agentes, G1, y uno que lo hace todo en una sola llamada, G2. En toda la exposición, el verde azulado es G1 y el ocre es G2.");
}

// 2 · Qué es: narrativa interactiva en segunda persona
async function v02() {
  const s = content("EL ESCENARIO", "Una historia interactiva: tú decides, el sistema narra");
  // intercambio tipo chat
  box(s, 0.6, 1.75, 6.6, 4.2, { fill: SOFT, line: SOFT });
  // turno real: par 05 (Vado Cabrero), G2, turno 334 — texto abreviado con «…»
  kick(s, "Un turno real · par 05, G2, turno 334", 0.95, 1.95, 6);
  box(s, 1.9, 2.35, 5.0, 1.2, { fill: X.dk1, line: X.dk1 });
  T(s, [{ text: "Jugador\n", options: { bold: true, fontSize: 11, color: X.accent4 } }, { text: "«No te despiertes ahora…» Me deslizo muy despacio hacia adelante para intentar obtener un mejor ángulo de visión sin hacer ruido. " }, { text: "{Sigilo}", options: { bold: true, color: "F0B35A" } }],
    { x: 2.1, y: 2.4, w: 4.65, h: 1.1, fontSize: 13, color: "FFFFFF" });
  box(s, 0.9, 3.7, 5.4, 1.55, { fill: "FFFFFF", line: LINE });
  T(s, [{ text: "Narrador (IA)\n", options: { bold: true, fontSize: 11, color: X.accent4 } }, { text: "Un pequeño fragmento de piedra suelta cede bajo tu bota con un chasquido seco… La silueta masiva se tensa bruscamente… su cabeza gira con un movimiento espasmódico hacia tu dirección." }],
    { x: 1.1, y: 3.75, w: 5.0, h: 1.45, fontSize: 13 });
  T(s, [{ text: "{Sigilo}", options: { bold: true, color: G2 } }, { text: " = habilidad declarada: el código tira el dado y el narrador cuenta el resultado.  × 1,400 turnos por historia", options: { color: MUTED } }],
    { x: 0.95, y: 5.38, w: 6.1, h: 0.5, fontSize: 11 });
  // glosario mínimo
  const G = [
    ["FaDiceD20", "Dungeons & Dragons", "juego de rol de mesa: un narrador cuenta la historia y el jugador decide qué hace su personaje"],
    ["FaUserTie", "Director de juego (DM)", "el narrador: describe el mundo, da voz a los personajes y aplica las reglas"],
    ["FaUsers", "PNJ", "personajes no jugadores: todos los que controla el narrador"],
    ["FaCommentDots", "Segunda persona", "la narración se dirige a ti: «entras…», «te mira…»"],
  ];
  for (let i = 0; i < G.length; i++) {
    const y = 1.75 + i * 1.07;
    await iconDot(s, G[i][0], 7.6, y, 0.6, "FFFFFF", X.dk1);
    T(s, G[i][1], { x: 8.4, y: y - 0.04, w: 4.3, h: 0.35, fontSize: 16, bold: true });
    T(s, G[i][2], { x: 8.4, y: y + 0.32, w: 4.3, h: 0.65, fontSize: 12, color: MUTED });
  }
  await analogia(s, "Como un «elige tu propia aventura» sin páginas fijas: la historia se escribe en el momento, según lo que decides.");
  s.addNotes("[0:30–1:30] Primero, el escenario, porque es un campo de nicho. Dungeons & Dragons es un juego de rol de mesa: un narrador, el director de juego, cuenta la historia, da voz a todos los demás personajes y aplica las reglas; el jugador solo decide qué hace su personaje. Funciona por turnos, y este es un turno real de nuestro corpus: el jugador dice qué hace y qué habilidad usa, aquí sigilo; el código tira el dado, la tirada sale mal, y el narrador cuenta la consecuencia en segunda persona: la piedra cruje y la criatura despierta. Es como un libro de elige tu propia aventura, pero sin páginas fijas. En nuestra tesis el narrador es una inteligencia artificial, y cada historia dura 1,400 turnos.");
}

// 3 · El problema
async function v03() {
  const s = content("EL PROBLEMA", "En historias largas, el narrador artificial pierde el hilo");
  const cards = [
    ["FaHourglassHalf", "Olvida", "Como un mesero que a la hora ya no recuerda tu pedido.", "Lo que pasó hace 300 turnos ya no existe.", false],
    ["FaFilm", "Contradice", "Como el error de continuidad de una serie: el personaje que murió vuelve a aparecer.", "El mundo cambia sin razón.", false],
    // turno real: par 10, G2, turno 426 (ítem C790084), marcado «sí» por el evaluador externo de referencia
    ["FaUserSlash", "Decide por ti", "Tú: «Sostengo la mirada de Elian, buscando cualquier señal de debilidad».\nNarrador: «…interpretas su silencio […] como un signo de nerviosismo y debilidad».", "Turno real (par 10, G2, turno 426), confirmado por el evaluador externo.", true],
  ];
  for (let i = 0; i < 3; i++) {
    const [ic, head, ex, sub, hot] = cards[i];
    const x = 0.6 + i * 4.1;
    box(s, x, 1.75, 3.8, 4.15, { fill: hot ? HOTT : SOFT, line: hot ? HOTT : SOFT });
    await iconDot(s, ic, x + 0.35, 2.05, 0.85, "FFFFFF", hot ? HOT : X.dk1);
    T(s, head, { x: x + 0.35, y: 3.1, w: 3.1, h: 0.55, fontFace: HF, fontSize: 24, bold: true, color: hot ? HOT : X.dk1 });
    T(s, ex, { x: x + 0.35, y: 3.7, w: 3.2, h: 1.75, fontSize: 13, italic: true });
    T(s, sub, { x: x + 0.35, y: 5.35, w: 3.15, h: 0.5, fontSize: 12, color: MUTED });
  }
  small(s, "La literatura lo reporta en modelos de lenguaje como narradores (Callison-Burch et al., 2022; Gallotta et al., 2024). Olvidar y contradecir se muestran con analogías.", 6.2);
  s.addNotes("[1:30–2:20] Cuando un modelo de lenguaje narra durante cientos de turnos aparecen tres fallas, que la literatura ya reporta. Olvida, como un mesero que a la hora ya no recuerda tu pedido. Contradice, como el error de continuidad de una serie en el que un personaje muerto vuelve a aparecer. Y la más grave en un juego: decide por el jugador. Este es un turno real de nuestro corpus: el jugador solo dijo que observaba a Elian buscando debilidad, y el narrador decidió por él qué concluye: le dictó que interpreta el silencio como nerviosismo. Un evaluador externo lo confirmó como usurpación. A esto lo llamamos usurpar la agencia del jugador: el sistema decide, piensa, siente o habla por él.");
}

// 4 · La pregunta: ¿un cocinero o una brigada?
async function v04() {
  const s = content("PREGUNTA DE INVESTIGACIÓN", "¿Un solo cocinero o una brigada de cocina?");
  // G2
  box(s, 0.6, 1.7, 5.4, 2.0, { fill: G2T, line: G2T });
  motifG2(s, 0.95, 2.25, 0.85, G2, G2T);
  T(s, "G2 · monolítico", { x: 2.1, y: 1.95, w: 3.7, h: 0.4, fontSize: 17, bold: true, color: G2 });
  T(s, "Un solo cocinero toma el pedido, cocina, aplica las reglas y sirve: una sola llamada al modelo por turno.", { x: 2.1, y: 2.4, w: 3.7, h: 1.2, fontSize: 13 });
  // G1
  box(s, 0.6, 3.9, 5.4, 2.0, { fill: G1T, line: G1T });
  motifG1(s, 0.85, 4.45, 0.9, G1, G1T);
  T(s, "G1 · multiagente", { x: 2.1, y: 4.15, w: 3.7, h: 0.4, fontSize: 17, bold: true, color: G1 });
  T(s, "Una brigada: cada puesto hace una sola tarea y ve solo lo que necesita.", { x: 2.1, y: 4.6, w: 3.7, h: 1.2, fontSize: 13 });
  // hipótesis en lenguaje llano
  const cols = [["", "Responde", "¿a lo que acabas de hacer?"], ["", "Recuerda", "¿personajes y hechos previos?"], ["", "Respeta", "¿te deja decidir a ti?"]];
  const rows = [["¿El cocinero solo empeora con las horas?", ["H1a", "H1b", "H1c"]], ["¿La brigada lo hace mejor?", ["H1d", "H1e", "H1f"]]];
  gridHipMini(s, 6.4, 1.7, cols, rows);
  T(s, [{ text: "Hipótesis general: ", options: { bold: true } }, { text: "la brigada es más coherente solo si gana en las tres (H1d, H1e y H1f)." }], { x: 6.4, y: 5.2, w: 6.3, h: 0.7, fontSize: 14 });
  await analogia(s, "La analogía es solo para orientar: en el sistema real, «cocinar» es generar el texto del turno.");
  s.addNotes("[2:20–3:10] La literatura propone repartir el trabajo entre agentes especializados, pero no encontramos una comparación controlada en este tipo de juego, y menos en español y en segunda persona. Piensen en una cocina. G2 es un solo cocinero que toma el pedido, cocina, aplica las reglas y sirve. G1 es una brigada: cada puesto hace una tarea y ve solo lo que necesita. Medimos tres cosas: si el narrador responde a lo que el jugador acaba de hacer, si recuerda lo que pasó y si respeta sus decisiones. Para cada una hacemos dos preguntas: si el cocinero solo empeora con las horas, H1a a H1c, y si la brigada lo hace mejor, H1d a H1f. La hipótesis general solo se sostiene si la brigada gana en las tres.");
}
function gridHipMini(s, x0, y0, cols, rows) {
  const lw = 2.0, cw = 1.35, gap = 0.1, rh = 1.15;
  cols.forEach(([, name, q], j) => T(s, [{ text: name, options: { bold: true, breakLine: true } }, { text: q, options: { fontSize: 11, color: MUTED } }],
    { x: x0 + lw + j * (cw + gap), y: y0, w: cw, h: 0.9, fontSize: 15, align: "center" }));
  rows.forEach(([q, hs], i) => {
    const y = y0 + 1.0 + i * (rh + gap);
    T(s, q, { x: x0, y, w: lw - 0.1, h: rh, valign: "middle", fontSize: 13, bold: true, color: i ? X.dk1 : MUTED });
    hs.forEach((h, j) => {
      const x = x0 + lw + j * (cw + gap);
      box(s, x, y, cw, rh, { fill: i ? G1T : SOFT, line: i ? G1T : SOFT });
      T(s, h, { x, y, w: cw, h: rh, align: "center", valign: "middle", fontFace: HF, fontSize: 20, bold: true });
    });
  });
}

// 5 · Diseño de pares emparejados
async function v05() {
  const s = content("DISEÑO EXPERIMENTAL", "Cada historia se genera dos veces: una con cada sistema");
  label(s, 0.6, 2.25, 2.6, 1.3, "Escenario i\nmundo, tono, conflicto y personaje", { fill: SOFT, line: SOFT, fs: 13 });
  label(s, 3.9, 1.7, 2.7, 1.0, "Historia con G1\n1,400 turnos", { fill: G1T, line: G1, bold: true, fs: 14 });
  label(s, 3.9, 3.1, 2.7, 1.0, "Historia con G2\n1,400 turnos", { fill: G2T, line: G2, bold: true, fs: 14 });
  label(s, 7.3, 2.25, 2.7, 1.3, "Diferencia dentro del par\nG1 − G2", { fs: 14, bold: true });
  arrow(s, 3.2, 2.7, 3.9, 2.2); arrow(s, 3.2, 3.1, 3.9, 3.6);
  arrow(s, 6.6, 2.2, 7.3, 2.7); arrow(s, 6.6, 3.6, 7.3, 3.1);
  [["27", "escenarios (pares)"], ["54", "historias"], ["75,600", "turnos"]].forEach(([b, l], i) => stat(s, 10.6, 1.6 + i * 1.05, 2.2, b, l, X.dk1, 32));
  kick(s, "Igual dentro del par", 0.6, 4.55, 6);
  const k = ["mismo modelo de lenguaje", "misma base de datos", "mismo extractor", "mismos dados", "mismo personaje", "mismo jugador simulado", "1,400 turnos"];
  let x = 0.6, y = 4.95;
  k.forEach((t) => {
    const w = 0.1 * t.length + 0.45;
    if (x + w > 12.75) { x = 0.6; y += 0.55; }
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.42, rectRadius: 0.21, fill: { color: SOFT }, line: { color: SOFT } });
    T(s, t, { x, y, w, h: 0.42, align: "center", valign: "middle", fontSize: 13 });
    x += w + 0.15;
  });
  await analogia(s, "Como probar dos motores en el mismo auto, la misma pista y el mismo piloto: lo único que cambia es el motor.");
  s.addNotes("[3:10–4:10] El diseño es experimental, de medidas repetidas con pares emparejados. Escribimos 27 escenarios distintos y cada uno se generó dos veces: una con G1 y otra con G2. Son 54 historias de 1,400 turnos, 75,600 turnos en total. Dentro del par todo es igual: el mismo modelo de lenguaje, gemma-4 de 31 mil millones de parámetros, de un solo proveedor y con su huella verificada antes de cada tanda; la misma base de datos, los mismos dados, el mismo personaje y el mismo jugador. Es como probar dos motores en el mismo auto, la misma pista y el mismo piloto. Cada escenario es su propio control, y lo que se analiza es la diferencia dentro del par.");
}

// 6 · Jugador simulado y dados
async function v06() {
  const s = content("CONTROLES DEL EXPERIMENTO", "El jugador y la suerte también se controlan");
  box(s, 0.6, 1.7, 5.9, 4.3, { fill: SOFT, line: SOFT });
  await iconDot(s, "FaUserSecret", 0.9, 1.95, 0.75, "FFFFFF", X.dk1);
  T(s, "Jugador simulado", { x: 1.85, y: 2.05, w: 4.5, h: 0.5, fontFace: HF, fontSize: 22, bold: true });
  T(s, [
    { text: "Un modelo de lenguaje con personalidad y objetivos fijos", options: { breakLine: true, bullet: true } },
    { text: "Juega igual contra G1 y contra G2", options: { breakLine: true, bullet: true } },
    { text: "75,600 turnos no se pueden jugar con personas", options: { bullet: true } },
  ], { x: 0.9, y: 2.95, w: 5.4, h: 1.5, fontSize: 14, paraSpaceAfter: 6 });
  [["8", "principistas"], ["14", "moral ambigua"], ["5", "sin escrúpulos"]].forEach(([b, l], i) => stat(s, 0.9 + i * 1.8, 4.6, 1.7, b, l, X.dk1, 28));
  box(s, 6.83, 1.7, 5.9, 4.3, { fill: SOFT, line: SOFT });
  await iconDot(s, "FaDiceD20", 7.13, 1.95, 0.75, "FFFFFF", X.dk1);
  T(s, "Dados verificables", { x: 8.08, y: 2.05, w: 4.5, h: 0.5, fontFace: HF, fontSize: 22, bold: true });
  T(s, [
    { text: "Dado de 20 caras + bonificación de la ficha, resuelto por código", options: { breakLine: true, bullet: true } },
    { text: "Mismo mecanismo en ambos sistemas", options: { breakLine: true, bullet: true } },
    { text: "La suerte no favoreció a ninguno", options: { bullet: true } },
  ], { x: 7.13, y: 2.95, w: 5.4, h: 1.5, fontSize: 14, paraSpaceAfter: 6 });
  [["4.7 %", "coincidencias (azar: 5 %)"], ["p = 0.946", "dado medio G1 vs G2"]].forEach(([b, l], i) => stat(s, 7.13 + i * 2.7, 4.6, 2.6, b, l, X.dk1, 28));
  await analogia(s, "Como un «cliente incógnito» que visita las dos cocinas con el mismo pedido y la misma actitud.");
  s.addNotes("[4:10–5:00] Dos controles más. El jugador también es un modelo de lenguaje, con una personalidad y objetivos fijos: hay 27 personajes, desde principistas hasta personajes sin escrúpulos. Es como un cliente incógnito que visita las dos cocinas con el mismo pedido y la misma actitud, porque 75,600 turnos no se pueden jugar con personas. Y la suerte: las tiradas de dado las resuelve el código, con el mismo mecanismo en los dos sistemas. Las secuencias no son idénticas, pero verificamos que la suerte no favoreció a ninguno: coinciden lo que da el azar y el dado medio no difiere.");
}

// 8 · La brigada, puesto por puesto
async function v08() {
  const s = content("G1 · LA BRIGADA, PUESTO POR PUESTO", "Cada agente hace una tarea y ve solo lo que necesita");
  const R = [
    ["Enrutador", "código", "Recibe la comanda y decide qué puestos intervienen.", false],
    ["Árbitro", "código; modelo si hace falta juicio", "Aplica las reglas: ¿la acción sale bien o mal?", false],
    ["Actor de PNJ", "modelo", "Da voz a cada personaje con solo lo que ese personaje sabe.", true],
    ["Agente del mundo", "código + modelo", "Hace avanzar lo que pasa alrededor, aunque el jugador no mire.", true],
    ["Narrador", "modelo", "Escribe la única prosa que ve el jugador, sin conocer los secretos.", true],
  ];
  R.forEach(([n, t, d, mod], i) => {
    const x = 0.6 + i * 2.46;
    box(s, x, 1.75, 2.26, 3.45, { fill: mod ? G1 : "FFFFFF", line: G1, lw: 1.25 });
    T(s, String(i + 1), { x: x + 0.2, y: 1.9, w: 1, h: 0.5, fontFace: HF, fontSize: 24, bold: true, color: mod ? "FFFFFF" : G1 });
    T(s, n, { x: x + 0.2, y: 2.45, w: 1.95, h: 0.45, fontSize: 16, bold: true, color: mod ? "FFFFFF" : X.dk1 });
    T(s, t, { x: x + 0.2, y: 2.9, w: 1.95, h: 0.5, fontSize: 11, color: mod ? "D7EEEE" : MUTED });
    T(s, d, { x: x + 0.2, y: 3.45, w: 1.9, h: 1.7, fontSize: 13, color: mod ? "FFFFFF" : X.dk1 });
    if (i < 4) arrow(s, x + 2.26, 3.47, x + 2.46, 3.47, { color: G1 });
  });
  box(s, 0.6, 5.4, 12.1, 0.6, { fill: G2T, line: G2T });
  T(s, [{ text: "G2: ", options: { bold: true, color: G2 } }, { text: "un solo director de juego hace los cinco trabajos en una llamada, viendo todo, incluidos los secretos de los personajes." }],
    { x: 0.85, y: 5.4, w: 11.7, h: 0.6, valign: "middle", fontSize: 14 });
  await analogia(s, "El narrador es el mesero: lo único que ve el cliente. Los secretos se quedan en la cocina.", 6.25);
  s.addNotes("[5:50–6:50] En G1 el turno pasa por cinco puestos. El enrutador, en código, recibe la comanda y decide quién interviene. El árbitro aplica las reglas y decide si la acción sale bien o mal; usa el modelo solo si hace falta juicio. El actor da voz a cada personaje con solo lo que ese personaje sabe, así no se le escapan secretos ajenos. El agente del mundo hace avanzar lo que pasa alrededor. Y el narrador escribe la única prosa que ve el jugador, sin conocer los secretos: es el mesero, lo único que ve el cliente. En G2, un solo director de juego hace los cinco trabajos en una llamada, viéndolo todo.");
}

// 9 · Memoria: el libro contable
async function v09() {
  const s = content("MEMORIA COMÚN A G1 Y G2", "El mundo se lleva como un libro contable");
  const L = [
    ["FaClipboardList", "Formulario cerrado", "Solo 19 campos del mundo se pueden modificar."],
    ["FaReceipt", "Comprobante obligatorio", "Todo cambio debe citar textualmente el turno que lo causó."],
    ["FaTags", "Tarifario, no regateo", "Las magnitudes salen de una tabla según la personalidad del personaje, no del modelo."],
  ];
  for (let i = 0; i < 3; i++) {
    const y = 1.75 + i * 1.3;
    await iconDot(s, L[i][0], 0.6, y, 0.8, "FFFFFF", X.dk1);
    T(s, L[i][1], { x: 1.6, y: y - 0.02, w: 4.9, h: 0.4, fontSize: 18, bold: true });
    T(s, L[i][2], { x: 1.6, y: y + 0.4, w: 4.9, h: 0.75, fontSize: 14, color: MUTED });
  }
  box(s, 6.9, 1.7, 5.8, 3.6, { fill: SOFT, line: SOFT });
  kick(s, "El tarifario en acción", 7.2, 1.9, 5.2);
  T(s, "«Le ofreces dinero al guardia para que mire a otro lado.»", { x: 7.2, y: 2.3, w: 5.2, h: 0.75, fontSize: 16, italic: true });
  [["Guardia honesto", "se ofende", "su actitud hacia ti baja", HOT], ["Guardia corrupto", "acepta", "no se ofende", MUTED]].forEach(([who, what, eff, col], i) => {
    const x = 7.2 + i * 2.65;
    box(s, x, 3.15, 2.45, 1.9, { fill: "FFFFFF", line: LINE });
    T(s, who, { x: x + 0.15, y: 3.3, w: 2.15, h: 0.35, fontSize: 13, bold: true });
    T(s, what, { x: x + 0.15, y: 3.75, w: 2.15, h: 0.45, fontFace: HF, fontSize: 20, bold: true, color: col });
    T(s, eff, { x: x + 0.15, y: 4.3, w: 2.15, h: 0.5, fontSize: 12, color: MUTED });
  });
  // comprobante real: par 02 (Alto Ferrena), G2, turno 979, delta 1511 (promise_made, docs/reportes/compromisos)
  box(s, 0.6, 5.42, 12.1, 0.68, { fill: "FFFFFF", line: X.dk1, lw: 1.25 });
  T(s, [{ text: "Comprobante real · par 02, G2, turno 979   ", options: { bold: true } }, { text: "Jugador: «Prometo que haré todo lo posible para protegerte…»  →  registro: " }, { text: "promesa hecha", options: { bold: true } }, { text: " a «el hombre de los harapos», con esa cita literal." }],
    { x: 0.8, y: 5.42, w: 11.7, h: 0.68, valign: "middle", fontSize: 13 });
  await analogia(s, "Como la contabilidad de una empresa: ningún asiento sin comprobante, y solo en las cuentas autorizadas.", 6.25);
  s.addNotes("[6:50–7:50] Ambos sistemas comparten la misma memoria: el estado del mundo vive en una base de datos PostgreSQL, no en la memoria del modelo, y se lleva como un libro contable. Tiene tres candados. Un formulario cerrado: solo 19 campos se pueden modificar. Un comprobante obligatorio: cada cambio debe citar textualmente el turno que lo causó; si el modelo parafrasea, se rechaza. Y un tarifario: las magnitudes las pone una tabla según la personalidad del personaje. Por ejemplo, el mismo soborno ofende a un guardia honesto y no ofende a uno corrupto. Abajo, un comprobante real: en el turno 979 el jugador promete proteger a un personaje, y el sistema registra la promesa con la cita textual de esa frase. El modelo propone; el código valida y escribe. Así quedaron 77,413 turnos y 17,908 cambios, cada uno con su comprobante. Esto es importante: como la memoria es igual en los dos brazos, lo único que comparamos es la organización del trabajo.");
}

// 10 · Medir sin un panel humano
async function v10() {
  const s = content("CÓMO SE MIDIÓ", "Sin panel humano: se midió con instrumentos automáticos");
  const steps = [["FaUsers", "Panel de 5 expertos", "inviable sobre 75,600 turnos; quedó como estudio piloto (14 set 2026, con el asesor)"], ["FaClipboardCheck", "Rúbrica D&D-IA", "define qué medir: 3 dimensiones y 6 indicadores"], ["FaBalanceScale", "Instrumentos deterministas", "el mismo texto da siempre la misma lectura; reproducibles"]];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    box(s, x, 1.75, 3.8, 2.75, { fill: i === 2 ? X.dk1 : SOFT, line: i === 2 ? X.dk1 : SOFT });
    await iconDot(s, steps[i][0], x + 0.3, 2.0, 0.7, i === 2 ? X.dk1 : "FFFFFF", i === 2 ? "FFFFFF" : X.dk1);
    T(s, steps[i][1], { x: x + 0.3, y: 2.85, w: 3.2, h: 0.45, fontSize: 18, bold: true, color: i === 2 ? "FFFFFF" : X.dk1 });
    T(s, steps[i][2], { x: x + 0.3, y: 3.3, w: 3.2, h: 1.1, fontSize: 13, color: i === 2 ? "D5D8E3" : MUTED });
    if (i < 2) arrow(s, x + 3.8, 3.12, x + 4.1, 3.12, { color: X.dk1 });
  }
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: X.dk1 } } });
  s.addTable([
    [H("Dimensión"), H("Indicador 1"), H("Indicador 2")],
    ["Reactiva: responde a lo que hiciste", "CR-1 · fluidez", "CR-2 · arraigo a la acción"],
    ["Longitudinal: recuerda lo que pasó", "CL-1 · consistencia de personajes", "CL-2 · consistencia de eventos y mundo"],
    ["Calidad: interesa y te deja decidir", "QN-1 · interés y diversidad", "QN-2 · respeto a la agencia"],
  ], { x: 0.6, y: 4.7, w: 12.1, colW: [4.3, 3.9, 3.9], fontSize: 13, color: X.dk1, border: { type: "solid", pt: 0.75, color: LINE }, rowH: 0.36, valign: "middle", margin: 0.06 });
  s.addNotes("[7:50–8:40] ¿Cómo se mide la coherencia de 75,600 turnos? Inicialmente planeamos un panel de cinco expertos, pero no era viable a esta escala; de acuerdo con el asesor, el panel quedó como estudio piloto. La rúbrica D&D-IA define qué medir: tres dimensiones y seis indicadores, que ven en la tabla. Y para medir usamos instrumentos deterministas, es decir, programas que leen el texto y devuelven siempre la misma lectura para el mismo texto. Eso los hace reproducibles: cualquiera puede volver a correrlos y obtener lo mismo.");
}

// 11 · Calibrar el instrumento
async function v11() {
  const s = content("VALIDACIÓN DE CADA INSTRUMENTO", "Antes de confiar en una balanza, se prueba con pesas conocidas");
  const st = [
    ["FaEnvelope", "1 · Sellar la predicción", "Se escribe qué debe detectar el instrumento y se sella con SHA-256 antes de mirar.", "sobre lacrado"],
    ["FaFlask", "2 · Inyectar defectos", "Se crean copias del texto con un defecto de efecto conocido.", "pesas patrón"],
    ["FaChartBar", "3 · Exigir que lo detecte", "Diferencia de tamaño mínimo (δ de Cliff ≥ 0.147) y significativa tras Holm.", "la balanza marca"],
    ["FaTag", "4 · Clasificar", "Según cómo le fue, el instrumento decide, orienta o solo describe.", "etiqueta de calibración"],
  ];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.1;
    box(s, x, 1.75, 2.85, 3.9, { fill: SOFT, line: SOFT });
    await iconDot(s, st[i][0], x + 0.3, 2.0, 0.7, "FFFFFF", X.dk1);
    T(s, st[i][1], { x: x + 0.3, y: 2.85, w: 2.4, h: 0.7, fontSize: 16, bold: true });
    T(s, st[i][2], { x: x + 0.3, y: 3.55, w: 2.35, h: 1.45, fontSize: 13, color: MUTED });
    T(s, "≈ " + st[i][3], { x: x + 0.3, y: 5.05, w: 2.4, h: 0.4, fontSize: 12, italic: true, color: G1 });
    if (i < 3) arrow(s, x + 2.85, 3.7, x + 3.1, 3.7, { color: X.dk1 });
  }
  small(s, "Validez buscada por perturbación y por contraste con juicio humano externo; los índices kappa de la literatura miden confiabilidad, no validez.", 5.85);
  await analogia(s, "Si la balanza no detecta la pesa de 1 kg que le pusimos, no la usamos para pesar lo que no conocemos.", 6.3);
  s.addNotes("[8:40–9:40] Un instrumento automático puede medir mal, así que cada uno pasó una prueba de sensibilidad. Es como calibrar una balanza con pesas conocidas. Primero escribimos qué debía detectar y lo sellamos con un hash SHA-256 antes de mirar los resultados, como un sobre lacrado. Segundo, creamos copias del texto con defectos de efecto conocido: las pesas patrón. Tercero, exigimos que el instrumento detecte la diferencia, con un tamaño de efecto mínimo y corrección de Holm por hacer varias pruebas. Y cuarto, según cómo le fue, lo clasificamos. Si la balanza no detecta la pesa que le pusimos, no la usamos para pesar lo que no conocemos.");
}

// 12 · Clasificación de la evidencia y peritos externos
async function v12() {
  const s = content("CLASIFICACIÓN DE LA EVIDENCIA", "Como en un juicio: hay pruebas e indicios");
  const K = [
    ["Confirmatorio", "prueba que decide la hipótesis", HOT, "CR-2 · respuesta a la acción específica"],
    ["Condicionado", "decide, pero falta confirmar que coincide con el juicio humano", G2, "QN-2 · persona2 (usurpación explícita)"],
    ["Exploratorio", "indicio: orienta, no decide", X.accent4, "Jericho, supervivencia, semántico, entidad…"],
    ["Descriptivo", "describe, sin contraste", "B9BDCB", ""],
  ];
  K.forEach(([h, d, col, ex], i) => {
    const y = 1.7 + i * 0.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 2.3, h: 0.75, rectRadius: 0.08, fill: { color: col }, line: { color: col } });
    T(s, h, { x: 0.6, y, w: 2.3, h: 0.75, align: "center", valign: "middle", fontSize: 15, bold: true, color: "FFFFFF" });
    T(s, d, { x: 3.1, y, w: 4.0, h: 0.75, valign: "middle", fontSize: 13 });
    T(s, ex, { x: 7.2, y, w: 5.5, h: 0.75, valign: "middle", fontSize: 13, bold: true, color: i < 2 ? X.dk1 : MUTED });
  });
  box(s, 0.6, 5.6, 5.9, 0.95, { fill: "FFFFFF", line: HOT, lw: 1.5 });
  T(s, [{ text: "Longitudinal (CL-1, CL-2): ", options: { bold: true, color: HOT } }, { text: "ningún instrumento llegó a confirmatorio." }], { x: 0.85, y: 5.6, w: 5.5, h: 0.95, valign: "middle", fontSize: 14 });
  box(s, 6.83, 5.6, 5.9, 0.95, { fill: SOFT, line: SOFT });
  await iconDot(s, "FaUserCheck", 7.0, 5.78, 0.6, "FFFFFF", X.dk1);
  T(s, [{ text: "Peritos externos: ", options: { bold: true } }, { text: "la validación humana la hicieron evaluadores externos; los autores nunca etiquetaron." }], { x: 7.75, y: 5.6, w: 4.85, h: 0.95, valign: "middle", fontSize: 13 });
  s.addNotes("[9:40–10:30] Como en un juicio, no toda evidencia pesa igual. Un instrumento confirmatorio es una prueba que decide. Uno condicionado decide, pero falta confirmar que coincide con el juicio humano. Uno exploratorio es un indicio: orienta, no decide. Y uno descriptivo solo describe. Al final, solo dos instrumentos pudieron decidir: la respuesta a la acción específica, para la dimensión reactiva, y persona2, que detecta cuándo el sistema decide por el jugador, este último condicionado. Lo decimos desde ya: la dimensión longitudinal se quedó sin instrumento confirmatorio. Donde un instrumento interpreta el texto, lo contrastamos con evaluadores externos, como peritos independientes; nosotros nunca etiquetamos.");
}

// 13 · Análisis estadístico
async function v13() {
  const s = content("ANÁLISIS ESTADÍSTICO", "Dos preguntas, dos pruebas");
  const P = [
    ["¿El cocinero solo empeora con las horas?", "Prueba de tendencia de Page", "Cada historia de G2 se parte en 7 bloques de 200 turnos y se busca una caída ordenada.", "H1a–H1c", "Como medir a un mesero cada hora de su turno.", G2, G2T],
    ["¿La brigada lo hace mejor?", "Wilcoxon de rangos con signo, pareado", "Se compara G1 − G2 dentro de cada par, sin suponer distribución normal.", "H1d–H1f", "Como comparar los dos motores en cada una de las 27 pistas.", G1, G1T],
  ];
  P.forEach(([q, t, d, h, an, col, tint], i) => {
    const x = 0.6 + i * 6.23;
    box(s, x, 1.7, 5.87, 3.75, { fill: tint, line: tint });
    T(s, h, { x: x + 0.35, y: 1.9, w: 3, h: 0.35, fontSize: 13, bold: true, color: col });
    T(s, q, { x: x + 0.35, y: 2.25, w: 5.2, h: 0.5, fontSize: 18, bold: true });
    T(s, t, { x: x + 0.35, y: 2.85, w: 5.2, h: 0.5, fontFace: HF, fontSize: 21, bold: true, color: col });
    T(s, d, { x: x + 0.35, y: 3.45, w: 5.2, h: 0.95, fontSize: 14 });
    T(s, an, { x: x + 0.35, y: 4.55, w: 5.2, h: 0.6, fontSize: 13, italic: true, color: MUTED });
  });
  [["N = 27 pares", "G*Power: efecto medio (dz = 0.5), α = 0.05"], ["potencia 0.81", "unilateral, el contraste declarado"], ["Holm", "corrige por hacer varias pruebas a la vez"]].forEach(([b, l], i) => {
    T(s, [{ text: b + "  ", options: { bold: true, fontSize: 17 } }, { text: l, options: { color: MUTED, fontSize: 12 } }], { x: 0.6 + i * 4.1, y: 5.75, w: 4.0, h: 0.8 });
  });
  s.addNotes("[10:30–11:20] Para las dos preguntas usamos dos pruebas. Para saber si el sistema simple empeora con el tiempo, partimos cada historia de G2 en siete bloques de 200 turnos y aplicamos la prueba de tendencia de Page, que busca una caída ordenada: como medir a un mesero cada hora de su turno. Para saber si G1 es mejor, comparamos G1 contra G2 dentro de cada par con Wilcoxon pareado, que no supone normalidad. Corregimos con Holm porque hacemos varias pruebas. El tamaño de 27 pares sale de G*Power, para un efecto medio con potencia de 0.81.");
}

// 14 · Resultados en una lámina
function v14() {
  const s = content("RESULTADOS", "Lo que respondieron los datos");
  const R = [
    ["¿El cocinero solo empeora?", "No", "Respuesta a la acción: 2.768 → 2.742 en 1,400 turnos (Page p = 0.310).", "no"],
    ["¿Responde mejor la brigada? (H1d)", "No", "Empate en lo específico (p = 0.59). La ventaja aparente de G1 era «efecto horóscopo»: textos más largos que encajan con cualquier acción.", "no"],
    ["¿Recuerda mejor la brigada? (H1e)", "Sin decisión", "Tres intentos (Jericho, supervivencia, semántico); ninguno llegó a confirmatorio.", "na"],
    ["¿Te deja decidir más? (H1f)", "Sí*", "Usurpa tu agencia en el 0.17 % de los turnos, frente al 3.47 % de G2.", "ok"],
  ];
  R.forEach(([q, v, d, k], i) => {
    const x = 0.6 + (i % 2) * 6.23, y = 1.7 + Math.floor(i / 2) * 2.3;
    const hot = k === "ok";
    box(s, x, y, 5.87, 2.1, { fill: hot ? HOTT : SOFT, line: hot ? HOT : SOFT, lw: hot ? 1.5 : 1 });
    T(s, q, { x: x + 0.3, y: y + 0.2, w: 3.3, h: 0.55, fontSize: 15, bold: true });
    T(s, v, { x: x + 3.4, y: y + 0.12, w: 2.2, h: 0.6, fontFace: HF, fontSize: 22, bold: true, align: "right", color: hot ? HOT : MUTED });
    T(s, d, { x: x + 0.3, y: y + 0.75, w: 5.3, h: 1.25, fontSize: 13 });
  });
  T(s, [{ text: "Hipótesis general: no se sostiene", options: { bold: true } }, { text: " (gana solo en una de tres).   * condicionada a la precisión del detector." }], { x: 0.6, y: 6.4, w: 12.1, h: 0.4, fontSize: 14, color: X.dk1 });
  s.addNotes("[11:20–12:35] Estos son los resultados. Primero, el sistema simple no empeora: la respuesta a la acción pasa de 2.768 a 2.742 en 1,400 turnos, sin tendencia. Segundo, la coherencia reactiva: el confirmatorio favorece ligeramente a G2, y cuando separamos la parte específica de la genérica, hay empate en lo específico. La ventaja que veíamos en G1 era un efecto horóscopo: G1 escribe más largo, unos 16 lemas más por turno, y un texto largo se parece a cualquier acción. Tercero, en memoria a largo plazo ningún instrumento llegó a decidir. Y cuarto, la agencia: G1 decide por el jugador en el 0.17 por ciento de los turnos; G2, en el 3.47. Gana en una de tres, así que la hipótesis general no se sostiene.");
}

// 15 · La agencia resiste la corrección
function v15() {
  const s = content("RESULTADOS · H1f", "La ventaja en la agencia resiste aunque el detector se equivoque");
  T(s, "0.17 %", { x: 0.6, y: 1.65, w: 3.6, h: 1.0, fontFace: HF, fontSize: 54, bold: true, color: G1 });
  T(s, "G1 · multiagente", { x: 0.6, y: 2.65, w: 3.6, h: 0.35, fontSize: 14, bold: true, color: G1 });
  T(s, "3.47 %", { x: 0.6, y: 3.15, w: 3.6, h: 1.0, fontFace: HF, fontSize: 54, bold: true, color: G2 });
  T(s, "G2 · monolítico", { x: 0.6, y: 4.15, w: 3.6, h: 0.35, fontSize: 14, bold: true, color: G2 });
  T(s, "turnos en que el sistema decide, piensa, siente o habla por el jugador (mediana de 27 pares)", { x: 0.6, y: 4.6, w: 3.6, h: 0.9, fontSize: 12, color: MUTED });
  // detector con falsas alarmas
  box(s, 4.6, 1.7, 8.1, 1.65, { fill: SOFT, line: SOFT });
  kick(s, "El detector tiene falsas alarmas", 4.9, 1.85, 7);
  T(s, [{ text: "Precisión 33 %", options: { bold: true } }, { text: " frente al evaluador externo de referencia: de cada 3 alarmas, 2 son falsas. Por brazo: 42.9 % en G1 y 28.6 % en G2." }],
    { x: 4.9, y: 2.2, w: 7.6, h: 1.05, fontSize: 14 });
  // 27 cuadros
  kick(s, "Corrigiendo cada brazo por sus falsas alarmas: G1 < G2 en", 4.6, 3.6, 8);
  for (let i = 0; i < 27; i++) {
    const x = 4.6 + (i % 14) * 0.5, y = 4.0 + Math.floor(i / 14) * 0.52;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 0.42, h: 0.42, rectRadius: 0.06, fill: { color: G1 }, line: { color: G1 } });
    T(s, String(i + 1), { x, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontSize: 10, color: "FFFFFF", bold: true });
  }
  T(s, "27 / 27", { x: 11.15, y: 4.42, w: 1.55, h: 0.6, fontFace: HF, fontSize: 26, bold: true, color: G1, align: "right" });
  T(s, "pares · peor caso 26/27 · p < 0.0001", { x: 8.6, y: 5.2, w: 4.1, h: 0.3, fontSize: 12, color: MUTED, align: "right" });
  chip(s, 0.6, 5.65, "H1f · se acepta (condicionada)", "ok");
  T(s, "Cambia la magnitud (en G2, entre 0.5 % y 1 %), no la dirección.", { x: 4.6, y: 5.7, w: 8.1, h: 0.35, fontSize: 13 });
  T(s, "Como un detector de metales con falsas alarmas: aun descontándolas en cada playa, una tiene más metal que la otra en las 27 pruebas.", { x: 0.6, y: 6.35, w: 12.1, h: 0.45, fontSize: 13, italic: true, color: MUTED });
  s.addNotes("[12:35–13:35] Este es el resultado principal, y queremos mostrar por qué lo sostenemos. El detector persona2 tiene falsas alarmas: tres directores de juego externos lo revisaron a ciegas y, frente al evaluador de referencia, su precisión es del 33 por ciento; de cada tres alarmas, dos son falsas. Por eso corregimos la tasa de cada brazo por su propia precisión, 42.9 por ciento en G1 y 28.6 en G2. Aun así, G1 queda por debajo de G2 en los 27 pares, y en el peor caso del intervalo, en 26. Es como un detector de metales con falsas alarmas: aun descontándolas en cada playa, una tiene más metal que la otra. Cambia la magnitud, no la dirección. H1f se acepta, condicionada.");
}

// 17 · Conclusión y aportes
async function v17() {
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Exposición" });
  T(s, "CONCLUSIÓN", { x: 0.7, y: 0.55, w: 6, h: 0.35, fontSize: 12, bold: true, charSpacing: 3, color: X.accent4 });
  T(s, [
    { text: "Con una memoria bien llevada, dividir el trabajo " },
    { text: "no hizo al sistema más coherente", options: { color: X.accent4 } },
    { text: ", pero " },
    { text: "sí hizo que respete las decisiones del jugador.", options: { color: "F08A5D" } },
  ], { x: 0.7, y: 1.05, w: 11.9, h: 2.1, fontFace: HF, fontSize: 32, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.05 });
  const A = [["FaDatabase", "Corpus en español", "75,600 turnos en segunda persona, con el estado del mundo y sus comprobantes"], ["FaBalanceScale", "Instrumentos calibrados", "batería determinista validada por perturbación y con evaluadores externos"], ["FaCompass", "Guía de diseño", "especializar sirve para la agencia; para la coherencia basta una buena memoria"]];
  for (let i = 0; i < 3; i++) {
    const x = 0.7 + i * 4.0;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.55, w: 3.75, h: 1.9, rectRadius: 0.08, fill: { color: "222944" }, line: { color: "2E365A" } });
    await iconDot(s, A[i][0], x + 0.25, 3.75, 0.55, INK, "FFFFFF");
    T(s, A[i][1], { x: x + 0.95, y: 3.8, w: 2.7, h: 0.45, fontSize: 16, bold: true, color: "FFFFFF" });
    T(s, A[i][2], { x: x + 0.25, y: 4.45, w: 3.3, h: 0.9, fontSize: 12, color: X.accent4 });
  }
  T(s, [{ text: "Trabajo futuro: ", options: { bold: true, color: "FFFFFF" } }, { text: "clasificador NLI en español para la memoria a largo plazo · jugadores humanos · monolítico con el mismo presupuesto de llamadas", options: { color: X.accent4 } }],
    { x: 0.7, y: 5.8, w: 11.9, h: 0.6, fontSize: 14 });
  s.addNotes("[14:15–15:00] En conclusión: con una memoria bien llevada, dividir el trabajo entre agentes no hizo al sistema más coherente, pero sí hizo que respete las decisiones del jugador. Es un resultado negativo controlado, y orienta el diseño: para la coherencia basta una buena memoria estructurada; especializar vale para la agencia. La tesis deja además un corpus de 75,600 turnos en español y una batería de instrumentos calibrados. Como trabajo futuro: un clasificador de inferencia textual en español para la memoria a largo plazo, jugadores humanos y un monolítico con el mismo presupuesto de llamadas. Muchas gracias.");
}

(async () => {
  v01(); await v02(); await v03(); await v04(); await v05(); await v06();
  D.l06("[5:00–5:50] Así funciona un turno, y es igual en los dos sistemas. Se lee el estado del mundo desde la base de datos, se arma el contexto con consultas exactas y la última escena, el jugador declara su acción y los dados se resuelven por código. Después de narrar, se verifica el texto y un extractor registra los cambios. Lo único que cambia es la franja del medio: quién produce la narración. En G2, un solo director de juego; en G1, cinco puestos, que veremos ahora. Los bloques oscuros usan el modelo de lenguaje; los claros son código.");
  await v08(); await v09(); await v10(); await v11(); await v12(); await v13(); v14(); v15();
  D.l13("[13:35–14:15] Una objeción obvia: ¿la brigada gana solo porque tiene más gente? Es cierto que gasta más: casi tres llamadas al modelo por turno contra una, 2.6 veces más tiempo de modelo y 1.5 veces más texto. Pero si el gasto fuera la causa, dentro de cada sistema las historias que más gastan deberían usurpar menos. Pasa lo contrario: en ambos, más texto narrado va con más usurpación. Por eso atribuimos la ventaja al diseño multiagente como paquete, y dejamos recomendado comparar contra un monolítico con el mismo presupuesto de llamadas."); // objeción de costo (v3)
  await v17(); D.l16();
  pres.addSection({ title: "Respaldo" });
  D.setSection("Respaldo");
  D.l09(); D.l10(); await D.l11(); D.l12();
  D.b01(); D.b02(); D.b03(); D.b04(); D.b05(); D.b06(); D.b07(); D.b08(); D.b09(); D.b10(); D.b11();
  await pres.writeFile({ fileName: OUT });
  await D.applyTheme(OUT, THEME);
  console.log("OK", OUT);
})().catch((e) => { console.error(e); process.exit(1); });
