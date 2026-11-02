# Papers de referencia — instrumentos de medición determinística

Contexto para Claude Code: estos son los papers que respaldan cada instrumento
determinístico implementado (o evaluado y descartado) en `motor/orquestador/reporte_validacion.py`,
tal como quedaron documentados en `claude/plan-cierre-investigacion.md`
(sección "Fase 0b — Herramientas determinísticas nuevas", research 2026-09-14).

**Nivel de confianza de cada enlace:** todos los enlaces de abajo se verificaron por
búsqueda web el 2026-09-18 y apuntan al paper correcto por título/autores/año. Donde el
venue exacto (conferencia/journal) todavía no está 100% confirmado para citar en la
tesis, lo marco explícitamente — no asumir que está cerrado solo porque hay un link.

---

## 1. CR-1 — Grammaticality (vía LanguageTool) · `reporte_validacion.py` sección 7

**Roemmele, M. & Gordon, A. S.** — *"Evaluating Story Generation Systems Using Automated
Linguistic Analyses"*

- PDF directo (sitio de la autora): https://roemmele.github.io/publications/fiction_generation.pdf
- Semantic Scholar: https://www.semanticscholar.org/paper/Evaluating-Story-Generation-Systems-Using-Automated-Roemmele-Gordon/cf222683dd06990d76da48612c4dbe72d62f968d

⚠️ **Venue sin confirmar todavía** (pendiente desde el 2026-09-14, ver plan doc) — el PDF
está alojado en el sitio personal de la autora, sin conferencia/journal claramente
impreso en los resultados de búsqueda. Antes de citarlo en la tesis, confirmar
venue exacto (posible workshop/simposio de KDD/AAAI en generación de historias).

## 2. CL-1 — Entity Coreference Rate · sección 6

Mismo paper que CR-1 (Roemmele & Gordon) — el proyecto usa el mismo trabajo como
respaldo para ambos indicadores (proporción de entidades que corefieren con el
contexto vs. análisis lingüístico automatizado).

## 3. CR-2 (complementario, vía spaCy) · sección 8, y `cr2_entidad_grafo_densidad` · sección 1

**Smith, K. S., Aziz, W. & Specia, L. (2016)** — *"Cohere: A Toolkit for Local Coherence"*, LREC 2016

- ACL Anthology: https://aclanthology.org/L16-1649/
- PDF directo (LREC): http://www.lrec-conf.org/proceedings/lrec2016/pdf/923_Paper.pdf

Reimplementa el método de:

**Guinaudeau, C. & Strube, M. (2013)** — *"Graph-based Local Coherence Modeling"*,
Proceedings of the 51st Annual Meeting of the ACL (Volume 1: Long Papers), pp. 93–103

- ACL Anthology: https://aclanthology.org/P13-1010/ (PDF en el mismo link)

El proyecto no instaló el toolkit de Smith/Aziz/Specia (centrado en inglés/Stanford
CoreNLP) — se implementó una versión equivalente con spaCy `es_core_news_sm`, mismo
principio (lematización real en vez de match por substring).

**Nota de nomenclatura pendiente (ya anotada en el plan):** `cr2_entidad_grafo_densidad`
(código, = Guinaudeau & Strube, sección 1 y 8) y "CR-2" en la Rúbrica humana
(= arraigo contextual de Zhu et al. 2023) son instrumentos DISTINTOS con el mismo
nombre corto — hay que renombrar uno antes de la redacción final.

## 4. QN-1 — Novedad estructural (diferido, no implementado)

**Peinado, F. et al. (2010)** — *"Assessing the Novelty of Computer-Generated
Narratives Using Empirical Metrics"*, Minds and Machines, 20(4), 565–588

- Springer: https://link.springer.com/article/10.1007/s11023-010-9209-8

Dominio de origen (cuentos folclóricos) distinto al corpus D&D — requiere adaptación
de diseño, no es plug-and-play. Sigue diferido.

## 5. QN-2 — sin candidato determinístico validado

CHADPOD/GAMES 2024 se documentó como "el único método publicado" pero rechazado por
ser un clasificador entrenado, no una regla determinística.

