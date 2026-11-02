// Generador del deck de sustentación (v3). Fuente de verdad: sustentacion/CONTEXTO_SUSTENTACION.md
// Las cifras de los gráficos se leen de los CSV del repo; las demás salen del contexto.
// Uso (desde la raíz del repo):
//   NODE_PATH=<carpeta con node_modules> PPTX_SKILL=<carpeta del skill pptx> node sustentacion/generador/deck.js
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const ROOT = path.join(__dirname, "..", "..");
const OUT = path.join(__dirname, "..", "propuestas", "Sustentacion_v3.pptx");

// ---------------------------------------------------------------- datos
function csv(rel) {
  const [head, ...rows] = fs.readFileSync(path.join(ROOT, rel), "utf8").trim().split(/\r?\n/);
  const k = head.split(",");
  return rows.map((r) => Object.fromEntries(r.split(",").map((v, i) => [k[i], v])));
}
const median = (a) => { const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const r3 = (x) => Math.round(x * 1000) / 1000;

// H1a: mediana de CR-2a(z) por bloque de 200 turnos (n = 27 por bloque)
const bloques = csv("docs/reportes/sensibilidad_a4bc_distribucion_27.csv");
const INIS = [1, 201, 401, 601, 801, 1001, 1201];
const zBloque = (brazo) => INIS.map((ini) => r3(median(bloques.filter((r) => r.brazo === brazo && +r.ini === ini).map((r) => +r.z))));
const zG2 = zBloque("G2");
if (zG2[0] !== 2.768 || zG2[6] !== 2.742) throw new Error("bloques de G2 no cuadran con el contexto: " + zG2);

// H1f: persona2 por par
const pares = csv("docs/resultados/por_pareja_ancho.csv").sort((a, b) => a.par.localeCompare(b.par));
const p2G1 = pares.map((r) => +r.p2_primaria__G1 * 100), p2G2 = pares.map((r) => +r.p2_primaria__G2 * 100);
if (pares.length !== 27 || p2G1.some((v, i) => v >= p2G2[i])) throw new Error("persona2: se esperaba G1 < G2 en 27/27");

// Costo: caracteres narrados por turno vs persona2, pares 07-27
const costo = csv("docs/reportes/brechas/costo_arquitectura.csv");
const byPar = Object.fromEntries(pares.map((r) => [r.par, r]));
const dosis = (brazo) => costo.filter((r) => r.brazo === brazo).map((r) => [+r.chars_narracion, +byPar[r.par]["p2_primaria__" + brazo] * 100]);

// Kaplan-Meier: primera mención de un PNJ no vivo (1401 = censurado)
function km(ts) {
  const ev = [...new Set(ts.filter((t) => t <= 1400))].sort((a, b) => a - b);
  let s = 1, n = ts.length; const out = [[0, 1]];
  for (const t of ev) {
    const d = ts.filter((x) => x === t).length;
    out.push([t, s]); s *= 1 - d / n; out.push([t, s]);
    n -= d;
  }
  out.push([1400, s]);
  return out;
}

// ---------------------------------------------------------------- tema
const THEME = {
  name: "DM-IA Sustentacion",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2035", lt1: "FFFFFF", dk2: "5B6178", lt2: "F1F2F6",
    accent1: "0F8B8D", // G1 multiagente (solo para G1)
    accent2: "D08C2E", // G2 monolítico (solo para G2)
    accent3: "C2410C", // el hallazgo (usurpación / H1f)
    accent4: "8A90A6", accent5: "2B3150", accent6: "E3E5EC",
    hlink: "0F8B8D", folHlink: "5B6178",
  },
};
const X = THEME.colors;
const INK = "141A2E";
const G1 = X.accent1, G2 = X.accent2, HOT = X.accent3, MUTED = X.dk2, LINE = X.accent6, SOFT = X.lt2;
const G1T = "E3F2F2", G2T = "FAF0E1", HOTT = "FBEAE2"; // tintes

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Sustentación: coherencia narrativa MAS vs monolítico";
pres.author = "Marin Yupanqui, B. A.; Mostacero Cieza, L. D.";
const C = pres.SchemeColor;
const W = 13.333;

pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: "FFFFFF" },
  objects: [
    { placeholder: { options: { name: "kicker", type: "body", x: 0.6, y: 0.35, w: 9, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: C.accent4, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.65, w: 12.1, h: 0.75, fontFace: THEME.headFontFace, fontSize: 28, bold: true, color: C.text1, margin: 0, valign: "top", align: "left" }, text: "" } },
    { text: { text: "Marin · Mostacero · UPAO 2026", options: { x: 0.6, y: 7.05, w: 5, h: 0.25, fontSize: 9, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.02, w: 0.5, h: 0.3, fontSize: 9, color: X.accent4, align: "right" },
});
pres.defineSlideMaster({ title: "OSCURO", background: { color: INK }, objects: [] });

// ---------------------------------------------------------------- utilidades
const ICON = {};
async function icon(name, color) {
  const key = name + color;
  if (!ICON[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { color: "#" + color, size: 256 }));
    ICON[key] = "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
  }
  return ICON[key];
}
async function iconDot(s, name, x, y, d, fg, bg) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg } });
  const p = d * 0.26;
  s.addImage({ data: await icon(name, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p });
}
function T(s, text, o) { s.addText(text, { isTextBox: true, margin: 0, valign: "top", fontSize: 16, color: X.dk1, ...o }); }
function box(s, x, y, w, h, o = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: o.fill || "FFFFFF" }, line: { color: o.line || LINE, width: o.lw || 1, dashType: o.dash || "solid" } });
}
function label(s, x, y, w, h, text, o = {}) {
  box(s, x, y, w, h, o);
  T(s, text, { x: x + 0.12, y, w: w - 0.24, h, align: "center", valign: "middle", fontSize: o.fs || 13, color: o.color || X.dk1, bold: o.bold });
}
function arrow(s, x1, y1, x2, y2, o = {}) {
  s.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.max(Math.abs(x2 - x1), 0.001), h: Math.max(Math.abs(y2 - y1), 0.001),
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color: o.color || X.accent4, width: o.width || 1.5, dashType: o.dash || "solid", endArrowType: o.noHead ? undefined : "triangle" },
  });
}
// Veredicto de hipótesis
function chip(s, x, y, text, kind) {
  const st = { ok: { fill: HOT, color: "FFFFFF", line: HOT }, no: { fill: "FFFFFF", color: MUTED, line: X.accent4 }, na: { fill: SOFT, color: MUTED, line: SOFT } }[kind];
  const w = 0.13 * text.length * 0.62 + 0.5;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.42, rectRadius: 0.21, fill: { color: st.fill }, line: { color: st.line, width: 1 } });
  T(s, text, { x, y, w, h: 0.42, align: "center", valign: "middle", fontSize: 13, bold: true, color: st.color });
}
let SECTION = "Exposición"; // sección por defecto de content(); deck_v4 la cambia al reutilizar láminas
const setSection = (t) => { SECTION = t; };
function content(kicker, title, section) {
  const s = pres.addSlide({ masterName: "CONTENIDO", sectionTitle: section || SECTION });
  s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  return s;
}
function stat(s, x, y, w, big, small, color, bigSize = 40) {
  T(s, big, { x, y, w, h: bigSize / 60, fontFace: THEME.headFontFace, fontSize: bigSize, bold: true, color });
  T(s, small, { x, y: y + bigSize / 60 + 0.05, w, h: 0.6, fontSize: 13, color: MUTED });
}
const AX = { catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 11, valAxisLabelFontSize: 11, valGridLine: { color: LINE, size: 0.75 }, catGridLine: { style: "none" }, catAxisLineColor: X.accent4, valAxisLineShow: false, legendFontFace: "+mn-lt", legendFontSize: 11, legendColor: MUTED, valAxisTitleFontFace: "+mn-lt", catAxisTitleFontFace: "+mn-lt", valAxisTitleColor: MUTED, catAxisTitleColor: MUTED, valAxisTitleFontSize: 11, catAxisTitleFontSize: 11, dataLabelFontFace: "+mn-lt" };

// Motivo: G1 = constelación de 5 nodos; G2 = un nodo
function motifG1(s, x, y, sz, color, ring = INK) {
  const pts = [[0.5, 0], [1, 0.38], [0.8, 1], [0.2, 1], [0, 0.38]].map(([a, b]) => [x + a * sz, y + b * sz]);
  pts.forEach(([ax, ay], i) => { const [bx, by] = pts[(i + 1) % 5]; arrow(s, ax, ay, bx, by, { color, width: 1.25, noHead: true }); });
  const r = 0.16 * sz;
  pts.forEach(([cx, cy]) => s.addShape(pres.shapes.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: { color }, line: { color: ring, width: 1.5 } }));
}
function motifG2(s, x, y, d, color, ring = INK) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { color: ring, width: 1.5 } });
}

// ================================================================ EXPOSICIÓN
pres.addSection({ title: "Exposición" });

