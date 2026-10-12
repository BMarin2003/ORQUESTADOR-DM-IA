#!/bin/bash
cd /c/BMARIN2003/DEV/proyecto
export PYTHONUTF8=1
until [ -f datos_v2/_final.ok ]; do sleep 30; done
py scripts/reporte_v2/resultados_tesis.py > datos_v2/_final_paquete.log 2>&1
py scripts/reporte_v2/consolidar.py --B 10000 > datos_v2/_final_consolidar2.log 2>&1
echo listo > datos_v2/_paquete.ok
