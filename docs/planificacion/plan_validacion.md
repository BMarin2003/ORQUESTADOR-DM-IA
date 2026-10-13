# Plan de validación de los instrumentos (paso a paso)

> **Encuadre (2026-09-20, tras revisar la Rúbrica v2).** La rúbrica v2 (7 niveles, panel de 5 DMs, campaña completa) se sustituyó por
> medición 100 % determinista a petición del asesor. Este plan respeta ese giro: **la ruta principal no usa evaluadores humanos**. La rúbrica
> queda como definición de los constructos; su cruce con los instrumentos está en `docs/matriz_cobertura_rubrica_instrumentos.md`.
> Una comprobación humana pequeña (Ruta B) queda **opcional y sujeta al visto bueno del asesor**.

## Ruta A · sin evaluadores humanos (compatible con el giro determinista)

| # | Paso | Entregable | Estado |
|---|---|---|---|
| A1 | Matriz de cobertura rúbrica ↔ instrumentos (validez de contenido) | `docs/matriz_cobertura_rubrica_instrumentos.md` | **hecho** |
| A2 | Pruebas de sensibilidad por perturbación: inyectar defectos controlados en ventanas reales (PNJ muerto que actúa, «tú decides…», HP contradicho, párrafos duplicados, nombres inventados, turnos barajados) y comprobar que cada instrumento reacciona en la dirección esperada. Habría detectado el fallo de los detectores en 3.ª persona | script + tabla de sensibilidad | siguiente |
| A3 | Auditoría de precisión y recall de los detectores (Pista B): el investigador etiqueta sí/no una muestra de marcas y de no-marcas; el segundo autor re-etiqueta el 20 % | precisión/recall con IC | |
| A4 | Corregir o complementar los instrumentos con lagunas (2.ª persona, respuesta a la acción, consecuencias) y recalcular en las 54 campañas (determinista, barato) | reportes v2 | |
| A5 | Declarar como límite lo no medible (interés/creatividad, voz de personaje) | sección de limitaciones | |

## Ruta B · comprobación humana pequeña (opcional; requiere OK del asesor)

Reusa el material ya generado (`datos/validacion/`). Si se hace, se **alinea con la rúbrica v2**: escala de 7 niveles con sus descriptores y su
protocolo de calibración (ICC ≥ 0.75; segunda sesión si es menor; indicador con ICC < 0.65 se reporta con la limitación declarada), en lugar
de la escala 1-5 y el alfa de Krippendorff que usa el formulario actual. Evaluadores propuestos: los dos autores. Es una versión a escala de la
v2 (ventanas de 8 turnos, no campañas completas de 1 400 turnos, imposibles de leer para 54 campañas), presentada como validación
convergente de los instrumentos, no como retorno al panel.

---

**Pregunta que responde:** ¿los instrumentos deterministas miden lo que dicen medir (coherencia reactiva, longitudinal y calidad
narrativa emergente)? Sin esto, sus resultados tienen solo validez aparente (varios están en efecto techo o tienen artefactos).
Respaldo bibliográfico: `docs/papers_revistas_q1-q3.md` (Reiter 2018; van der Lee et al. 2021; Artstein & Poesio 2008).

## Alcance: qué se puede validar con humanos y qué no

| Pista | Qué se valida | Cómo | Instrumentos |
|---|---|---|---|
| **A · Dimensional** (ventanas de 8 turnos) | Que el instrumento sube y baja con el juicio humano | 2 evaluadores ciegos califican pares de textos (G1 vs G2, mismo par y mismo tramo) en 6 subdimensiones; se correlaciona la diferencia humana con la diferencia del instrumento | CR-1 gramaticalidad, CR-2 grafo por lema, CL-1 ECR, QN-1 (TTR, n-gramas, legibilidad), QN-2; CL-1/CL-2 solo dentro de la ventana |
| **B · Precisión de detectores** | Que lo que el detector marca es un problema real (y qué se le escapa) | Un evaluador etiqueta sí/no una muestra de marcas y de no-marcas; otro re-etiqueta el 20 % | `cl2_pnj_inactivo_actua`, `cr1_veredicto_contradice`, relojes «reconocidos», Jericho recall, `cl1_campo_inmutable` |
| **No validable con humanos** | Papalampidi C/V, detector de bucles (requieren la campaña completa) | Se declaran como limitación, o se validan por inspección de casos | — |

Los pares de la muestra son Par07-27 (21 pares): Par01-06 corrieron con un motor anterior y no están en `ids_*.json`.

## Pasos de la Ruta B

