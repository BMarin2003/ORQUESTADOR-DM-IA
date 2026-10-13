# Matriz de cobertura: Rúbrica D&D-IA v2 ↔ instrumentos deterministas

**Encuadre.** La rúbrica v2 (7 niveles, panel de 5 DMs, campaña completa) se sustituyó por medición 100 % determinista a petición del
asesor. La rúbrica pasa a ser la **definición de los constructos**; los instrumentos son su operacionalización. Esta matriz responde,
para cada indicador, qué componente de la definición mide cada instrumento y cuál queda sin medir (validez de contenido). Los datos
salen de las 42 campañas de Par07-27 (58 800 turnos en total (29 400 por brazo)) y las definiciones, del código (`orquestador/vertical_slice.py`,
`reporte_validacion.py`), no de descripciones previas.

## 1. Cobertura por indicador

| Indicador (rúbrica v2) | Componente de la definición | Instrumento(s) actual(es) | ¿Lo mide realmente? | Laguna |
|---|---|---|---|---|
| **CR-1** Fluidez y sensatez | (a) cohesivo y comprensible | Gramaticalidad (LanguageTool, sin ortografía) | Solo corrección gramatical; el techo (0.999 / 0.988) no discrimina | — |
| | (b) consistente con las reglas del juego | `cr1_veredicto_contradice_narracion` | Muy estrecho: solo pifia (1 natural) narrada como éxito, por regex de verbos | Plausibilidad lógica: **sin instrumento** |
| **CR-2** Arraigo contextual | (a) anclada en la acción específica del jugador | — | — | **Sin instrumento** |
| | (b) anclada en el estado del mundo, sin entidades inventadas | `cr2_nombres_no_reconocidos`; `cr2_entidad_grafo_densidad`; grafo por lema; ECR | Nombres desconocidos: **inflado en G1** (cuenta «Éxito/Fallo/Percepción» de su línea mecánica); ECR sube casi a 1 en todo | — |
| **CL-1** Consistencia de personajes | rasgos, historia, capacidades | Papalampidi C/V; ECR; `cl1_campo_inmutable_alterado` | **`cl1_campo_inmutable` no mide esto**: detecta que el *extractor* propuso un campo fuera de `mutable_fields` (deriva contrato↔base) | Voz, personalidad y motivaciones: **sin instrumento** |
| **CL-2** Consistencia de eventos y mundo | consecuencias duraderas, sin contradicción | Jericho recall; relojes «reconocidos»; `cl2_pnj_inactivo_actua`; `cl2_pc_hp_contradice_narracion` | Jericho y relojes sí (heurísticas léxicas); `pnj_inactivo` = «nombre de PNJ no vivo aparece», con falsos positivos (capturados, menciones); **`pc_hp` nunca se dispara (ver 2)** | — |
| **QN-1** Interés y creatividad | evocador, creativo, sin repetición | TTR; repetición de n-gramas; legibilidad Fernández-Huerta; detector de bucles | Miden **diversidad léxica y complejidad**, no interés ni creatividad | Interés, giros, «hooks»: **sin instrumento** |
| **QN-2** Reactividad a la agencia | (a) consecuencias visibles de la decisión | — (Jericho recall solo cuenta cambios de estado narrados) | — | **Sin instrumento** de consecuencias |
| | (b) no usurpa la agencia del jugador | `qn2_pj_piensa_narrado`; `qn2_pj_accion_revisar` | **Ciegos en G2 (ver 2)** | — |

Resultado: la rúbrica se descompone en 12 componentes (CR-1: cohesión, reglas, plausibilidad · CR-2: acción específica, estado del mundo ·
CL-1: rasgos/historia, voz/motivación · CL-2: consecuencias duraderas · QN-1: lenguaje/repetición, interés/creatividad · QN-2: consecuencias
visibles, no usurpar la agencia). **5 no tienen ningún instrumento** (plausibilidad lógica, acción específica, voz y motivación,
interés y creatividad, consecuencias visibles). **3 están medidos con instrumentos sesgados o de validez no comprobada**: reglas (CR-1,
detector muy estrecho), estado del mundo (CR-2, inflado en G1) y no usurpar la agencia (QN-2, ciego en G2). Los otros 4 tienen
cobertura parcial con proxies (cohesión, rasgos/historia, consecuencias duraderas, lenguaje/repetición).

## 2. Amenazas a la validez detectadas con datos

| Instrumento | Hallazgo | Evidencia |
|---|---|---|
| `cl2_pc_hp_contradice_narracion`, `qn2_pj_accion_revisar` | **0 marcas en 58 800 turnos en total (29 400 por brazo).** Buscan «<nombre del PJ> muere/ataca/decide…» en tercera persona | G2 nombra al PJ en el **0.1 %** de los turnos y narra en 2.ª persona en el 84.5 %; G1 nombra al PJ en el 4.9 % y usa 2.ª persona en el 36.9 % |
| `qn2_pj_piensa_narrado` | 0 marcas en G2, 4 en G1: el sesgo favorece a G2 por construcción (no puede verlo) | ídem; el equivalente en 2.ª persona («decides/piensas/comprendes/te das cuenta/te sientes») aparece en **293 turnos de G2 (1.00 %) y 133 de G1 (0.45 %)**: el signo se invierte |
| `cr1_veredicto_contradice_narracion` | 21 marcas en G2 y 139 en G1 | Sin verificar si las de G1 son reales o vienen de su línea mecánica |
| `cl1_campo_inmutable_alterado` | Se dispara en 21/21 campañas de ambos brazos | Mide el extractor, no al personaje; no debe presentarse como consistencia de personajes |
| `cl2_pnj_inactivo_actua` | 816 marcas (G2) y 2 564 (G1) | Sección 9 del reporte: la mayoría son menciones, no acciones; «capturado» cuenta como inactivo |
| `cr2_nombres_no_reconocidos` | ≈ 100 % de los turnos de G1 | Artefacto de formato (ya documentado) |
| Estilo por brazo | G2 narra en 2.ª persona, G1 mezcla 2.ª y 3.ª | Cualquier regex por persona gramatical sesga entre brazos |

Los patrones en 2.ª persona de la fila de `qn2_pj_piensa_narrado` son **exploratorios y sin validar** («te das cuenta» puede ser una percepción
legítima). Su precisión hay que medirla antes de usarlos (Pista B del plan).

**Consecuencia para lo ya reportado:** los ceros de estos detectores en Par07-27 no son evidencia de ausencia del defecto. No deben citarse
como «G2 nunca usurpa la agencia» ni «el HP del PJ es siempre coherente».

## 3. Lagunas cubribles con instrumentos deterministas baratos (propuestas, sin implementar)

1. **Usurpación de agencia en 2.ª persona:** patrones de acción, decisión o pensamiento atribuidos al «tú» (base: los de arriba, afinados con la Pista B).
2. **Respuesta a la acción específica (CR-2a):** solapamiento léxico (lemas) entre la acción del jugador y la respuesta del DM.
3. **Consecuencias (QN-2a):** deltas de estado por turno tras acciones con tirada (`state_deltas`), como tasa de cambio del mundo.
4. **Muerte/HP del PJ en 2.ª persona:** «mueres/caes muerto/pierdes la vida» contra `hp_current`.

Interés y creatividad (QN-1) y voz de personaje (CL-1) no tienen sustituto determinista razonable: declararlos como **límite del
enfoque** (los instrumentos miden diversidad y coherencia de entidades, no interés ni voz).