// 1 · Portada
function l01() {
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Exposición" });
  T(s, "SUSTENTACIÓN DE TESIS", { x: 0.7, y: 0.6, w: 7.5, h: 0.35, fontSize: 12, bold: true, charSpacing: 3, color: X.accent4 });
  T(s, "Comparación de la coherencia narrativa en campañas de Dungeons & Dragons generadas por sistemas multiagente versus sistemas monolíticos", {
    x: 0.7, y: 1.2, w: 7.6, h: 2.9, fontFace: THEME.headFontFace, fontSize: 32, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.05 });
  T(s, [
    { text: "Marin Yupanqui, Bryan Arturo", options: { breakLine: true } },
    { text: "Mostacero Cieza, Luis David", options: { breakLine: true } },
    { text: "Asesor: Dr. Cueva Chávez, Walter Manuel", options: { color: X.accent4 } },
  ], { x: 0.7, y: 4.55, w: 7.5, h: 1.2, color: "FFFFFF", paraSpaceAfter: 4 });
  T(s, "Universidad Privada Antenor Orrego · Escuela de Ingeniería de Sistemas e Inteligencia Artificial · Trujillo, 2026", { x: 0.7, y: 6.55, w: 11.9, h: 0.35, fontSize: 11, color: X.accent4 });
  motifG1(s, 9.05, 1.75, 1.9, G1);
  motifG2(s, 9.6, 4.45, 0.8, G2);
  T(s, "G1 · multiagente", { x: 8.6, y: 3.95, w: 2.8, h: 0.35, align: "center", fontSize: 12, color: G1, bold: true });
  T(s, "G2 · monolítico", { x: 8.6, y: 5.4, w: 2.8, h: 0.35, align: "center", fontSize: 12, color: G2, bold: true });
  s.addNotes("[0:00–0:30] Buenos días, señores miembros del jurado. Somos Bryan Marin y Luis Mostacero, y presentamos nuestra tesis, asesorada por el Dr. Walter Cueva. Comparamos dos formas de construir un director de juego con inteligencia artificial para Dungeons & Dragons: un sistema multiagente, al que llamaremos G1, y un sistema monolítico, G2. En toda la exposición, el verde azulado es G1 y el ocre es G2.");
}

// 2 · El problema
async function l02() {
  const s = content("EL PROBLEMA", "Un director de juego con IA pierde el hilo… y juega por ti");
  const cards = [
    ["FaHourglassHalf", "Olvida", "El herrero que te vendió la espada hace 300 turnos ya no sabe quién eres.", false],
    ["FaRandom", "Contradice", "Yenna desapareció tras el incendio… y hoy te atiende en su puesto del mercado.", false],
    ["FaUserSlash", "Decide por ti", "Tú: «Me quedo en silencio».\nDM: «Decides confesarlo todo y sientes alivio».", true],
  ];
  for (let i = 0; i < 3; i++) {
    const [ic, head, ex, hot] = cards[i];
    const x = 0.6 + i * 4.1;
    box(s, x, 1.8, 3.8, 3.6, { fill: hot ? HOTT : SOFT, line: hot ? HOTT : SOFT });
    await iconDot(s, ic, x + 0.35, 2.15, 0.9, "FFFFFF", hot ? HOT : X.dk1);
    T(s, head, { x: x + 0.35, y: 3.3, w: 3.1, h: 0.55, fontFace: THEME.headFontFace, fontSize: 24, bold: true, color: hot ? HOT : X.dk1 });
    T(s, ex, { x: x + 0.35, y: 4.0, w: 3.15, h: 1.9, fontSize: 16, italic: true, color: X.dk1 });
  }
  T(s, "Ejemplos ilustrativos de turnos en segunda persona.", { x: 0.6, y: 5.6, w: 8, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes("[0:30–1:30] En D&D, el director de juego narra el mundo, interpreta a los personajes no jugadores y arbitra las reglas; el jugador solo decide qué hace su personaje. Cuando un modelo de lenguaje cumple ese papel durante cientos de turnos, aparecen tres fallas. Olvida hechos previos. Contradice el estado del mundo, como revivir a alguien que había desaparecido. Y la más grave para un juego: decide por el jugador. El jugador dijo que se quedaba callado y el sistema le hizo confesar y le dictó lo que siente. A esa tercera falla la llamamos usurpación de la agencia, y va a volver al final.");
}

// 3 · El vacío
async function l03() {
  const s = content("EL VACÍO", "Se propone dividir el trabajo entre agentes, pero nadie lo ha comparado en rol de mesa");
  box(s, 0.6, 1.8, 5.9, 4.6, { fill: SOFT, line: SOFT });
  box(s, 6.83, 1.8, 5.9, 4.6, { fill: "FFFFFF", line: HOT, lw: 1.5 });
  await iconDot(s, "FaCheck", 0.95, 2.1, 0.6, "FFFFFF", MUTED);
  await iconDot(s, "FaQuestion", 7.18, 2.1, 0.6, "FFFFFF", HOT);
  T(s, "Lo que existe", { x: 1.75, y: 2.15, w: 4.5, h: 0.5, fontFace: THEME.headFontFace, fontSize: 22, bold: true });
  T(s, "Lo que falta", { x: 7.98, y: 2.15, w: 4.5, h: 0.5, fontFace: THEME.headFontFace, fontSize: 22, bold: true, color: HOT });
  const L = [
    ["El LLM como director de juego", "Callison-Burch et al., 2022 · Gallotta et al., 2024"],
    ["Repartir roles mejora historias largas", "Xia et al., 2025"],
    ["Los MAS traen modos de fallo propios", "Cemri et al., 2025"],
  ];
  T(s, L.flatMap(([a, b], i) => [
    { text: a, options: { bold: true, breakLine: true } },
    { text: b, options: { fontSize: 12, color: MUTED, breakLine: i < L.length - 1 } },
  ]), { x: 0.95, y: 3.0, w: 5.3, h: 3.2, paraSpaceAfter: 10 });
  const R = [
    ["Una comparación controlada", "MAS vs. monolítico, misma memoria y mismo modelo"],
    ["En español", "herramientas y datasets son mayormente en inglés"],
    ["En segunda persona e interactiva", "«tú entras en la taberna…», turno a turno"],
  ];
  T(s, R.flatMap(([a, b], i) => [
    { text: a, options: { bold: true, breakLine: true } },
    { text: b, options: { fontSize: 12, color: MUTED, breakLine: i < R.length - 1 } },
  ]), { x: 7.18, y: 3.0, w: 5.3, h: 3.2, paraSpaceAfter: 10 });
  s.addNotes("[1:30–2:30] La literatura ya usa modelos de lenguaje como directores de juego, y propone repartir el trabajo entre agentes especializados, un sistema multiagente, porque mejora las historias largas. Pero también se ha documentado que los sistemas multiagente tienen fallas propias y mejoras a veces mínimas. Lo que no encontramos fue una comparación controlada entre multiagente y monolítico en juegos de rol de mesa. Y menos en español y en narrativa interactiva en segunda persona, donde casi todas las herramientas de evaluación están pensadas para el inglés.");
}

// 4 · Pregunta e hipótesis (la grilla se reutiliza en la conclusión)
const COLS_HIP = [["CR", "Reactiva", "¿responde a lo que acabas de hacer?"], ["CL", "Longitudinal", "¿recuerda personajes y mundo?"], ["QN", "Calidad", "¿interés y respeto a tu agencia?"]];
function gridHip(s, x0, y0, verdicts, cols = COLS_HIP, rows0) {
  const rows = rows0 || [["¿G2 se degrada con los turnos?", ["H1a", "H1b", "H1c"]], ["¿G1 supera a G2?", ["H1d", "H1e", "H1f"]]];
  const cw = 2.85, rh = verdicts ? 0.95 : 1.15, lw = 2.9;
  cols.forEach(([code, name, q], j) => {
    T(s, [{ text: code ? code + " · " + name : name, options: { bold: true, breakLine: true } }, { text: q, options: { fontSize: 12, color: MUTED } }],
      { x: x0 + lw + j * (cw + 0.15), y: y0, w: cw, h: 0.8, fontSize: 15, align: "center" });
  });
  rows.forEach(([q, hs], i) => {
    const y = y0 + 0.95 + i * (rh + 0.15);
    T(s, q, { x: x0, y, w: lw - 0.2, h: rh, valign: "middle", fontSize: 15, bold: true, color: i ? X.dk1 : MUTED });
    hs.forEach((h, j) => {
      const v = verdicts && verdicts[h];
      const x = x0 + lw + j * (cw + 0.15);
      const hot = v && v.kind === "ok";
      box(s, x, y, cw, rh, { fill: hot ? HOT : i ? G1T : SOFT, line: hot ? HOT : i ? G1T : SOFT });
      T(s, v ? [{ text: h + "  ", options: { bold: true } }, { text: v.text }] : h,
        { x, y, w: cw, h: rh, align: "center", valign: "middle", fontSize: v ? 14 : 20, bold: !v, fontFace: v ? undefined : THEME.headFontFace, color: hot ? "FFFFFF" : X.dk1 });
    });
  });
}
function l04() {
  const s = content("PREGUNTA E HIPÓTESIS", "¿Es superior la coherencia narrativa de un sistema multiagente frente a uno monolítico?");
  gridHip(s, 0.6, 1.85, null);
  box(s, 0.6, 5.75, 12.1, 0.75, { fill: "FFFFFF", line: X.dk1, lw: 1.25 });
  T(s, [{ text: "Hipótesis general H1: ", options: { bold: true } }, { text: "se sostiene solo si se sostienen H1d, H1e y H1f." }],
    { x: 0.85, y: 5.75, w: 11.6, h: 0.75, valign: "middle", fontSize: 16 });
  s.addNotes("[2:30–3:15] Nuestra pregunta general es si la coherencia narrativa de un sistema multiagente es superior a la de uno monolítico. La coherencia tiene tres dimensiones: reactiva, longitudinal y calidad narrativa. Y para cada una hacemos dos preguntas. Primera fila: ¿el monolítico se degrada a lo largo de la campaña? Son H1a a H1c. Segunda fila: ¿el multiagente supera al monolítico? Son H1d a H1f. La hipótesis general solo se sostiene si se sostienen las tres comparativas. Esa regla la fijamos antes de ver los datos.");
}

// 5 · Diseño
function l05() {
  const s = content("DISEÑO EXPERIMENTAL", "Mismo escenario, dos arquitecturas; todo lo demás constante");
  label(s, 0.6, 2.3, 2.5, 1.2, "Escenario del par i\nambientación, tono, conflicto, personaje", { fill: SOFT, line: SOFT, fs: 13 });
  label(s, 3.8, 1.75, 2.6, 0.95, "G1 · campaña\n1,400 turnos", { fill: G1T, line: G1, bold: true, fs: 14 });
  label(s, 3.8, 3.1, 2.6, 0.95, "G2 · campaña\n1,400 turnos", { fill: G2T, line: G2, bold: true, fs: 14 });
  label(s, 7.1, 1.75, 2.75, 0.95, "O₁ − O₂ por par\nWilcoxon pareado · H1d–H1f", { fs: 13 });
  label(s, 7.1, 3.1, 2.75, 0.95, "7 bloques de 200 turnos\nPage · H1a–H1c", { fs: 13, dash: "dash" });
  arrow(s, 3.1, 2.75, 3.8, 2.22); arrow(s, 3.1, 3.05, 3.8, 3.57);
  arrow(s, 6.4, 2.22, 7.1, 2.22); arrow(s, 6.4, 3.4, 7.1, 2.55); arrow(s, 6.4, 3.75, 7.1, 3.57, { dash: "dash" });
  // cifras
  [["27", "pares"], ["54", "campañas"], ["75,600", "turnos"]].forEach(([b, l], i) => stat(s, 10.5, 1.65 + i * 1.1, 2.3, b, l, X.dk1, 34));
  // constantes
  T(s, "CONSTANTE DENTRO DEL PAR", { x: 0.6, y: 4.75, w: 6, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: X.accent4 });
  const k = ["modelo gemma-4-31B-it", "base de datos del estado", "extractor", "mecanismo de dados", "personaje jugador", "agente jugador", "extensión"];
  let x = 0.6, y = 5.15;
  k.forEach((t) => {
    const w = 0.105 * t.length + 0.45;
    if (x + w > 12.75) { x = 0.6; y += 0.6; }
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.45, rectRadius: 0.22, fill: { color: SOFT }, line: { color: SOFT } });
    T(s, t, { x, y, w, h: 0.45, align: "center", valign: "middle", fontSize: 13 });
    x += w + 0.15;
  });
  T(s, "Entre pares varían ambientación, tono, conflicto y personaje (27 personajes: 8 principistas · 14 de moral ambigua · 5 sin escrúpulos).", { x: 0.6, y: 6.35, w: 12.1, h: 0.4, fontSize: 12, color: MUTED });
  s.addNotes("[3:15–4:30] El diseño es experimental de medidas repetidas con pares emparejados. Cada uno de los 27 escenarios se genera dos veces: una con G1 y otra con G2. Son 54 campañas de 1,400 turnos, 75,600 turnos en total. Dentro del par todo es igual: el mismo modelo, gemma-4 de 31 mil millones, un solo proveedor con su huella verificada antes de cada tanda, la misma base de datos, el mismo extractor, el mismo mecanismo de dados, el mismo personaje y el mismo agente jugador. Así, cada escenario es su propio control. Para la degradación partimos cada campaña de G2 en 7 bloques y aplicamos la prueba de tendencia de Page; para la comparación, Wilcoxon pareado sobre la diferencia dentro del par, con Holm. El tamaño de 27 pares sale de G*Power: efecto medio, alfa 0.05, potencia 0.81.");
}

