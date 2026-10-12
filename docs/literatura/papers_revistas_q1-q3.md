# Referencias de revista (SJR Q1-Q3) para dar validez a la investigación

Búsqueda hecha el 2026-09-20. Complementa `docs/papers.md` (que es casi todo de conferencia).

**Cómo se verificó.** Cada artículo se confirmó por búsqueda web (título, autores, revista, año, y DOI o URL). Los cuartiles son el
"mejor cuartil" SJR (SCImago, dato más reciente) leído de los resúmenes de la búsqueda, porque SCImago devuelve 403 a la lectura
directa. El cuartil cambia por año y por categoría: **confirmarlo en scimagojr.com antes de citarlo en la tesis.** Lo que no pude
confirmar está marcado «no verificado».

## A. Validez de las métricas y de la evaluación (lo más importante para la tesis)

| Referencia | Revista (SJR) | Para qué sirve aquí |
|---|---|---|
| Reiter, E. (2018). A Structured Review of the Validity of BLEU. *Computational Linguistics* 44(3), 393-401. https://doi.org/10.1162/COLI_a_00322 | Computational Linguistics (Q1) | Una métrica automática solo vale si se valida contra juicio humano; revisó 284 correlaciones y no respalda usar BLEU fuera de su uso original ni para contrastar hipótesis. Es el argumento para exigir validación humana a los instrumentos deterministas. |
| Sai, A. B., Mohankumar, A. K., Khapra, M. M. (2022). A Survey of Evaluation Metrics Used for NLG Systems. *ACM Computing Surveys* 55(2), art. 26. https://doi.org/10.1145/3485766 | ACM Computing Surveys (Q1) | Taxonomía de métricas y críticas a su uso; encuadra los instrumentos del proyecto. |
| van der Lee, C., Gatt, A., van Miltenburg, E., Krahmer, E. (2021). Human evaluation of automatically generated text: current trends and best practice guidelines. *Computer Speech & Language* 67, 101151. https://www.sciencedirect.com/science/article/pii/S088523082030084X | Computer Speech & Language (Q2) | Guía de cómo diseñar y reportar la evaluación humana (tamaño de muestra, evaluadores, instrucciones, acuerdo, pruebas). |
| Artstein, R., Poesio, M. (2008). Inter-Coder Agreement for Computational Linguistics. *Computational Linguistics* 34(4), 555-596. https://aclanthology.org/J08-4004/ | Computational Linguistics (Q1) | Cómo medir y reportar el acuerdo entre anotadores (alfa de Krippendorff, kappa). |

## B. Tratamiento estadístico (diseño pareado, medidas repetidas, efecto de lote)

