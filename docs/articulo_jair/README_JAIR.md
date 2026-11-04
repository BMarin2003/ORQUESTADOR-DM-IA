# Artículo JAIR: borrador

Archivos:
- `main.tex`: manuscrito en inglés, en formato IMRAD, con resumen estructurado (Background / Objectives / Methods / Results / Conclusions).
- `refs.bib`: 41 referencias tomadas de la tesis.
- `main.pdf`: compilación de verificación, 8 páginas.

## 1. Pasarlo a la plantilla oficial de JAIR (obligatoria desde el vol. 83)

1. Abrir la plantilla en Overleaf: https://www.overleaf.com/read/hycbzkdksrzz#8106d4. Usar *Copy project*.
2. Copiar cada sección de `main.tex` (de Introduction a Reproducibility Statement) en el cuerpo de la plantilla.
3. Subir `refs.bib` y cambiar `\bibliography{...}` por `refs`. Usar el estilo bibliográfico que trae la plantilla, no `plainnat`.
4. Completar los datos que pide la plantilla: autores, afiliación (UPAO), correos y ORCID. El Author Kit está en https://www.jair.org/index.php/jair/libraryFiles/downloadPublic/6.
5. Quitar `\provisional{}` y el color naranja una vez actualizadas las cifras de persona2 (ver la sección 4).

## 2. Respuesta para el formulario: «¿Por qué es importante su trabajo?» (≤150 palabras)

> Multi-agent LLM architectures are increasingly adopted for interactive storytelling on the assumption that agent specialization improves narrative coherence. We provide, to our knowledge, the first controlled test of that assumption in long role-playing campaigns: 27 matched pairs of 1,400-turn Dungeons & Dragons campaigns in which both architectures share the same open-weights model, the same structured world-state memory and the same scenarios. Using deterministic instruments validated by perturbation tests and a blind human study, we find that specialization brings no gain in reactive or longitudinal coherence once memory is shared, but robustly reduces how often the system decides on behalf of the player—a failure that grows with campaign length in single-call game masters. The result reframes the design question from "multi-agent or not" to which decision boundaries are worth specializing, and offers a reusable protocol for evaluating narrative AI architectures.

(≈145 palabras)

## 3. Lista de reproducibilidad (obligatoria): qué responder

- **Código y datos:** repositorio público en GitHub. Antes del envío conviene crear un release con DOI en Zenodo.
- **Modelo:** `google/gemma-4-31B-it`, versión fijada, un solo proveedor de inferencia, sin ajuste fino. Indicar la temperatura y los parámetros que usa el orquestador.
- **Semillas:** tiradas deterministas con semilla (campaña, turno, habilidad), más la semilla de la partición dev/test (20261105).
- **Estadística:** pruebas exactas, intervalos de confianza, tamaño del efecto y corrección de Holm. Se reportan todos los instrumentos, no solo los significativos.
- **Sujetos humanos:** 5 directores de juego con consentimiento firmado. **Los consentimientos y la relación persona↔código no se publican.**
- **Cómputo:** número de llamadas, tokens, costo y horas por arquitectura (dato disponible en `costo-por-arquitectura`).

## 4. Pendiente antes de enviar

- [ ] **Cifras de persona2 (provisionales):** se actualizan tras el rehecho del martes, con contexto en dev y medición en test. Afecta al resumen, a H1c, a la Tabla 2, a la robustez, a la precisión (1/1 y 5/11) y a Limitations.
- [ ] Llenar el valor de *r* de la fila *emotion* de la Tabla 2, o quitar la fila.
- [ ] Agregar las referencias de la tesis que no se pasaron al .bib (Ma et al. 2026, NCP-Bench), sobre todo si se cita como trabajo relacionado directo.
- [ ] Revisar con el asesor si figura como coautor (en el borrador aparece como tercer autor).
- [ ] **Política de IA de JAIR:** las contribuciones centrales deben ser de los autores. Declarar en los agradecimientos o en la carta el uso de asistentes de IA en la redacción y el análisis.
- [ ] **Riesgo de desk reject por «aplicar técnicas conocidas»:** la carta de presentación debe subrayar el aislamiento del factor memoria y el protocolo de validación de instrumentos como aportes metodológicos.
- [ ] Opcional: una figura con las curvas de usurpación por bloque (G1 frente a G2).
