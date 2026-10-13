#!/bin/bash
cd /c/BMARIN2003/DEV/proyecto
export PYTHONUTF8=1
until [ "$(ls datos_v2/campana/par*_G?.json 2>/dev/null | wc -l)" -ge 54 ]; do sleep 60; done
py scripts/reporte_v2/consolidar.py --B 10000 > datos_v2/_final_consolidar.log 2>&1
py scripts/reporte_v2/cierre_brechas.py > datos_v2/_final_cierre.log 2>&1
echo listo > datos_v2/_final.ok