| Referencia | Revista (SJR) | Para qué sirve aquí |
|---|---|---|
| Demšar, J. (2006). Statistical Comparisons of Classifiers over Multiple Data Sets. *JMLR* 7, 1-30. https://jmlr.org/papers/v7/demsar06a.html | Journal of Machine Learning Research (Q1) | Respalda la prueba de Wilcoxon de rangos con signo para comparar dos sistemas sobre varios conjuntos (aquí, 27 pares). |
| Barr, D. J., Levy, R., Scheepers, C., Tily, H. J. (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. *Journal of Memory and Language* 68(3), 255-278. https://www.sciencedirect.com/science/article/abs/pii/S0749596X12001180 | Journal of Memory and Language (Q1) | Modelos mixtos con el par como efecto aleatorio y el lote como efecto fijo. |
| Bates, D., Mächler, M., Bolker, B., Walker, S. (2015). Fitting Linear Mixed-Effects Models Using lme4. *Journal of Statistical Software* 67(1), 1-48. https://doi.org/10.18637/jss.v067.i01 | J. Statistical Software (cuartil **no verificado**) | Implementación de esos modelos. |

## C. Narrativa, creatividad y homogeneidad

| Referencia | Revista (SJR) | Para qué sirve aquí |
|---|---|---|
| Jordanous, A. (2012). A Standardised Procedure for Evaluating Creative Systems (SPECS). *Cognitive Computation* 4(3), 246-279. https://doi.org/10.1007/s12559-012-9156-1 | Cognitive Computation (Q1) | Método para definir qué significa «creativo» en el dominio y derivar pruebas; sirve para operacionalizar la dimensión «calidad narrativa emergente». |
| Ritchie, G. (2007). Some Empirical Criteria for Attributing Creativity to a Computer Program. *Minds and Machines* 17, 67-99. https://doi.org/10.1007/s11023-007-9066-2 | Minds and Machines (Q1) | Criterios empíricos (tipicidad, calidad, novedad); ancla el QN-1 diferido. |
| Doshi, A. R., Hauser, O. P. (2024). Generative AI enhances individual creativity but reduces the collective diversity of novel content. *Science Advances* 10(28), eadn5290. https://doi.org/10.1126/sciadv.adn5290 | Science Advances (Q1) | Evidencia de homogeneización del contenido generado: las historias con IA se parecen más entre sí. Respalda medir la diversidad entre campañas (ver deriva del escenario). |
| Alhussain, A. I., Azmi, A. M. (2021). Automatic Story Generation: A Survey of Approaches. *ACM Computing Surveys* 54(5), art. 103. https://doi.org/10.1145/3453156 | ACM Computing Surveys (Q1) | Panorama de la generación de historias y de cómo se evalúa. |
| Wang, Y., Lin, J., Yu, Z., Hu, W., Karlsson, B. F. (2023). Open-world story generation with structured knowledge enhancement: A comprehensive survey. *Neurocomputing* 559, 126792. https://doi.org/10.1016/j.neucom.2023.126792 | Neurocomputing (Q1) | Generación con conocimiento estructurado: el respaldo de tener un estado de mundo en base de datos. |

## D. Contexto largo y deriva

| Referencia | Revista (SJR) | Para qué sirve aquí |
|---|---|---|
| Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., Liang, P. (2024). Lost in the Middle: How Language Models Use Long Contexts. *TACL* 12, 157-173. https://aclanthology.org/2024.tacl-1.9/ | Transactions of the ACL (Q1) | El rendimiento cae al crecer el contexto y cuando la información queda en medio; justifica analizar por ventanas de tiempo y no solo el agregado. |

## E. Agentes, juegos y consistencia de personaje

| Referencia | Revista (SJR) | Para qué sirve aquí |
|---|---|---|
| Wang, L., Ma, C., Feng, X., et al. (2024). A survey on large language model based autonomous agents. *Frontiers of Computer Science* 18, 186345. https://doi.org/10.1007/s11704-024-40231-1 | Frontiers of Computer Science (Q1) | Marco de agentes (perfil, memoria, planificación, acción) para describir G1. |
| Gallotta, R., Todd, G., Zammit, M., Earle, S., Liapis, A., Togelius, J., Yannakakis, G. N. (2024). Large Language Models and Games: A Survey and Roadmap. *IEEE Transactions on Games*. https://arxiv.org/abs/2402.18659 (volumen/DOI de la versión de revista: **no verificado**) | IEEE Transactions on Games (Q2) | Sitúa el LLM como director de juego y lista los límites (consistencia, memoria). |
| Riedl, M. O., Bulitko, V. (2013). Interactive Narrative: An Intelligent Systems Approach. *AI Magazine* 34(1), 67-77. https://doi.org/10.1609/aimag.v34i1.2449 | AI Magazine (Q2) | Tradición de gestión de drama/experiencia; el agente Mundo de G1 pertenece a esa línea. |
| Han, X., Zhao, W., Guan, Z., Peng, J. (2025). Act-LLM: A whole-process chain for character-centric role-playing with large language models. *Expert Systems with Applications*. https://www.sciencedirect.com/science/article/abs/pii/S0957417425026417 (volumen/artículo: **no verificado**) | Expert Systems with Applications (Q1) | Memoria de largo y corto plazo y límites de conocimiento del personaje. |
| Wang, J., Wu, K., Ouyang, Y. (2025). Enhancing Character-Coherent Role-Playing Dialogue with a Verifiable Emotion Reward. *Information* 16(9), 738. https://doi.org/10.3390/info16090738 | Information (Q2) | Coherencia de personaje a nivel de turno y de diálogo; menciona la deriva de la personalidad en conversaciones largas. |
| «Game Knowledge Management System: Schema-Governed LLM Pipeline for Executable Narrative Generation in RPGs». *Systems* 14(2), 175 (feb. 2026). https://www.mdpi.com/2079-8954/14/2/175 (autores: **no verificados**) | Systems (Q2) | El más cercano a la arquitectura del proyecto: generación gobernada por esquema, validación y admisión al motor, con estudio humano. |

## F. Precedentes directos que NO son de revista (sin cuartil; conferencias)

- Huot, F., Amplayo, R. K., Palomaki, J., Jakobovits, A. S., Clark, E., Lapata, M. (2025). *Agents' Room: Narrative Generation through Multi-step Collaboration*. ICLR 2025. Descompone la escritura en agentes especializados; evaluación humana de expertos y automática; los agentes ganan a las líneas base sin colaboración.
- *StoryWriter: A Multi-Agent Framework for Long Story Generation*. CIKM 2025 (https://dl.acm.org/doi/10.1145/3746252.3761616).
- *Lost in Stories: Consistency Bugs in Long Story Generation by LLMs*. Findings of ACL 2026 (https://aclanthology.org/2026.findings-acl.410/). Errores de consistencia, sobre todo factuales y temporales, y hacia la mitad de la narración.

## Hueco encontrado (importante)

**No encontré, verificado en revista Q1-Q3, un estudio que compare directamente un sistema multiagente contra uno monolítico en
coherencia de narrativa larga o de partida rolera.** Lo más cercano es de conferencia (sección F). Es una oportunidad de
contribución, pero obliga a sostener las afirmaciones con evidencia análoga y a declararlo.

## Referencias ya en `docs/papers.md` con problemas de verificación (resolver o retirar antes de citar)

Roemmele & Gordon (venue sin confirmar), «CHADPOD/GAMES 2024» (no localizado), De Lima et al. 2023 (no localizado), Hausknecht/Ammanabrolu 2020
(autoría anotada distinta), Zhou et al. (año 2022 vs. ACL 2023).