// 6 · Las dos arquitecturas
function l06(notes) {
  const s = content("LAS DOS ARQUITECTURAS", "Mismo ciclo del turno; solo cambia quién narra");
  const MOD = { fill: X.dk1, color: "FFFFFF", line: X.dk1 }; // usa el modelo
  const top = [["Estado del mundo\nPostgreSQL", {}], ["Contexto de la escena\nSQL exacto + última escena", {}], ["Agente jugador\nacción + habilidad", MOD], ["Dados\nd20 + modificador", {}]];
  top.forEach(([t, o], i) => {
    const x = 0.6 + i * 3.1;
    label(s, x, 1.6, 2.75, 0.8, t, { fill: SOFT, line: SOFT, fs: 12, ...o });
    if (i < 3) arrow(s, x + 2.75, 2.0, x + 3.1, 2.0);
  });
  // carril G1
  box(s, 0.6, 2.75, 12.1, 1.45, { fill: G1T, line: G1T });
  T(s, "G1\nmulti-\nagente", { x: 0.75, y: 2.75, w: 1.0, h: 1.45, valign: "middle", fontSize: 13, bold: true, color: G1 });
  const roles = [["Enrutador\ncódigo", {}], ["Árbitro\ncódigo; modelo si hace falta", {}], ["Actor de PNJ\nsolo lo que sabe ese PNJ", MOD], ["Agente del mundo\ncódigo + modelo", MOD], ["Narrador\núnica prosa que ves", MOD]];
  roles.forEach(([t, o], i) => {
    const x = 1.85 + i * 2.17;
    label(s, x, 3.0, 1.95, 0.95, t, { fs: 11, line: G1, ...o, ...(o.fill ? { line: G1, fill: G1 } : {}) });
    if (i < 4) arrow(s, x + 1.95, 3.47, x + 2.17, 3.47, { color: G1 });
  });
  // carril G2
  box(s, 0.6, 4.35, 12.1, 1.05, { fill: G2T, line: G2T });
  T(s, "G2\nmonolítico", { x: 0.75, y: 4.35, w: 1.0, h: 1.05, valign: "middle", fontSize: 13, bold: true, color: G2 });
  label(s, 1.85, 4.5, 10.63, 0.75, "Director de juego: en una sola llamada arbitra, interpreta a los PNJ, mueve el mundo y escribe la prosa", { fill: G2, line: G2, color: "FFFFFF", fs: 13 });
  // cierre común
  label(s, 0.6, 5.6, 3.6, 0.75, "Verificación de la narración", { fill: SOFT, line: SOFT, fs: 12 });
  label(s, 4.55, 5.6, 4.6, 0.75, "Extractor de cambios: lista cerrada + cita literal", { ...MOD, fs: 12 });
  arrow(s, 4.2, 5.97, 4.55, 5.97);
  arrow(s, 9.15, 5.97, 9.6, 5.97, { dash: "dash" });
  T(s, "registra en el estado del mundo", { x: 9.7, y: 5.6, w: 3.0, h: 0.75, valign: "middle", fontSize: 12, italic: true, color: MUTED });
  // leyenda
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 6.6, w: 0.22, h: 0.22, fill: { color: X.dk1 }, line: { color: X.dk1 } });
  T(s, "usa el modelo", { x: 0.9, y: 6.57, w: 1.6, h: 0.3, fontSize: 11, color: MUTED });
  s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: 6.6, w: 0.22, h: 0.22, fill: { color: SOFT }, line: { color: X.accent4 } });
  T(s, "código", { x: 2.8, y: 6.57, w: 1.2, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes(notes || "[4:30–5:45] Este es el ciclo de un turno, y es el mismo en los dos brazos. Se lee el estado del mundo desde PostgreSQL, se arma el contexto con consultas SQL exactas y la última escena, el agente jugador declara su acción y los dados se resuelven por código. Lo único que cambia es la franja del medio. En G1 el trabajo se reparte: un enrutador y un árbitro en código, un actor que interpreta a cada personaje no jugador con solo su ficha y lo que ese personaje sabe, un agente del mundo y un narrador, que escribe la única prosa que ve el jugador. En G2, un solo director de juego hace todo en una llamada. Después, en ambos, se verifica la narración y un extractor registra los cambios en la base.");
}

// 7 · Memoria estructurada
async function l07() {
  const s = content("MEMORIA ESTRUCTURADA · COMÚN A G1 Y G2", "Tres candados contra la alucinación del estado del mundo");
  const locks = [
    ["FaListUl", "Lista blanca", "Solo 19 campos del mundo se pueden modificar."],
    ["FaQuoteRight", "Cita literal obligatoria", "Todo cambio extraído debe citar el texto del turno."],
    ["FaBalanceScale", "Magnitudes por personalidad", "Los números los pone una tabla, no el modelo."],
  ];
  for (let i = 0; i < 3; i++) {
    const y = 1.75 + i * 1.3;
    await iconDot(s, locks[i][0], 0.6, y, 0.8, "FFFFFF", X.dk1);
    T(s, locks[i][1], { x: 1.6, y: y - 0.02, w: 4.9, h: 0.4, fontSize: 18, bold: true });
    T(s, locks[i][2], { x: 1.6, y: y + 0.4, w: 4.9, h: 0.6, fontSize: 15, color: MUTED });
  }
  // ejemplo del soborno
  box(s, 6.9, 1.7, 5.8, 3.85, { fill: SOFT, line: SOFT });
  T(s, "Candado 3, en acción", { x: 7.2, y: 1.9, w: 5.2, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: X.accent4 });
  T(s, "«Le ofreces una bolsa de oro al guardia para que mire a otro lado.»", { x: 7.2, y: 2.3, w: 5.2, h: 0.8, fontSize: 16, italic: true });
  [["Guardia de principios", "se ofende", "disposición baja", "FaArrowDown", HOT], ["Guardia corrupto", "no se ofende", "acepta el trato", "FaArrowRight", MUTED]].forEach(([who, what, eff, ic, col], i) => {
    const x = 7.2 + i * 2.65;
    box(s, x, 3.25, 2.45, 2.05, { fill: "FFFFFF", line: LINE });
    T(s, who, { x: x + 0.15, y: 3.4, w: 2.15, h: 0.35, fontSize: 13, bold: true });
    T(s, what, { x: x + 0.15, y: 3.85, w: 2.15, h: 0.45, fontFace: THEME.headFontFace, fontSize: 20, bold: true, color: col });
    T(s, eff, { x: x + 0.15, y: 4.4, w: 2.15, h: 0.35, fontSize: 13, color: MUTED });
  });
  T(s, "Mismo soborno, efecto distinto: lo decide la ficha del PNJ, no el modelo.", { x: 6.9, y: 5.65, w: 5.8, h: 0.35, fontSize: 12, color: MUTED });
  // cifras de la base
  [["77,413", "turnos registrados"], ["17,908", "cambios con evidencia"], ["387", "PNJ"], ["947", "hechos conocidos por PNJ"]].forEach(([b, l], i) => {
    T(s, [{ text: b + " ", options: { bold: true, color: X.dk1, fontSize: 18 } }, { text: l, options: { color: MUTED, fontSize: 12 } }], { x: 0.6 + i * 3.05, y: 6.35, w: 3.0, h: 0.4 });
  });
  s.addNotes("[5:45–6:45] Ambos brazos comparten una memoria estructurada: el mundo vive en una base de datos, no en la memoria del modelo. Para que el modelo no invente cambios hay tres candados. Primero, solo 19 campos se pueden modificar. Segundo, cada cambio que extrae el sistema necesita una cita literal del turno; si el modelo parafrasea, se rechaza. Tercero, las magnitudes las pone una tabla según la personalidad del personaje, no el modelo. Por ejemplo, el mismo soborno ofende a un guardia de principios y no ofende a uno corrupto. Al final quedaron más de 77 mil turnos y casi 18 mil cambios de estado, cada uno con su evidencia.");
}

// 8 · Cómo se midió
function l08() {
  const s = content("INSTRUMENTOS", "Cómo se midió: de la rúbrica a instrumentos validados");
  const steps = [
    ["Rúbrica D&D-IA", "3 dimensiones · 6 indicadores definen qué medir"],
    ["Batería determinista", "mismo texto, mismo resultado; escala a 75,600 turnos"],
    ["Prueba de perturbación", "defectos conocidos · expectativas selladas · δ de Cliff ≥ 0.147 + Holm"],
    ["Clasificación", "confirmatorio · condicionado · exploratorio · descriptivo"],
  ];
  steps.forEach(([h, d], i) => {
    const w = 11.4 - i * 1.3, x = (W - w) / 2, y = 1.65 + i * 1.02;
    const fill = ["2B3150", "3A4166", "4B527A", X.dk1][i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.85, rectRadius: 0.1, fill: { color: fill }, line: { color: fill } });
    T(s, [{ text: (i + 1) + "  " + h + "   ", options: { bold: true, fontSize: 17 } }, { text: d, options: { fontSize: 13, color: "D5D8E3" } }],
      { x: x + 0.3, y, w: w - 0.6, h: 0.85, valign: "middle", color: "FFFFFF", align: "center" });
  });
  arrow(s, W / 2, 5.73, W / 2, 6.0, { color: X.dk1 });
  T(s, [{ text: "Confirmatorios: ", options: { bold: true } }, { text: "CR-2 respuesta a la acción (z) · QN-2 persona2 (condicionado) · " }, { text: "CL-1 y CL-2: ninguno", options: { bold: true, color: HOT } }],
    { x: 0.6, y: 6.05, w: 12.1, h: 0.4, align: "center", fontSize: 15 });
  T(s, "El panel de 5 DM quedó como estudio piloto (14 set 2026, con el asesor). La validación humana se hizo solo con evaluadores externos.", { x: 0.6, y: 6.5, w: 12.1, h: 0.35, align: "center", fontSize: 12, color: MUTED });
  s.addNotes("[6:45–7:45] La rúbrica D&D-IA define los constructos: tres dimensiones y seis indicadores. Un panel de expertos no era viable sobre 75,600 turnos, así que, de acuerdo con el asesor, medimos con una batería de instrumentos deterministas: el mismo texto da siempre el mismo resultado. El panel quedó como estudio piloto. Cada instrumento pasó una prueba de sensibilidad: le inyectamos defectos de efecto conocido, con las expectativas fijadas antes y selladas con SHA-256, y exigimos un tamaño de efecto mínimo con corrección de Holm. Según eso, cada instrumento se clasificó. Solo dos quedaron confirmatorios: la respuesta a la acción específica para la reactiva, y persona2 para la agencia, este último condicionado. Hay que decirlo desde ya: la dimensión longitudinal no tiene ningún confirmatorio.");
}

