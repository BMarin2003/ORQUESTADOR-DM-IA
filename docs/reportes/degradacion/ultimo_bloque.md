# Último bloque (1301-1400): análisis exploratorio

Bloques de 100 turnos; una campaña por par (n = 27 por brazo). Wilcoxon bilateral; Holm dentro de cada lectura.
A = b14 − media(b12, b13); B = b14 − predicción OLS de b1..b13; C = salto G1 − salto G2 por par.

| indicador | peor si | lectura | brazo | n | mediana | + | p | p Holm |
|---|---|---|---|---|---|---|---|---|
| qn1_ttr | baja | A_salto | G1 | 26 | 0.0003 | 14 | 0.745 | 1.000 |
| qn1_ttr | baja | A_salto | G2 | 27 | -0.0033 | 11 | 0.170 | 1.000 |
| qn1_ttr | baja | B_tendencia | G1 | 27 | -0.0008 | 12 | 0.662 | 1.000 |
| qn1_ttr | baja | B_tendencia | G2 | 27 | -0.0021 | 10 | 0.386 | 1.000 |
| qn1_ttr | baja | C_difendif | G1-G2 | 27 | 0.0002 | 15 | 0.348 | 1.000 |
| qn1_ngram_repeticion | sube | A_salto | G1 | 27 | 0.0000 | 14 | 0.611 | 1.000 |
| qn1_ngram_repeticion | sube | A_salto | G2 | 27 | 0.0003 | 15 | 0.822 | 1.000 |
| qn1_ngram_repeticion | sube | B_tendencia | G1 | 27 | -0.0007 | 9 | 0.211 | 1.000 |
| qn1_ngram_repeticion | sube | B_tendencia | G2 | 27 | 0.0003 | 14 | 0.878 | 1.000 |
| qn1_ngram_repeticion | sube | C_difendif | G1-G2 | 27 | -0.0003 | 12 | 0.470 | 1.000 |
| qn1_legibilidad_fh | ? | A_salto | G1 | 27 | 0.5444 | 20 | 0.009 | 0.169 |
| qn1_legibilidad_fh | ? | A_salto | G2 | 27 | 0.7111 | 15 | 0.500 | 1.000 |
| qn1_legibilidad_fh | ? | B_tendencia | G1 | 27 | 0.5995 | 18 | 0.065 | 1.000 |
| qn1_legibilidad_fh | ? | B_tendencia | G2 | 27 | 0.6474 | 14 | 0.361 | 1.000 |
| qn1_legibilidad_fh | ? | C_difendif | G1-G2 | 27 | -0.2697 | 12 | 0.953 | 1.000 |
| cl2_lugar_jaccard | ? | A_salto | G1 | 27 | -0.0017 | 11 | 0.163 | 1.000 |
| cl2_lugar_jaccard | ? | A_salto | G2 | 27 | -0.0028 | 9 | 0.155 | 1.000 |
| cl2_lugar_jaccard | ? | B_tendencia | G1 | 27 | -0.0035 | 9 | 0.026 | 0.472 |
| cl2_lugar_jaccard | ? | B_tendencia | G2 | 27 | -0.0038 | 10 | 0.025 | 0.466 |
| cl2_lugar_jaccard | ? | C_difendif | G1-G2 | 27 | -0.0003 | 12 | 0.897 | 1.000 |
| cr2_nombres_no_reconocidos | sube | A_salto | G1 | 24 | -0.0175 | 9 | 0.170 | 1.000 |
| cr2_nombres_no_reconocidos | sube | A_salto | G2 | 25 | 0.0050 | 14 | 0.957 | 1.000 |
| cr2_nombres_no_reconocidos | sube | B_tendencia | G1 | 27 | 0.0031 | 14 | 0.494 | 1.000 |
| cr2_nombres_no_reconocidos | sube | B_tendencia | G2 | 27 | -0.0177 | 8 | 0.155 | 1.000 |
| cr2_nombres_no_reconocidos | sube | C_difendif | G1-G2 | 23 | -0.0300 | 9 | 0.687 | 1.000 |
| cr1_contradice_narracion | sube | A_salto | G1 | 7 | -0.0050 | 2 | 1.000 | 1.000 |
| cr1_contradice_narracion | sube | A_salto | G2 | 4 | — | — | — | — |
| cr1_contradice_narracion | sube | B_tendencia | G1 | 21 | -0.0015 | 9 | 0.192 | 1.000 |
| cr1_contradice_narracion | sube | B_tendencia | G2 | 17 | -0.0012 | 5 | 0.061 | 1.000 |
| cr1_contradice_narracion | sube | C_difendif | G1-G2 | 9 | -0.0050 | 4 | 0.516 | 1.000 |
| cl2_pnj_inactivo_actua | sube | A_salto | G1 | 8 | -0.0125 | 4 | 0.844 | 1.000 |
| cl2_pnj_inactivo_actua | sube | A_salto | G2 | 10 | 0.0100 | 6 | 0.826 | 1.000 |
| cl2_pnj_inactivo_actua | sube | B_tendencia | G1 | 16 | 0.0171 | 8 | 0.632 | 1.000 |
| cl2_pnj_inactivo_actua | sube | B_tendencia | G2 | 16 | -0.0067 | 6 | 0.193 | 1.000 |
| cl2_pnj_inactivo_actua | sube | C_difendif | G1-G2 | 16 | -0.0025 | 8 | 0.744 | 1.000 |
| qn2_persona2_primaria | sube | A_salto | G1 | 8 | 0.0050 | 5 | 0.492 | 1.000 |
| qn2_persona2_primaria | sube | A_salto | G2 | 26 | -0.0000 | 13 | 0.760 | 1.000 |
| qn2_persona2_primaria | sube | B_tendencia | G1 | 23 | 0.0004 | 12 | 0.574 | 1.000 |
| qn2_persona2_primaria | sube | B_tendencia | G2 | 27 | -0.0035 | 10 | 0.614 | 1.000 |
| qn2_persona2_primaria | sube | C_difendif | G1-G2 | 27 | 0.0050 | 14 | 1.000 | 1.000 |
| qn2_persona2_secundaria | sube | A_salto | G1 | 27 | -0.0050 | 12 | 0.570 | 1.000 |
| qn2_persona2_secundaria | sube | A_salto | G2 | 27 | -0.0100 | 12 | 0.838 | 1.000 |
| qn2_persona2_secundaria | sube | B_tendencia | G1 | 26 | -0.0015 | 11 | 0.909 | 1.000 |
| qn2_persona2_secundaria | sube | B_tendencia | G2 | 27 | -0.0119 | 10 | 0.786 | 1.000 |
| qn2_persona2_secundaria | sube | C_difendif | G1-G2 | 26 | 0.0000 | 13 | 0.585 | 1.000 |
| cr2a_z | baja | A_salto | G1 | 27 | 0.1349 | 18 | 0.065 | 1.000 |
| cr2a_z | baja | A_salto | G2 | 27 | -0.0302 | 12 | 0.348 | 1.000 |
| cr2a_z | baja | B_tendencia | G1 | 27 | 0.0964 | 20 | 0.002 | 0.049 |
| cr2a_z | baja | B_tendencia | G2 | 27 | -0.0710 | 10 | 0.135 | 1.000 |
| cr2a_z | baja | C_difendif | G1-G2 | 27 | 0.2377 | 19 | 0.032 | 0.319 |
