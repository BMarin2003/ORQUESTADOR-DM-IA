# Validación persona2 (A3 / H1f) — resultado

Evaluador principal: **E1_IA_asistido** (515/515 ítems de la clave, oculta durante el etiquetado).

Evaluadores del subconjunto del 20 %: **E2, E3, E4** (102 ítems — ⚠ los conjuntos NO coinciden exactamente entre evaluadores, revisar exports).

## 1. Detector vs. evaluador principal (515 ítems)

| Modo | N | TP | FP | TN | FN | Precisión | IC95% | Recall | IC95% | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Estricto (solo `si`) | 515 | 55 | 160 | 274 | 26 | 25.6% | 20.2%–31.8% | 67.9% | 57.1%–77.1% | 0.372 |
| Amplio (`si`+`dudoso`) | 515 | 56 | 159 | 272 | 28 | 26.0% | 20.6%–32.3% | 66.7% | 56.1%–75.8% | 0.375 |

## 2. Acuerdo: evaluador principal vs. cada evaluador del 20 % (ítems compartidos)

Sirve para validar si el evaluador principal (IA-asistido mientras no haya un E1 humano) es un proxy razonable de juicio humano — ver docs claude/persona2-auditoria-IA-analisis.md.

| Evaluador | n común | % acuerdo | kappa Cohen | PABAK | AC1 de Gwet |
|---|---|---|---|---|---|
| E2 | 102 | 86.3% | 0.000 | 0.725 | 0.843 |
| E3 | 102 | 70.6% | 0.045 | 0.412 | 0.578 |
| E4 | 101 | 70.3% | 0.043 | 0.406 | 0.572 |

## 3. Acuerdo entre evaluadores del 20 % (mide si el criterio humano es fiable)

- Kappa de Fleiss (3 evaluadores, 3 categorías no/si/dudoso): **-0.093**

| Par | n común | % acuerdo | kappa Cohen | PABAK | AC1 de Gwet |
|---|---|---|---|---|---|
| E2–E3 | 102 | 76.5% | 0.000 | 0.529 | 0.703 |
| E2–E4 | 101 | 76.2% | 0.000 | 0.525 | 0.699 |
| E3–E4 | 101 | 59.4% | -0.137 | 0.188 | 0.369 |

## 4. Consenso mayoritario del 20 % (mayoría entre evaluadores del subconjunto)

Empates (sin mayoría, excluidos de precisión/recall): 1 de 102.

**Detector vs. consenso mayoritario humano** (n=101, solo humano real, sin IA): TP=2 FP=40 TN=58 FN=1.
- Precisión: 4.8% (IC95% Wilson 1.3%–15.8%)
- Recall: 66.7% (IC95% Wilson 20.8%–93.9%)

**E1_IA_asistido vs. consenso mayoritario humano**: n=101, acuerdo=85.1%, kappa=0.072. Si el acuerdo es alto, el proxy queda razonablemente validado para los 413 ítems restantes que ningún humano etiquetó; si es bajo, revisar los criterios antes de citar la sección 1 en la tesis.

## Nota metodológica
«Violación» para precisión/recall = veredicto humano 'si' (modo estricto) o 'si'/'dudoso' (modo amplio). El detector se considera positivo cuando `categoria_asignada` no está vacío en la clave. La clave nunca se muestra a los evaluadores durante el etiquetado (diseño ciego). Ningún evaluador (principal ni del 20 %) puede pertenecer al equipo investigador (mismo principio de juez-y-parte que en brecha 4) — no hay límite de cuántos evaluadores externos se usen, solo de quién puede serlo.