// 9 · ¿G2 se degrada?
function l09() {
  const s = content("RESULTADOS · H1a–H1c", "G2 no se degradó en 1,400 turnos");
  s.addChart(pres.charts.LINE, [{ name: "G2 · respuesta a la acción (z), mediana", labels: ["1–200", "201–400", "401–600", "601–800", "801–1000", "1001–1200", "1201–1400"], values: zG2 }], {
    x: 0.5, y: 1.6, w: 7.4, h: 4.6, chartColors: [G2], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 9,
    valAxisMinVal: 2.0, valAxisMaxVal: 3.2, valAxisMajorUnit: 0.2, valAxisLabelFormatCode: "0.0",
    showValue: true, dataLabelPosition: "t", dataLabelFormatCode: "0.000", dataLabelColor: X.dk1, dataLabelFontSize: 11,
    showLegend: false, showTitle: true, title: "G2 · respuesta a la acción (z), mediana por bloque", titleFontSize: 13, titleColor: X.dk1, titleFontFace: "+mn-lt",
    showCatAxisTitle: true, catAxisTitle: "turnos", ...AX,
  });
  const rows = [
    ["H1a · reactiva", "2.768 → 2.742 · Page p = 0.310", "no"],
    ["H1b · longitudinal", "sin confirmatorio; el alza de «PNJ inactivo» desaparece al relativizar (p = 0.451)", "na"],
    ["H1c · calidad", "persona2 3.0 % → 3.5 % · p Holm = 0.178", "no"],
  ];
  rows.forEach(([h, d, k], i) => {
    const y = 1.75 + i * 1.35;
    T(s, h, { x: 8.3, y, w: 4.4, h: 0.35, fontSize: 16, bold: true });
    T(s, d, { x: 8.3, y: y + 0.38, w: 4.4, h: 0.85, fontSize: 13, color: MUTED });
  });
  chip(s, 8.3, 5.85, "No se rechaza H0: sin degradación", "no");
  T(s, "Tampoco hay punto de quiebre en los turnos 1,301–1,400 (exploratorio).", { x: 0.6, y: 6.4, w: 7.3, h: 0.35, fontSize: 12, color: MUTED });
  s.addNotes("[7:45–8:45] Primera pregunta: ¿el monolítico se degrada? No. La respuesta a la acción del jugador empieza en 2.768 y termina en 2.742, una línea prácticamente plana; la prueba de Page da p = 0.31. En la longitudinal no hay confirmatorio; el indicador de personajes inactivos parecía subir, pero desaparece al relativizar por cuántos personajes inactivos existen. Y la usurpación en G2 pasa de 3.0 a 3.5 por ciento, sin significancia tras Holm. Revisamos además el último tramo, turnos 1,301 a 1,400, y no hay quiebre. Con una memoria estructurada, el monolítico se sostiene durante 1,400 turnos.");
}

