# website

Sitio de documentación (Docusaurus 3). La referencia de código se genera desde los docstrings con
[`scripts/documentacion/generar_referencia_api.py`](../scripts/documentacion/generar_referencia_api.py)
(`npm start` y `npm run build` la ejecutan antes) y no se versiona.

```powershell
cd website
npm install
npm start        # servidor local con recarga
npm run build    # sitio estático en build/
```
