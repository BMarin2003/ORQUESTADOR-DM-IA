# Archivos congelados modificados después del congelamiento

Los manifiestos [`persona2_congelado.sha256`](persona2_congelado.sha256) (detector persona2 v2b, 2026-09-20) y [`../validacion_v2/congelamiento_v2.sha256`](../validacion_v2/congelamiento_v2.sha256) (validación humana v2, 2026-10-28) se conservan tal cual, como registro de lo congelado. Después, la reorganización del repositorio y la documentación del código cambiaron los bytes de algunos de esos archivos, así que **sus hashes actuales ya no coinciden con los manifiestos**.

**Ningún cambio toca la lógica del detector ni de los instrumentos.** Los cambios son de dos tipos:

- **Documentación:** docstrings agregados (commit `5a376e4`) y textos descriptivos que mencionan rutas.
- **Rutas:** la reorganización en `motor/`, `experimento/` y `datos/` (commits `a441cd1` y `7d8ca28`) cambió la profundidad de `RAIZ` y los nombres de carpeta (`scripts/` → `experimento/scripts/`, `orquestador/` → `motor/orquestador/`, `validacion/` → `datos/validacion/`, `datos_v2/` → `datos/datos_v2/`).

## Detalle por archivo

Se tomó como referencia la versión de cada archivo en el commit `b7ac5b1`, donde todos coinciden con el hash congelado.

| Archivo actual | Ruta congelada | Qué cambió | Verificación |
| --- | --- | --- | --- |
| `experimento/scripts/instrumentos/persona2.py` | `scripts/instrumentos/persona2.py` | Docstrings | AST idéntico sin docstrings |
| `experimento/scripts/instrumentos/lexicon_persona2.json` | `scripts/instrumentos/lexicon_persona2.json` | Texto de `_fuentes.general` (`dm/prompt_g2.md` → `motor/dm/prompt_g2.md`) | Todas las listas idénticas; solo difiere el campo descriptivo `_fuentes` |
| `experimento/scripts/instrumentos/respuesta_accion.py` | `scripts/instrumentos/respuesta_accion.py` | Docstrings | AST idéntico sin docstrings |
| `experimento/scripts/instrumentos/test_persona2.py` | `scripts/instrumentos/test_persona2.py` | Docstrings | AST idéntico sin docstrings |
| `experimento/scripts/instrumentos/lemas_es.py` | `scripts/instrumentos/lemas_es.py` | Docstring y rutas (`RAIZ`, `sys.path`) | Revisión del diff: solo rutas |
| `experimento/scripts/instrumentos/confirmacion_persona2.py` | `scripts/instrumentos/confirmacion_persona2.py` | Docstring y ruta de salida (`datos/validacion`) | Revisión del diff: solo rutas |
| `experimento/scripts/reporte_v2/normalizacion.py` | `scripts/reporte_v2/normalizacion.py` | Docstrings y rutas (`RAIZ`, `sys.path`, destino) | Revisión del diff: solo rutas |
| `motor/orquestador/reporte_validacion.py` | `orquestador/reporte_validacion.py` | Docstrings y rutas (`RAIZ`, `sys.path`, mensajes) | Revisión del diff: solo rutas |

Hashes SHA-256 actuales (contenido en git, finales de línea LF):

```
267eac52fe94f9f921cda57531a50f9499254137e395e7699628e0bcf4fb78e4  experimento/scripts/instrumentos/persona2.py
01a7c7644e2c392916549c4d89526e70f00b7fb2937d83c123bd79bd4435bfd9  experimento/scripts/instrumentos/lexicon_persona2.json
101f1ab6ad06d43f513d7e37905c6b2a891f449bc0332df9950bce502a13eef7  experimento/scripts/instrumentos/respuesta_accion.py
8e25eb7e9ad8f7ef3a7ecb0e9f3471cb119452d1222268ec57411a99bf0efe5f  experimento/scripts/instrumentos/test_persona2.py
2f6db9deece60585926232a04b6c3d6cd25872e672e6f3e2a905615a4cab729d  experimento/scripts/instrumentos/lemas_es.py
2c2321dcff58a791e14aabba9cdf9f92bd5ea07e36fb0b5df3a123541985c7b9  experimento/scripts/instrumentos/confirmacion_persona2.py
30e5afd373f2ff464c4737fc7d96f6f79de92af2c18ae2e43aae456fba137d6c  experimento/scripts/reporte_v2/normalizacion.py
60f267a5c1ae2e8927a6a0a3399f8b4fb907a5e7ec96a71b81600a50e2836af0  motor/orquestador/reporte_validacion.py
```

Los archivos propios de `validacion_v2/` listados en `congelamiento_v2.sha256` no se modificaron (ruta antigua `validacion_v2/` → `datos/validacion_v2/`). Todos coinciden con su hash, aunque algunos se hashearon con finales de línea LF y otros con CRLF: con `core.autocrlf=true` (Windows), unos coinciden con el contenido en git (`git show HEAD:<ruta> | sha256sum`) y otros con el archivo en disco (`sha256sum <ruta>`).

## Efecto en los scripts

`experimento/scripts/reporte_v2/recalcular_persona2.py` (y `recalcular_persona2_v3b.py`, que usa la misma función) verifica antes de correr que `persona2.py` y el léxico sean los congelados. Acepta los hashes de `persona2_congelado.sha256` o los de [`persona2_congelado_equivalentes.sha256`](persona2_congelado_equivalentes.sha256), que son las versiones de la tabla de arriba. Compara el archivo con finales de línea LF y CRLF, así que funciona en cualquier sistema operativo. Cualquier otro cambio a esos dos archivos sigue abortando la ejecución.

## Cómo comprobarlo

Para ver el diff completo de un archivo contra su versión congelada:

```
git diff -M b7ac5b1 HEAD -- scripts/instrumentos/persona2.py experimento/scripts/instrumentos/persona2.py
```

Para recuperar la versión congelada byte a byte y verificar su hash:

```
git show b7ac5b1:scripts/instrumentos/persona2.py | sha256sum
```

## Observación aparte: `confirmacion_persona2_muestra.csv`

`confirmacion_persona2_muestra.csv` no coincide con su hash en `persona2_congelado.sha256` desde su primer commit (`0b86c02`, 2026-10-12). Es decir, ya difería cuando se versionó por primera vez y no es consecuencia de la reorganización. La clave (`confirmacion_persona2_clave.csv`) y los turnos de desarrollo (`persona2_desarrollo_turnos.csv`) sí coinciden.