// 10 · Reactiva (H1d)
function l10() {
  const s = content("RESULTADOS · H1d · COHERENCIA REACTIVA", "Empate en lo específico: G1 solo escribe respuestas más largas");
  s.addChart(pres.charts.BAR, [
    { name: "Genérico: se parece a cualquier acción", labels: ["G2", "G1"], values: [0.0305, 0.0396] },
    { name: "Específico: responde a tu acción", labels: ["G2", "G1"], values: [0.0928, 0.0953] },
  ], {
    x: 0.5, y: 1.6, w: 7.6, h: 4.3, barDir: "bar", barGrouping: "stacked", barGapWidthPct: 55,
    chartColors: ["B9BDCB", X.dk1], showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0.000", dataLabelColor: "FFFFFF", dataLabelFontSize: 12,
    valAxisMinVal: 0, valAxisMaxVal: 0.15, valAxisMajorUnit: 0.05, valAxisLabelFormatCode: "0.00", catAxisLabelFontSize: 14,
    showLegend: true, legendPos: "b", showTitle: true, title: "Solapamiento acción–respuesta (mediana de 27 pares)", titleFontSize: 13, titleColor: X.dk1, titleFontFace: "+mn-lt", ...AX,
  });
  const facts = [
    ["Específico", "G1 ≈ G2 · p = 0.59", "Ninguna arquitectura responde mejor a lo que el jugador acaba de hacer."],
    ["Genérico", "G1 > G2 en 27/27 pares", "G1 escribe +16 lemas por turno: más texto, más parecido a cualquier acción."],
    ["Confirmatorio (z)", "G1 2.70 vs G2 2.81 · p = 0.032", "HL −0.13 [−0.25, −0.03]; leve a favor de G2."],
  ];
  facts.forEach(([h, b, d], i) => {
    const y = 1.65 + i * 1.33;
    T(s, h.toUpperCase(), { x: 8.5, y, w: 4.2, h: 0.28, fontSize: 11, bold: true, charSpacing: 2, color: X.accent4 });
    T(s, b, { x: 8.5, y: y + 0.28, w: 4.2, h: 0.4, fontSize: 17, bold: true });
    T(s, d, { x: 8.5, y: y + 0.7, w: 4.2, h: 0.6, fontSize: 12, color: MUTED });
  });
  chip(s, 8.5, 5.75, "H1d · no se sostiene", "no");
  T(s, "G1 sí nombra más su propio mundo (anclaje al escenario, concentrado en nombres propios).", { x: 0.6, y: 6.4, w: 7.5, h: 0.35, fontSize: 12, color: MUTED });
  s.addNotes("[8:45–10:00] La coherencia reactiva mide si la respuesta corresponde a la acción del jugador. El instrumento confirmatorio favorece levemente a G2: 2.70 contra 2.81, p = 0.032. Pero tres versiones crudas favorecían a G1, así que descompusimos la medida. El solapamiento tiene una parte genérica, cuánto se parece la respuesta a cualquier acción, y una parte específica, cuánto responde a esta acción. La parte genérica es mayor en G1 en los 27 pares, porque G1 escribe más largo: unos 16 lemas más por turno. La parte específica no difiere, p = 0.59. Es decir, ninguna arquitectura responde mejor a lo que el jugador acaba de hacer. H1d no se sostiene.");
}

// 11 · Longitudinal (H1e)
async function l11() {
  const s = content("RESULTADOS · H1e · COHERENCIA LONGITUDINAL", "Tres intentos; ninguno llegó a instrumento confirmatorio");
  const tries = [
    ["Jericho-QA", "¿recupera los cambios de estado?", "Pasa 4/4 perturbaciones, pero contra el azar solo discrimina en la condición de los personajes (30–32 % vs 7–9 %)."],
    ["Supervivencia", "¿cuándo menciona a un PNJ no vivo?", "Kaplan-Meier: turno 1,139 en G1 vs 891 en G2 · p = 0.77."],
    ["Semántico", "bge-m3 sobre 457,613 oraciones", "Recall 0.08 frente a 0.05 por azar: casi no detecta cambios de estado."],
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.6 + i * 4.1;
    box(s, x, 1.7, 3.8, 3.5, { fill: SOFT, line: SOFT });
    await iconDot(s, "FaTimes", x + 0.3, 2.0, 0.6, "FFFFFF", X.accent4);
    T(s, tries[i][0], { x: x + 0.3, y: 2.75, w: 3.2, h: 0.45, fontFace: THEME.headFontFace, fontSize: 21, bold: true });
    T(s, tries[i][1], { x: x + 0.3, y: 3.2, w: 3.2, h: 0.5, fontSize: 13, italic: true, color: MUTED });
    T(s, tries[i][2], { x: x + 0.3, y: 3.75, w: 3.25, h: 1.6, fontSize: 14 });
  }
  T(s, [{ text: "Evidencia exploratoria mixta: ", options: { bold: true } }, { text: "coherencia de entidad G1 2.17 vs G2 1.67 (p = 0.017), pero «PNJ inactivo» desfavorece a G1 (p = 0.032) y su versión refinada no es significativa (p = 0.44)." }],
    { x: 0.6, y: 5.65, w: 12.1, h: 0.6, fontSize: 13, color: X.dk1 });
  chip(s, 0.6, 6.35, "H1e · sin decisión confirmatoria", "na");
  T(s, "Siguiente paso: un clasificador NLI en español.", { x: 5.2, y: 6.38, w: 7.5, h: 0.4, fontSize: 13, color: MUTED, align: "right" });
  s.addNotes("[10:00–11:00] La coherencia longitudinal es la más difícil de medir. Lo intentamos por tres caminos. Jericho, que pregunta por los cambios de estado: pasa las perturbaciones, pero contra el azar solo discrimina en los cambios de condición de los personajes. Un análisis de supervivencia: cuándo aparece por primera vez un personaje muerto actuando; G1 tarda más, turno 1,139 contra 891, pero no es significativo. Y un instrumento semántico con embeddings sobre casi 458 mil oraciones, que apenas supera al azar. La evidencia exploratoria es mixta, en ambas direcciones. Lo decimos con honestidad: ningún instrumento llegó a confirmatorio, así que H1e queda sin decisión. El paso siguiente es un clasificador de inferencia textual en español.");
}

// 12 · Agencia (H1f)
function l12() {
  const s = content("RESULTADOS · H1f · RESPETO A LA AGENCIA", "G1 casi nunca decide por el jugador");
  T(s, "0.17 %", { x: 0.6, y: 1.65, w: 4.3, h: 1.2, fontFace: THEME.headFontFace, fontSize: 66, bold: true, color: G1 });
  T(s, "G1 · multiagente", { x: 0.6, y: 2.85, w: 4.3, h: 0.35, fontSize: 15, bold: true, color: G1 });
  T(s, "3.47 %", { x: 0.6, y: 3.35, w: 4.3, h: 1.2, fontFace: THEME.headFontFace, fontSize: 66, bold: true, color: G2 });
  T(s, "G2 · monolítico", { x: 0.6, y: 4.55, w: 4.3, h: 0.35, fontSize: 15, bold: true, color: G2 });
  T(s, "de los turnos el sistema decide, piensa, siente o habla por ti (mediana de 27 pares)", { x: 0.6, y: 5.05, w: 4.3, h: 0.7, fontSize: 13, color: MUTED });
  const xs = pares.map((_, i) => i + 1);
  s.addChart(pres.charts.SCATTER, [{ name: "par", values: xs }, { name: "G1", values: p2G1 }, { name: "G2", values: p2G2 }], {
    x: 5.2, y: 1.55, w: 7.6, h: 3.85, chartColors: [G1, G2], lineSize: 0, lineDataSymbol: "circle", lineDataSymbolSize: 8,
    valAxisMinVal: 0, valAxisMaxVal: 12, valAxisMajorUnit: 3, valAxisLabelFormatCode: "0",
    catAxisMinVal: 0, catAxisMaxVal: 28, catAxisMajorUnit: 3, showLegend: true, legendPos: "t",
    showTitle: true, title: "% de turnos con usurpación, por par", titleFontSize: 13, titleColor: X.dk1, titleFontFace: "+mn-lt",
    showValAxisTitle: true, valAxisTitle: "% de turnos", showCatAxisTitle: true, catAxisTitle: "par (1–27)", ...AX,
  });
  box(s, 5.3, 5.55, 7.4, 1.0, { fill: HOTT, line: HOTT });
  T(s, [{ text: "Corrigiendo cada brazo por su precisión: ", options: { bold: true } }, { text: "G1 < G2 en 27/27 pares; en el peor caso del intervalo, 26/27 (p < 0.0001)." }],
    { x: 5.5, y: 5.55, w: 7.0, h: 1.0, valign: "middle", fontSize: 14 });
  chip(s, 0.6, 5.95, "H1f · se acepta (condicionada)", "ok");
  T(s, "p < 0.0001 tras Holm · r ≈ −1.00 · persona2: confirmatorio condicionado, detecta la usurpación explícita.", { x: 0.6, y: 6.65, w: 12.1, h: 0.3, fontSize: 11, color: MUTED });
  s.addNotes("[11:00–12:30] Y aquí está el resultado principal. Volvemos a la falla del inicio: el sistema que decide por el jugador. Con el instrumento persona2, G2 usurpa la agencia en el 3.47 por ciento de los turnos; G1, en el 0.17 por ciento. En el gráfico, cada punto es un par: G1 está por debajo de G2 en los 27 pares, p menor a 0.0001 tras Holm. Sabemos que persona2 tiene una precisión baja: lo validaron tres directores de juego externos, y frente al evaluador de referencia su precisión es del 33 por ciento. Por eso corregimos la tasa de cada brazo por su propia precisión, 42.9 por ciento en G1 y 28.6 en G2. G1 sigue menor en 27 de 27 pares, y en el peor caso del intervalo, en 26. Cambia la magnitud: en G2 sería entre 0.5 y 1 por ciento. La dirección no cambia. H1f se acepta, condicionada.");
}

