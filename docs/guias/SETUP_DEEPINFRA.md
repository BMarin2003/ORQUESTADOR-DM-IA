# Entorno de inferencia — DeepInfra

Objetivo: dejar el entorno **replicable y auditable** antes de generar una
sola campaña. Lo que se hace aquí es lo que permite demostrar después que
todas las campañas de ambos grupos corrieron contra el mismo artefacto.

---

## 1. Cuenta y clave

1. Crear cuenta en `deepinfra.com`.
2. Ir a la sección de API keys (a veces etiquetada "tokens") y crear una.
3. **Copiarla en el momento**: como en la mayoría de proveedores, el secreto
   completo se muestra una sola vez.
4. Añadir método de pago o crédito. La facturación es por uso; revisar en el
   panel si hay crédito de prueba vigente.

La clave va en variable de entorno, nunca en el código ni en git.

---

## 2. Archivos del entorno

```
proyecto/
├── .env                    ← NO se versiona
├── .env.example            ← sí se versiona, sin secretos
├── .gitignore              ← debe contener .env
└── motor/entorno/
    ├── verificar_modelo.py
    └── manifiesto_AAAA-MM-DD.json   ← sí se versiona
```

`.env`:
```
DEEPINFRA_API_KEY=di_xxxxxxxxxxxxxxxx
DEEPINFRA_BASE_URL=https://api.deepinfra.com/v1/openai
DMIA_MODELO=                      # se rellena en el paso 3
```

Antes de nada, confirmar que `.env` está en `.gitignore`. Una clave filtrada
en el historial de git no se borra rotando el archivo: hay que rotar la clave.

---

## 3. Encontrar el ID exacto del modelo

Los IDs de DeepInfra llevan prefijo de organización y **no tienen alias
cortos**. Un fallo cercano devuelve 404 o "modelo desconocido", no un
mensaje útil.

```bash
export $(grep -v '^#' .env | xargs)
python3 motor/entorno/verificar_modelo.py --listar gemma
```

Copiar el ID **exacto** que devuelva y guardarlo en `DMIA_MODELO`.

Mientras estés en la página del modelo, anotar también:
- La cuantización, si el proveedor la publica.
- El precio por millón de tokens de entrada y salida en esa fecha.
- La ventana de contexto servida (puede ser menor que la nominal del modelo).

---

## 4. Huella de determinismo

```bash
python3 motor/entorno/verificar_modelo.py --modelo "<ID exacto>"
```

Esto genera `manifiesto_AAAA-MM-DD.json` con el hash SHA-256 de la salida de
tres prompts fijos a temperatura 0.

**Por qué esto y no solo la etiqueta de cuantización:** el proveedor puede
cambiar el motor de inferencia, la plantilla de chat o la cuantización sin
cambiar el ID del modelo ni la etiqueta publicada. La huella lo detecta
porque compara la salida real.

Versionar el manifiesto en git. Es la prueba documental de qué artefacto
generó cada campaña.

---

## 5. Comprobación periódica

Antes de cada tanda de campañas, y obligatoriamente al pasar de G2 a G1:

```bash
python3 motor/entorno/verificar_modelo.py \
  --modelo "$DMIA_MODELO" --comparar motor/entorno/manifiesto_2026-08-24.json
```

Si la huella cambió, el script sale con código 2 y muestra el antes/después.

**Qué hacer si cambia a mitad de la recolección:** parar. Las campañas ya
generadas y las siguientes no son comparables. Documentar la fecha del
cambio, y decidir entre regenerar lo anterior o tratar el conjunto como dos
bloques con la asimetría declarada. No continuar sin decidirlo.

> Nota: la reproducibilidad exacta a temperatura 0 no está garantizada en
> ningún proveedor —el batching y el hardware introducen variación—, así que
> una divergencia aislada no prueba un cambio de artefacto. Lo que sí es
> señal fuerte es que **los tres hashes cambien a la vez** o que la muestra
> de texto sea claramente distinta, no una palabra diferente al final.

---

## 6. Conexión desde el orquestador

Endpoint compatible con OpenAI, así que sirve cualquier SDK de OpenAI
cambiando la base URL:

```
https://api.deepinfra.com/v1/openai
```

TypeScript, con el AI SDK que decidimos usar:

```ts
import { createOpenAICompatible } from '@ai-sdk/openai-compatible';

const deepinfra = createOpenAICompatible({
  name: 'deepinfra',
  baseURL: process.env.DEEPINFRA_BASE_URL!,
  apiKey:  process.env.DEEPINFRA_API_KEY!,
});

export const modelo = deepinfra(process.env.DMIA_MODELO!);
```

Ventaja de esta capa: si un proveedor sirve el modelo mal o caro, se cambia
una línea. Los IDs y precios se mueven rápido, así que conviene no cablearlos.

---

## 7. Registro obligatorio por llamada

Toda llamada escribe una fila en `model_calls`:

| Campo | Por qué |
|---|---|
| `provider`, `model_id` | Auditoría de validez |
| `quantization` | Lo que publique el proveedor; si no publica, el hash de la huella vigente |
| `input_tokens`, `output_tokens` | Economía por arquitectura — dato imposible de reconstruir después |
| `latency_ms` | Presupuesto de latencia de G1 |
| `role` | Qué agente hizo la llamada; permite detectar omisiones por fallo |

La consulta 13 de `inspeccion.sql` verifica esto: si devuelve más de una
fila, hubo mezcla de artefactos y el experimento está contaminado.

---

## 8. Reglas de uso

**Un solo proveedor, sin router.** Nada de OpenRouter para las campañas de
evaluación: puede enrutar a proveedores distintos con cuantizaciones
distintas del mismo modelo. Para desarrollo y pruebas, sin problema.

**Los free tiers son para desarrollo.** Varios proveedores dan crédito
inicial. Útil para iterar prompts; nunca para generar campañas evaluadas.

**Presupuesto declarado.** Para la investigación, sin límite en ambos grupos
(coherente con "cada paradigma en su mejor forma"). Pero registrar el
consumo aunque no se limite: de ahí sale el presupuesto de la plataforma,
medido en vez de estimado.

---

## Lista de verificación

- [ ] Cuenta creada y método de pago añadido
- [ ] Clave en `.env`, y `.env` en `.gitignore`
- [ ] ID exacto obtenido con `--listar` y guardado en `DMIA_MODELO`
- [ ] Cuantización, precios y ventana de contexto anotados con fecha
- [ ] Manifiesto generado y versionado en git
- [ ] Comprobación de huella agendada antes de cada tanda
- [ ] `model_calls` escribiendo desde la primera llamada