| # | Paso | Entregable | Quién | Tiempo |
|---|---|---|---|---|
| **1.0** | Aprobar alcance y rúbrica (6 ítems, escala 1-5 con anclas) | Rúbrica cerrada | Bryan (+ asesor) | 30 min |
| **1.1** | Muestreo y material ciego — **HECHO** | `datos/validacion/` (ver abajo) | Claude | — |
| **1.2** | **Piloto**: 4 unidades, 2 evaluadores | CSV de cada uno; α de Krippendorff por ítem | Evaluadores | ~1 h c/u |
| **1.3** | Ajustar anclas de la rúbrica según el piloto (los ítems con α bajo se aclaran) | Rúbrica v2 | Bryan + Claude | 30 min |
| **1.4** | Calcular los instrumentos **por ventana** (hoy salen por campaña) | `datos/validacion/instrumentos_por_ventana.csv` | Claude | 1 sesión |
| **1.5** | Evaluación principal: 24 unidades | CSV de cada evaluador | Evaluadores | ~5-6 h c/u |
| **1.6** | Análisis pre-especificado: α, correlaciones instrumento-humano, preferencia G1 vs G2, comprobación del ciego | `docs/reportes/validacion_humana.md` | Claude | 1 sesión |
| **1.7** | Pista B: etiquetar marcas y no-marcas de los detectores | Precisión y recall con IC | 1-2 evaluadores | ~2 h |

Después (fuera de esta fase): análisis estadístico pre-especificado (Wilcoxon por par + modelos mixtos con lote), instrumento de
deriva/homogeneidad, comprobaciones de robustez, redacción.

## Diseño de la Pista A (ya implementado en `experimento/scripts/validacion_generar.py`)

- **Unidad:** (par, ventana de 8 turnos). Texto A y B: uno de G1 y otro de G2, mismo par y mismos turnos, orden al azar (mitad y
  mitad). El evaluador ve el lore, 1 turno previo (no se califica) y los 8 turnos con la acción del jugador.
- **Muestra:** 24 unidades (8 por posición: turnos 20-180, 600-780, 1200-1380; 2 por tono en cada posición: grimdark, heroic, light,
  mixed) + 4 de piloto. 16 pares distintos, mezcla de lote v1 y v2. Semilla 20260920 (reproducible).
- **Ciego:** G1 escribe con etiquetas `narrativa/mecanica/presion` y una línea de tirada (99-100 % y 95 % de sus turnos; G2 nunca).
  Se quitan las etiquetas y el bloque `mecanica`. Se excluyen ventanas con JSON crudo, `[meta-comentario]` o alfabetos no latinos.
  **Fuga residual que no se puede quitar:** G1 escribe ~34 % más por turno (946 vs 705 caracteres). Por eso cada evaluador responde
  «¿cuál es el multiagente?» y se reporta el acierto.
- **Calificación:** 1-5 por texto en CR1 (fluidez y sentido lógico), CR2 (arraigo contextual), CL1 (consistencia de personajes),
  CL2 (consistencia de eventos y estado del mundo), QN1 (interés y creatividad), QN2 (reactividad a la agencia del jugador); más
  marcas de problemas graves y comentario.
- **Límite de la Pista A:** una ventana de 8 turnos no permite juzgar la consistencia a largo plazo; CL-1/CL-2 se validan solo dentro
  de la ventana, y el largo plazo se cubre con la Pista B.

## Hipótesis y criterios (propuestos, a aprobar en 1.0)

1. **Fiabilidad de los humanos:** α de Krippendorff (ordinal) ≥ 0.667 por ítem para usar el ítem (0.8 = fiable). Umbrales
   convencionales, discutidos en Artstein & Poesio (2008): confirmar en el texto.
2. **Validez convergente, por instrumento y dimensión:** correlación de Spearman entre (instrumento G1 − G2) y (humano G1 − G2)
   sobre las unidades, con IC bootstrap al 95 %. El instrumento se considera respaldado si ρ ≥ 0.4 y el IC no incluye 0. Si no,
   se reporta como no validado (sin ajustar el umbral después de ver los datos).
3. **Potencia:** con 24 unidades, ρ = 0.5 se detecta con potencia ≈ 0.7 (aprox. de Fisher); para 0.9 harían falta ≈ 38. Las unidades
   no son totalmente independientes (un mismo par aparece hasta 2 veces), así que es una cifra optimista.
4. **Preferencia humana G1 vs G2** por dimensión, como resultado propio (no solo como criterio de validez).

## Material generado (Paso 1.1)

`datos/validacion/`: `evaluador_E1_piloto.html`, `evaluador_E2_piloto.html`, `evaluador_E?_principal.html` (autónomos: se abren con el
navegador, guardan solos y exportan CSV), `unidades.json` (ciego), **`clave_secreta.json` (los evaluadores no deben abrirlo)**.
Regenerar: `python experimento/scripts/validacion_generar.py [--k 8] [--n-por-posicion 8] [--piloto 4] [--seed N] [--evaluadores E1,E2]`.
Probado en Chromium sin interfaz: renderiza, guarda al recargar, cuenta el avance y exporta el CSV, sin errores de JavaScript.