// 13 · ¿Gana por gastar más?
function l13(notes) {
  const s = content("OBJECIÓN · COSTO", "¿G1 gana por gastar más? No: más cómputo, más usurpación");
  // dispersión dibujada a mano: dos series con distinto eje X
  const px = { x: 0.9, y: 1.85, w: 6.9, h: 4.0 }, xr = [600, 1200], yr = [0, 12];
  const X2 = (v) => px.x + ((v - xr[0]) / (xr[1] - xr[0])) * px.w, Y2 = (v) => px.y + px.h - ((v - yr[0]) / (yr[1] - yr[0])) * px.h;
  T(s, "Caracteres narrados por turno vs % de turnos con usurpación (pares 07–27)", { x: 0.6, y: 1.45, w: 7.4, h: 0.3, fontSize: 13, bold: true });
  [0, 3, 6, 9, 12].forEach((v) => {
    s.addShape(pres.shapes.LINE, { x: px.x, y: Y2(v), w: px.w, h: 0, line: { color: LINE, width: 0.75 } });
    T(s, v + "%", { x: px.x - 0.55, y: Y2(v) - 0.12, w: 0.45, h: 0.25, fontSize: 11, color: MUTED, align: "right" });
  });
  [600, 800, 1000, 1200].forEach((v) => T(s, String(v), { x: X2(v) - 0.4, y: px.y + px.h + 0.08, w: 0.8, h: 0.25, fontSize: 11, color: MUTED, align: "center" }));
  T(s, "caracteres por turno", { x: px.x, y: px.y + px.h + 0.35, w: px.w, h: 0.25, fontSize: 11, color: MUTED, align: "center" });
  [["G2", dosis("G2"), G2], ["G1", dosis("G1"), G1]].forEach(([, pts, col]) => pts.forEach(([a, b]) => {
    s.addShape(pres.shapes.OVAL, { x: X2(a) - 0.07, y: Y2(b) - 0.07, w: 0.14, h: 0.14, fill: { color: col, transparency: 15 }, line: { color: "FFFFFF", width: 0.5 } });
  }));
  T(s, "G2 · ρ = +0.74", { x: X2(560) + 0.1, y: Y2(11.6), w: 2, h: 0.3, fontSize: 13, bold: true, color: G2 });
  T(s, "G1 · ρ = +0.51", { x: X2(960), y: Y2(1.9), w: 2, h: 0.3, fontSize: 13, bold: true, color: G1 });
  // costo
  T(s, "COSTO DEL LADO DEL DM, G1 / G2", { x: 8.5, y: 1.55, w: 4.2, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: X.accent4 });
  [["2.86 vs 1", "llamadas al modelo por turno"], ["2.6×", "tiempo de modelo"], ["1.5×", "texto narrado"]].forEach(([b, l], i) => stat(s, 8.5, 1.95 + i * 1.05, 4.2, b, l, X.dk1, 28));
  box(s, 8.5, 5.15, 4.2, 1.15, { fill: SOFT, line: SOFT });
  T(s, "Dentro de cada brazo, más cómputo va con más usurpación: lo contrario de lo que exige la objeción.", { x: 8.7, y: 5.15, w: 3.8, h: 1.15, valign: "middle", fontSize: 13 });
  T(s, "La ventaja se atribuye al MAS como paquete. Recomendado: un monolítico con el mismo presupuesto de llamadas.", { x: 0.6, y: 6.5, w: 12.1, h: 0.35, fontSize: 12, color: MUTED });
  s.addNotes(notes || "[12:30–13:15] Una objeción obvia es que G1 gana porque gasta más. Es cierto que gasta más: casi tres llamadas al modelo por turno contra una, 2.6 veces más tiempo de modelo y 1.5 veces más texto. Pero si el cómputo fuera la causa, dentro de cada brazo las campañas que más gastan deberían usurpar menos. Pasa lo contrario: en ambos brazos, más texto narrado va con más usurpación, con correlaciones de Spearman de 0.51 en G1 y 0.74 en G2. Por eso atribuimos la ventaja al diseño multiagente como paquete, y dejamos recomendado comparar contra un monolítico con el mismo presupuesto de llamadas.");
}

// 14 · Conclusión
function l14() {
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Exposición" });
  T(s, "CONCLUSIÓN", { x: 0.7, y: 0.55, w: 6, h: 0.35, fontSize: 12, bold: true, charSpacing: 3, color: X.accent4 });
  T(s, [
    { text: "Con una memoria estructurada común, especializar agentes " },
    { text: "no mejoró la coherencia medible", options: { color: X.accent4 } },
    { text: ", pero " },
    { text: "sí redujo que el sistema decida por el jugador.", options: { color: "F08A5D" } },
  ], { x: 0.7, y: 1.1, w: 11.9, h: 2.2, fontFace: THEME.headFontFace, fontSize: 32, bold: true, color: "FFFFFF", lineSpacingMultiple: 1.05 });
  const v = [["H1a–c · G2 se degrada", "no"], ["H1d · reactiva", "no se sostiene"], ["H1e · longitudinal", "sin decisión"], ["H1f · agencia", "se acepta*"]];
  v.forEach(([h, r], i) => {
    const x = 0.7 + i * 3.0, hot = i === 3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.85, w: 2.8, h: 1.35, rectRadius: 0.08, fill: { color: hot ? HOT : "222944" }, line: { color: hot ? HOT : "2E365A" } });
    T(s, h, { x: x + 0.2, y: 4.0, w: 2.4, h: 0.4, fontSize: 13, color: hot ? "FFFFFF" : X.accent4 });
    T(s, r, { x: x + 0.2, y: 4.45, w: 2.4, h: 0.6, fontFace: THEME.headFontFace, fontSize: 22, bold: true, color: "FFFFFF" });
  });
  T(s, [{ text: "Hipótesis general: no se sostiene", options: { bold: true, color: "FFFFFF" } }, { text: "  ·  la ventaja del MAS es específica, en la agencia del jugador.   * condicionada a la precisión de persona2", options: { color: X.accent4 } }],
    { x: 0.7, y: 5.6, w: 11.9, h: 0.6, fontSize: 15 });
  s.addNotes("[13:15–14:15] En conclusión: con una memoria estructurada común, especializar agentes no mejoró la coherencia que hoy podemos medir. El monolítico no se degrada, la reactiva no favorece a G1 y la longitudinal queda sin decisión. Por la regla que fijamos al inicio, la hipótesis general no se sostiene. Pero sí hay una ventaja clara y específica: separar los roles reduce que el sistema decida, piense, sienta o hable por el jugador, y eso se mantiene incluso corrigiendo por la precisión del detector.");
}

