-- 002_medicion_semantica.sql
-- ADITIVA: crea UNA tabla nueva y no modifica ninguna existente. Sirve solo a la MEDICIÓN
-- (instrumento exploratorio cl2_recall_semantico, scripts/semantico/); ningún brazo (G1/G2) la lee
-- ni la escribe, y el corpus (turn_log, state_deltas, entidades) no cambia.
--
-- Por qué una tabla aparte y no narrative_chunks:
--   * narrative_chunks pertenece a la capa de GENERACIÓN (memoria narrativa para un futuro RAG) y el
--     experimento nunca la usó; llenarla ahora haría dudar de si los brazos la leyeron.
--   * narrative_chunks tiene un índice HNSW (búsqueda APROXIMADA). La medición necesita búsqueda
--     EXACTA y determinista, y ese índice multiplica el costo de inserción (~30x medido).
-- Se mantiene el principio del esquema: tenant_id en la fila y RLS por tenant.
--
-- Se aplica sola desde scripts/semantico/embeber_corpus.py (idempotente), o a mano:
--   Get-Content migrations\002_medicion_semantica.sql | docker exec -i dmia_db psql -U postgres -d dmia_dev
-- Para deshacer:  DROP TABLE medicion_oraciones;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS medicion_oraciones (
  id           bigserial PRIMARY KEY,
  tenant_id    uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id  uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id      bigint NOT NULL,
  n_oracion    integer NOT NULL,          -- orden de la oración dentro del turno (0, 1, 2…)
  content      text NOT NULL,             -- oración de la narración NORMALIZADA (normalizar_turno)
  embedding    vector(1024) NOT NULL,     -- bge-m3 denso, normalizado (coseno = producto punto)
  modelo       text NOT NULL,             -- 'BAAI/bge-m3@<commit>'
  UNIQUE (campaign_id, turn_id, n_oracion)
);
-- Sin índice HNSW a propósito: las consultas de medición filtran por campaña y rango de turnos
-- (este B-tree) y recorren esas filas de forma exacta.
CREATE INDEX IF NOT EXISTS medicion_oraciones_campana_turno ON medicion_oraciones (campaign_id, turn_id);

ALTER TABLE medicion_oraciones ENABLE ROW LEVEL SECURITY;
DO $$
BEGIN
  CREATE POLICY tenant_isolation ON medicion_oraciones USING (tenant_id = current_tenant());
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