⚠️ **No pude confirmar/localizar esta referencia por búsqueda web** — puede ser un
nombre abreviado/informal que se anotó en la bitácora QM original sin el título
completo, o el venue exacto es distinto a como quedó anotado. Si Claude Code o tú lo
necesitan para la tesis, hay que recuperarlo de la bitácora QM (punto donde se hizo
esta investigación, 2026-09-14) en vez de asumir el link. Por ahora QN-2 sigue como
límite reconocido del instrumento, sin cita verificada.

## 6. Jericho-QA State Graph EM/F1 · sección 5

Candidato más probable (por año + Jericho + Ammanabrolu como coautor):

**Hausknecht, M., Ammanabrolu, P., Côté, M.-A. & Yuan, X. (2020)** — *"Interactive
Fiction Games: A Colossal Adventure"*, AAAI 2020 (introduce el framework/entorno Jericho)

- arXiv: https://arxiv.org/abs/1909.05398
- AAAI (versión de conferencia): https://ojs.aaai.org/index.php/AAAI/article/view/6297
- Microsoft Research: https://www.microsoft.com/en-us/research/publication/interactive-fiction-games-a-colossal-adventure/

⚠️ En el plan doc está anotado de forma abreviada como "Ammanabrolu et al., 2020",
pero el primer autor de este paper es Hausknecht, no Ammanabrolu. Antes de citarlo
en la tesis, confirmar si la intención original era este paper (el que efectivamente
introduce Jericho) o algún otro trabajo de Ammanabrolu de 2020 sobre grafos de
conocimiento/state tracking en ficción interactiva (p. ej. líneas de trabajo sobre
KG-A2C). Vale la pena que Claude Code revise la bitácora QM original si necesita
cerrar esto con certeza.

## 7. Papalampidi C/V (coherencia y consistencia de entidades) · sección 4

**Papalampidi, P., Cao, K. & Kočiský, T. (2022)** — *"Towards Coherent and Consistent
Use of Entities in Narrative Generation"*, Proceedings of the 39th International
Conference on Machine Learning (ICML), PMLR 162

- PMLR (versión oficial): https://proceedings.mlr.press/v162/papalampidi22a.html
- arXiv: https://arxiv.org/abs/2202.01709 (PDF: https://arxiv.org/pdf/2202.01709)

Ya está en el proyecto como archivo: `Towards Coherent and Consistent Use of Entities
in Narrative Generation.pdf`.

## 8. Base entity-grid citada dentro de Papalampidi/Guinaudeau

**Barzilay, R. & Lapata, M. (2008)** — *"Modeling Local Coherence: An Entity-Based
Approach"*, Computational Linguistics, 34(1), 1–34

- ACL Anthology: https://aclanthology.org/J08-1001/ (PDF: https://aclanthology.org/J08-1001.pdf)
- MIT Press: https://direct.mit.edu/coli/article/34/1/1/1969/Modeling-Local-Coherence-An-Entity-Based-Approach

Ya está en el proyecto como archivo: `Modeling Local Coherence.pdf`.

---

## Panel humano (histórico — NO parte del pivote determinístico, incluido para contraste)

Fuente de la Rúbrica D&D-IA v2 (`Rubrica_DnD-IA_Instrumento_Evaluacion_v2.md`, ya en el proyecto):

**Zhu, A., Aggarwal, K., Feng, A., Martin, L. J. & Callison-Burch, C. (2023)** —
*"FIREBALL: A Dataset of Dungeons and Dragons Actual-Play with Structured Game State
Information"*, ACL 2023 (Volume 1: Long Papers), 4171–4193

- ACL Anthology: https://aclanthology.org/2023.acl-long.229/

**Zhou, P., Zhu, A., Hu, J., Pujara, J., Ren, X., Callison-Burch, C., Choi, Y. &
Ammanabrolu, P.** — *"I Cast Detect Thoughts: Learning to Converse and Guide with
Intents and Theory-of-Mind in Dungeons and Dragons"*

- ACL Anthology (ACL 2023, Long Papers): https://aclanthology.org/2023.acl-long.624/