// 15 · Aportes y trabajo futuro
async function l15() {
  const s = content("APORTES Y TRABAJO FUTURO", "Un resultado negativo controlado que dice dónde vale especializar");
  const A = [
    ["FaDatabase", "Corpus en español", "54 campañas, 75,600 turnos en segunda persona, con el estado del mundo y su evidencia"],
    ["FaRulerCombined", "Batería validada", "instrumentos deterministas probados por perturbación y contrastados con evaluadores externos"],
    ["FaCompass", "Guía de diseño", "con buena memoria estructurada, especializar sirve para la agencia, no para la coherencia"],
  ];
  const F = [
    ["FaProjectDiagram", "Clasificador NLI en español", "para tener un confirmatorio longitudinal"],
    ["FaUsers", "Jugadores humanos", "en lugar del agente jugador"],
    ["FaEquals", "Monolítico con el mismo presupuesto", "de llamadas que el MAS"],
  ];
  T(s, "APORTES", { x: 0.6, y: 1.6, w: 5.8, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: X.accent4 });
  T(s, "TRABAJO FUTURO", { x: 7.0, y: 1.6, w: 5.7, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: X.accent4 });
  for (let i = 0; i < 3; i++) {
    const y = 2.05 + i * 1.5;
    await iconDot(s, A[i][0], 0.6, y, 0.7, "FFFFFF", X.dk1);
    T(s, A[i][1], { x: 1.5, y, w: 5.0, h: 0.4, fontSize: 17, bold: true });
    T(s, A[i][2], { x: 1.5, y: y + 0.42, w: 5.0, h: 0.8, fontSize: 13, color: MUTED });
    await iconDot(s, F[i][0], 7.0, y, 0.7, X.dk1, SOFT);
    T(s, F[i][1], { x: 7.9, y, w: 4.8, h: 0.4, fontSize: 17, bold: true });
    T(s, F[i][2], { x: 7.9, y: y + 0.42, w: 4.8, h: 0.8, fontSize: 13, color: MUTED });
  }
  s.addNotes("[14:15–15:00] ¿Qué deja esta tesis? Primero, un corpus de 75,600 turnos en español y en segunda persona, con el estado del mundo y la evidencia de cada cambio. Segundo, una batería de instrumentos deterministas validada por perturbación y contrastada con evaluadores externos. Y tercero, un resultado negativo controlado que orienta el diseño: con buena memoria estructurada, especializar agentes vale para respetar la agencia del jugador, no para ganar coherencia. Como trabajo futuro: un clasificador de inferencia textual en español para la dimensión longitudinal, jugadores humanos, y un monolítico con el mismo presupuesto de llamadas. Muchas gracias; quedamos atentos a sus preguntas.");
}

// 16 · Gracias
function l16() {
  const s = pres.addSlide({ masterName: "OSCURO", sectionTitle: "Exposición" });
  T(s, "Gracias", { x: 0.7, y: 2.2, w: 8, h: 1.2, fontFace: THEME.headFontFace, fontSize: 54, bold: true, color: "FFFFFF" });
  T(s, "¿Preguntas?", { x: 0.7, y: 3.4, w: 8, h: 0.7, fontSize: 26, color: X.accent4 });
  T(s, "Marin Yupanqui, Bryan Arturo · Mostacero Cieza, Luis David", { x: 0.7, y: 6.3, w: 9, h: 0.35, fontSize: 13, color: X.accent4 });
  motifG1(s, 9.4, 2.3, 1.6, G1);
  motifG2(s, 11.55, 3.25, 0.65, G2);
  s.addNotes("Pausa para preguntas. Las láminas de respaldo siguen a continuación (dados, potencia, validación de persona2, auditoría de nombres, Jericho, Kaplan-Meier, semántico, último bloque, base de datos, rúbrica e instrumentos).");
}

// ================================================================ RESPALDO
function backup(title) { return content("RESPALDO", title, "Respaldo"); }
function cardsRow(s, items, y = 1.8, h = 2.3) {
  const n = items.length, gap = 0.3, w = (12.1 - gap * (n - 1)) / n;
  items.forEach(([big, lab, sub, col], i) => {
    const x = 0.6 + i * (w + gap);
    box(s, x, y, w, h, { fill: SOFT, line: SOFT });
    T(s, big, { x: x + 0.3, y: y + 0.3, w: w - 0.6, h: 0.8, fontFace: THEME.headFontFace, fontSize: big.length > 9 ? 24 : 32, bold: true, color: col || X.dk1 });
    T(s, lab, { x: x + 0.3, y: y + 1.1, w: w - 0.6, h: 0.4, fontSize: 14, bold: true });
    if (sub) T(s, sub, { x: x + 0.3, y: y + 1.5, w: w - 0.6, h: h - 1.6, fontSize: 12, color: MUTED });
  });
}
function noteLine(s, text, y = 4.5) { T(s, text, { x: 0.6, y, w: 12.1, h: 1.6, fontSize: 15 }); }

