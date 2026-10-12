"""Lleva al deck v2 el resultado de la validación externa de persona2 (E2, E3, E4; 2026-10-09).

    $env:PYTHONUTF8="1"; py scripts/verificacion/actualizar_deck_persona2.py
"""
from pathlib import Path

from pptx import Presentation

from actualizar_deck import forma, poner, reemplazar

RUTA = Path(__file__).resolve().parents[2] / "sustentacion" / "propuestas" / "Sustentacion_MAS_vs_Monolitico_v2.pptx"

NOTA_27 = (" Actualización 10 de octubre: tres DM externos etiquetaron a ciegas 102 ítems. Solo E4 pasó el control de "
           "calidad (E2 marcó «no» en todo, E3 respondió con mediana de 9 segundos). Con E4 la precisión del detector es "
           "33 %, parecida al 26 % de la pasada asistida. Corrigiendo la tasa de cada brazo por su precisión, G1 sigue "
           "por debajo de G2 en 27 de 27 pares, y en el peor caso de los intervalos en 26 de 27. La dirección de H1f se "
           "sostiene; la magnitud de 3.47 % en G2 está inflada, la real ronda 0.5 a 1 %.")


def main():
    """Actualiza el deck con la auditoría de persona2 (precisión corregida, conclusión y trabajo futuro); aserta que cada texto viejo exista."""
    prs = Presentation(RUTA)
    s = prs.slides
    poner(forma(s[26], 5), "r = −1.00 · p < 0.0001 · corregido por la precisión humana (33 %), G1 < G2 en 26–27 de 27 pares")
    n27 = s[26].notes_slide.notes_text_frame
    n27.text = n27.text + NOTA_27
    poner(forma(s[27], 22), "persona2: precisión ≈ 1/3")
    poner(forma(s[27], 23), "3 DM externos; solo 1 pasó el control de calidad. H1f se sostiene corregida, pero su magnitud se infla.")
    assert reemplazar(forma(s[28], 13), "sujeto a la auditoría del detector", "incluso corrigiendo por la precisión del detector"), "lám. 29 conclusión"
    assert reemplazar(forma(s[28], 16), "Completar la auditoría humana de persona2, por arquitectura",
                      "Calibrar persona2: libro de códigos refinado y más evaluadores"), "lám. 29 futuro"
    prs.save(RUTA)
    print(f"actualizado {RUTA}")


if __name__ == "__main__":
    main()