⚠️ La Rúbrica del proyecto lo cita como "Zhou et al. (2022)" (probablemente por el año
del preprint/arXiv), pero la versión de conferencia indexada en ACL Anthology es
**ACL 2023**, no EMNLP 2022 — vale la pena unificar el año antes de la redacción final
de la tesis para que coincida con la cita bibliográfica real.

**Pan, Z., Andronis, A., Hayek, E., Wilkinson, O. A. P., Lasy, I., Parry, A., Gadney,
G., Smith, T. J. & Grierson, M. (2025)** — *"Guiding Generative Storytelling with
Knowledge Graphs"*, International Journal of Human-Computer Interaction

- DOI: https://doi.org/10.1080/10447318.2025.2603634

**Callison-Burch, C., Tomar, G. S., Martin, L. J., Ippolito, D., Bailis, S. & Reitter,
D. (2022)** — *"Dungeons and Dragons as a Dialog Challenge for Artificial
Intelligence"*, EMNLP 2022, 9379–9393 (fuente de los coeficientes de confiabilidad
Randolph Kappa/Tau de Kendall usados en la Rúbrica para QN-1/CR-1/CR-2)

- ACL Anthology: https://aclanthology.org/2022.emnlp-main.637/
- arXiv: https://arxiv.org/abs/2210.07109

---

## Diferidos / no implementados (mencionados en el plan como trabajo futuro, no bloquean nada)

**IFEval** (cumplimiento de formato) — no buscado todavía, pedir si se necesita.

**Welleck, S. et al. (2019)** — *"Dialogue Natural Language Inference"*
(candidato para Dialogue NLI Persona Contradiction Rate — "aplicabilidad media",
requiere modelo NLI en español)

- arXiv: https://arxiv.org/abs/1811.00671

**Urbanek, J. et al. (2019)** — *"Learning to Speak and Act in a Fantasy Text
Adventure Game"* (paper de LIGHT, candidato para LIGHT Action-Dialogue Consistency)

- arXiv: https://arxiv.org/abs/1903.03094

**Li, J., Galley, M., Brockett, C., Gao, J. & Dolan, B. (2016)** — *"A
Diversity-Promoting Objective Function for Neural Conversation Models"*, NAACL 2016
(ya está en el proyecto como `A DiversityPromoting Objective Function for Neural
Conversation Models.pdf` — candidato tangencial para métricas de diversidad/novedad)

- ACL Anthology: https://aclanthology.org/N16-1014/
- arXiv: https://arxiv.org/abs/1510.03055

⚠️ **De Lima et al. (2023)**, citado en la tesis (sección Discusión de resultados,
OE-2) sobre dificultad de preservar continuidad de entidades nombradas en sistemas de
generación narrativa de contexto extendido — no lo pude localizar con confianza por
búsqueda web (varios candidatos no coincidentes). Si Claude Code lo necesita,
recuperar del gestor de referencias del proyecto (Zotero, según `ways-of-working.md`)
en vez de asumir un link.

---

## Ya disponibles como PDF en el proyecto (no requieren descarga)

Estos ya están subidos al proyecto de Claude — Claude Code no tiene acceso directo al
proyecto de claude.ai, así que si los necesita en su máquina, mejor descargarlos de
los links de arriba en vez de pedírtelos a ti:

- `Towards Coherent and Consistent Use of Entities in Narrative Generation.pdf` (Papalampidi et al. 2022)
- `Modeling Local Coherence.pdf` (Barzilay & Lapata 2008)
- `FIREBALL.pdf` (Zhu et al. 2023)
- `Dialogue Natural Lenguage Inference.pdf` (Welleck et al. 2019)
- `A DiversityPromoting Objective Function for Neural Conversation Models.pdf` (Li et al. 2016)
- `Learning to Memorize Enailment and Discourse Relations for PersonaConsistent Dialogues.pdf` (Chen et al. 2023)
- `RPGBench.pdf`
- `RAG.pdf`, `GRAPHRAG.pdf`, `LIGHTRAG.pdf`, `RAGANYTHING.pdf` (arquitectura RAG de G2, no instrumentos de medición)