function b01() {
  const s = backup("Dados: mismo mecanismo, sin ventaja para ningún brazo");
  cardsRow(s, [["4,824", "tiradas comparables", "pares de tiradas en la misma posición"], ["4.7 %", "coinciden", "el azar da 5 %"], ["p = 0.946", "d20 medio G1 vs G2", "Wilcoxon pareado"]]);
  noteLine(s, "La semilla incluye el ID de la campaña, así que las secuencias de los dos brazos no son idénticas. Lo que es igual es el mecanismo (d20 + modificador, determinista), y la suerte no favoreció a ninguno.");
  s.addNotes("Si preguntan por los dados: no recibieron la misma secuencia, recibieron el mismo mecanismo. La coincidencia es la del azar y el d20 medio no difiere.");
}
function b02() {
  const s = backup("Potencia estadística");
  cardsRow(s, [["N = 27", "pares", "G*Power a priori · dz = 0.5 · α = 0.05"], ["0.81", "potencia unilateral", "t pareada (contraste declarado)"], ["≈ 0.79", "con Wilcoxon", "unilateral"], ["0.71", "bilateral", "solo como complemento"]]);
  noteLine(s, "El contraste declarado es unilateral (H1: G1 supera a G2). El bilateral se reporta como complemento, no como criterio de decisión.");
  s.addNotes("La potencia de 0.81 corresponde al contraste unilateral que se declaró de antemano.");
}
function b03() {
  const s = backup("Validación humana externa: persona2 y PNJ inactivo");
  box(s, 0.6, 1.7, 5.9, 4.6, { fill: SOFT, line: SOFT }); box(s, 6.83, 1.7, 5.9, 4.6, { fill: SOFT, line: SOFT });
  T(s, "persona2 (QN-2)", { x: 0.9, y: 1.9, w: 5.3, h: 0.45, fontFace: THEME.headFontFace, fontSize: 20, bold: true });
  T(s, [
    { text: "3 DM externos etiquetaron a ciegas 102 ítems", options: { breakLine: true } },
    { text: "Acuerdo entre ellos nulo: Fleiss κ = −0.09", options: { breakLine: true } },
    { text: "Con el criterio de calidad queda un evaluador de referencia", options: { breakLine: true } },
    { text: "Precisión 33.3 % [21.0–48.4]; pasada asistida 25.6 %", options: { breakLine: true, bold: true } },
    { text: "Por brazo: 42.9 % en G1 · 28.6 % en G2", options: { breakLine: true } },
    { text: "Detecta la usurpación explícita; exhaustividad baja", options: {} },
  ], { x: 0.9, y: 2.5, w: 5.4, h: 3.6, fontSize: 14, paraSpaceAfter: 8 });
  T(s, "Detector de PNJ inactivo (CL-2)", { x: 7.13, y: 1.9, w: 5.3, h: 0.45, fontFace: THEME.headFontFace, fontSize: 20, bold: true });
  T(s, [
    { text: "3 evaluadores externos · 60 turnos → 59 casos únicos", options: { breakLine: true } },
    { text: "Se excluyó a uno por respuesta apresurada", options: { breakLine: true } },
    { text: "E1–E3: κ = 0.595 · AC1 = 0.593", options: { breakLine: true, bold: true } },
    { text: "Precisión 62.5 % · exhaustividad 40 %", options: {} },
  ], { x: 7.13, y: 2.5, w: 5.4, h: 3.6, fontSize: 14, paraSpaceAfter: 8 });
  T(s, "Los autores nunca etiquetaron. persona2 sigue como confirmatorio condicionado: la corrección por precisión cambia la magnitud de H1f, no su dirección.", { x: 0.6, y: 6.4, w: 12.1, h: 0.45, fontSize: 12, color: MUTED });
  s.addNotes("Si preguntan cómo se acepta H1f con 33 % de precisión: se corrigió la tasa de cada brazo por su propia precisión y G1 sigue menor en 27/27 pares (peor caso 26/27). Kappa mide confiabilidad; la validez se buscó por perturbación y contraste con juicio humano externo.");
}
function b04() {
  const s = backup("Auditoría censal de nombres no reconocidos (OE-1)");
  cardsRow(s, [["9,629", "marcas auditadas", "censo completo, no muestra"], ["4–11×", "sobrestimación", "la tasa bruta exagera la invención"], ["10.2 %", "en G2", "solo esas son menciones efímeras candidatas"], ["0.29 % vs 0.93 %", "turnos con candidatas", "G1 vs G2 · p = 0.019 (exploratorio)"]]);
  noteLine(s, "El indicador de «nombre no reconocido» no distinguía invención de personajes legítimos. La auditoría lo separa: la mayoría de las marcas son nombres válidos. Brecha cerrada en su alcance.");
  s.addNotes("OE-1: la tasa bruta sobrestima la invención entre 4 y 11 veces. G1 tiene menos candidatas, pero es exploratorio.");
}
function b05() {
  const s = backup("Jericho-QA por tipo de cambio (OE-2)");
  cardsRow(s, [["4 / 4", "perturbaciones superadas", "prueba de sensibilidad"], ["30–32 %", "recall en condición de personajes", "contra 7–9 % por azar"], ["≈ azar", "en los demás tipos de cambio", "no discrimina"]]);
  noteLine(s, "Jericho pasa la prueba de sensibilidad, pero contra el azar solo discrimina en los cambios de condición de los personajes. Por eso sigue como exploratorio y no decide H1e.");
  s.addNotes("OE-2: Jericho queda exploratorio.");
}
function b06() {
  const s = backup("Supervivencia: primera mención de un PNJ no vivo");
  const tG1 = pares.map((r) => +r.t_pnj__G1), tG2 = pares.map((r) => +r.t_pnj__G2);
  const k1 = km(tG1), k2 = km(tG2);
  const xs = [...new Set([...k1, ...k2].map((p) => p[0]))].sort((a, b) => a - b);
  // escalones sobre un eje X común: valor de cada curva justo a la derecha de t
  const at = (k, t) => { let v = 1; for (const [a, b] of k) if (a <= t) v = b; return v; };
  const X3 = [], y1 = [], y2 = [];
  xs.forEach((t) => {
    X3.push(t); y1.push(r3(at(k1.filter(([a]) => a < t), t))); y2.push(r3(at(k2.filter(([a]) => a < t), t)));
    X3.push(t); y1.push(r3(at(k1, t))); y2.push(r3(at(k2, t)));
  });
  s.addChart(pres.charts.SCATTER, [{ name: "turno", values: X3 }, { name: "G1 · mediana turno 1,139", values: y1 }, { name: "G2 · mediana turno 891", values: y2 }], {
    x: 0.5, y: 1.55, w: 8.2, h: 4.9, chartColors: [G1, G2], lineSize: 2.5, lineDataSymbol: "none",
    valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.2, valAxisLabelFormatCode: "General", catAxisMinVal: 0, catAxisMaxVal: 1400, catAxisMajorUnit: 200,
    showLegend: true, legendPos: "b", showTitle: true, title: "Fracción de campañas sin mención de un PNJ no vivo", titleFontSize: 13, titleColor: X.dk1, titleFontFace: "+mn-lt",
    showCatAxisTitle: true, catAxisTitle: "turno", ...AX,
  });
  [["1,139 vs 891", "turno mediano del primer evento (G1 vs G2)"], ["16 / 27", "campañas con evento en cada brazo"], ["p = 0.77", "log-rank"]].forEach(([b, l], i) => stat(s, 9.1, 1.7 + i * 1.5, 3.7, b, l, X.dk1, 28));
  s.addNotes("Kaplan-Meier: G1 tarda más en mencionar un PNJ no vivo como si actuara, pero la diferencia no es significativa (log-rank p = 0.77). Exploratorio.");
}
function b07() {
  const s = backup("Capa semántica: v1 y v2");
  cardsRow(s, [["457,613", "oraciones", "bge-m3, sobre los mismos turnos"], ["v1 → v2", "control de la mención", "v1 se encendía con solo nombrar al PNJ; v2 compara solo oraciones que lo mencionan"], ["0.30 → 0.08", "recall", "con la mención controlada; azar 0.05"]], 1.8, 2.5);
  noteLine(s, "pgvector se usó solo después, como capa de medición; no intervino en la generación y no se regeneró ninguna campaña. La brecha G1–G2 de la v1 era un artefacto de la mención.", 4.7);
  s.addNotes("Si preguntan por embeddings: se usaron solo para medir, después. La v2 deja el recall casi en el azar, así que no decide.");
}
function b08() {
  const s = backup("Último bloque: turnos 1,301–1,400");
  cardsRow(s, [["0", "indicadores que empeoran tras Holm", "bloques de 100 turnos, n = 27 por brazo"], ["2.65", "mínimo de G2 en respuesta a la acción", "sin significancia (p = 0.35)"], ["→", "base para probar más turnos", "campañas de más de 1,400 turnos"]]);
  noteLine(s, "Análisis exploratorio: no hay punto de quiebre al final de las campañas.");
  s.addNotes("No hay quiebre al final; el mínimo de G2 no es significativo.");
}
function b09() {
  const s = backup("La base de datos del estado del mundo");
  cardsRow(s, [["77,413", "turnos registrados"], ["17,908", "cambios con evidencia"], ["387", "PNJ"], ["1,725", "lugares"], ["2,890", "objetos"]], 1.75, 1.6);
  T(s, [
    { text: "Mundo: ", options: { bold: true } }, { text: "lugares, facciones, relojes de facción, misiones", options: { breakLine: true } },
    { text: "PNJ: ", options: { bold: true } }, { text: "fichas, disposición, conocimiento (947 hechos), secretos", options: { breakLine: true } },
    { text: "Cambios: ", options: { bold: true } }, { text: "campos modificables (19) y libro de cambios de solo añadir, con la cita de cada uno", options: { breakLine: true } },
    { text: "Contexto: ", options: { bold: true } }, { text: "consultas SQL exactas + la última escena narrada; nadie recibe el historial completo", options: {} },
  ], { x: 0.6, y: 3.7, w: 12.1, h: 2.6, fontSize: 15, paraSpaceAfter: 10 });
  s.addNotes("La memoria es el estado estructurado del mundo consultado con SQL exacto; ambos brazos reciben la misma información.");
}
function b10() {
  const s = backup("Rúbrica D&D-IA: 3 dimensiones, 6 indicadores");
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: X.dk1 } } });
  const rows = [
    [H("Dimensión"), H("Indicador"), H("Confirmatorio final")],
    ["Coherencia reactiva (CR)", "CR-1 · Fluidez", "—"],
    ["", "CR-2 · Arraigo a la acción", { text: "Respuesta a la acción específica (z)", options: { bold: true } }],
    ["Coherencia longitudinal (CL)", "CL-1 · Consistencia de personajes", { text: "ninguno", options: { color: HOT } }],
    ["", "CL-2 · Consistencia de eventos y del mundo", { text: "ninguno", options: { color: HOT } }],
    ["Calidad narrativa (QN)", "QN-1 · Interés y diversidad", "—"],
    ["", "QN-2 · Respeto a la agencia del jugador", { text: "persona2 (condicionado)", options: { bold: true } }],
  ];
  s.addTable(rows, { x: 0.6, y: 1.7, w: 12.1, colW: [3.6, 4.6, 3.9], fontSize: 14, color: X.dk1, border: { type: "solid", pt: 0.75, color: LINE }, rowH: 0.6, valign: "middle", margin: 0.1 });
  s.addNotes("La rúbrica define los constructos; los instrumentos los operacionalizan.");
}
function b11() {
  const s = backup("Instrumentos y su clasificación");
  const defs = [["Confirmatorio", "sostiene la decisión", HOT], ["Condicionado", "pasó la perturbación; concordancia humana no establecida", G2], ["Exploratorio", "orienta, no decide", X.accent4], ["Descriptivo", "sin contraste", "B9BDCB"]];
  defs.forEach(([h, d, col], i) => {
    const x = 0.6 + i * 3.1;
    s.addShape(pres.shapes.OVAL, { x, y: 1.75, w: 0.3, h: 0.3, fill: { color: col }, line: { color: col } });
    T(s, h, { x: x + 0.42, y: 1.7, w: 2.6, h: 0.35, fontSize: 15, bold: true });
    T(s, d, { x: x + 0.42, y: 2.05, w: 2.55, h: 0.7, fontSize: 12, color: MUTED });
  });
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: X.dk1 } } });
  s.addTable([
    [H("Instrumento"), H("Indicador"), H("Clase")],
    ["Respuesta a la acción específica (z)", "CR-2", "Confirmatorio"],
    ["persona2: usurpación explícita de la agencia", "QN-2", "Confirmatorio condicionado"],
    ["Coherencia de entidad · PNJ inactivo mencionado", "CL-1 / CL-2", "Exploratorio"],
    ["Jericho-QA · supervivencia · semántico (bge-m3)", "CL-2", "Exploratorio"],
    ["Nombres no reconocidos · diversidad léxica (MATTR)", "CR / QN-1", "Exploratorio"],
  ], { x: 0.6, y: 2.95, w: 12.1, colW: [6.4, 2.2, 3.5], fontSize: 14, color: X.dk1, border: { type: "solid", pt: 0.75, color: LINE }, rowH: 0.55, valign: "middle", margin: 0.1 });
  s.addNotes("Cada instrumento se validó con perturbaciones: expectativas fijadas antes con SHA-256, δ de Cliff ≥ 0.147 y Holm.");
}

// ================================================================ build
if (require.main === module) (async () => {
  l01(); await l02(); await l03(); l04(); l05(); l06(); await l07(); l08(); l09(); l10(); await l11(); l12(); l13(); l14(); await l15(); l16();
  pres.addSection({ title: "Respaldo" });
  b01(); b02(); b03(); b04(); b05(); b06(); b07(); b08(); b09(); b10(); b11();
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("OK", OUT);
})().catch((e) => { console.error(e); process.exit(1); });

module.exports = { pres, THEME, X, INK, G1, G2, HOT, MUTED, LINE, SOFT, G1T, G2T, HOTT, W, C, applyTheme,
  T, box, label, arrow, chip, content, stat, iconDot, icon, motifG1, motifG2, gridHip, setSection, AX,
  pares, p2G1, p2G2, zG2,
  l06, l09, l10, l11, l12, l13, l16, b01, b02, b03, b04, b05, b06, b07, b08, b09, b10, b11 };
