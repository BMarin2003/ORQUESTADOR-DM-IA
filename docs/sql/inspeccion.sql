-- ============================================================================
-- CONSULTAS DE INSPECCIÓN — pegar en el Query Tool de pgAdmin
-- ============================================================================
-- pgAdmin muestra el árbol de objetos, pero estas consultas responden las
-- preguntas que el árbol no responde de un vistazo.
-- ============================================================================


-- 1. INVENTARIO: tabla, columnas, filas estimadas, tamaño, RLS
--    La columna rls es la importante: cualquier tabla en 'SIN RLS' que tenga
--    datos de usuario es una fuga entre tenants.
SELECT c.relname                                              AS tabla,
       (SELECT count(*) FROM information_schema.columns
         WHERE table_name = c.relname AND table_schema = 'public') AS columnas,
       c.reltuples::bigint                                    AS filas_est,
       pg_size_pretty(pg_total_relation_size(c.oid))          AS tamano,
       CASE WHEN c.relrowsecurity THEN 'RLS' ELSE '⚠ SIN RLS' END AS rls
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'public' AND c.relkind = 'r'
 ORDER BY pg_total_relation_size(c.oid) DESC;


-- 2. GRAFO DE DEPENDENCIAS: qué tabla apunta a cuál y qué pasa al borrar
--    Verifica que todo cuelgue de tenants/campaigns con CASCADE: borrar una
--    campaña debe llevarse su mundo entero sin dejar huérfanos.
SELECT tc.table_name        AS origen,
       kcu.column_name      AS columna,
       ccu.table_name       AS destino,
       rc.delete_rule       AS al_borrar
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
  JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
  JOIN information_schema.referential_constraints rc
    ON rc.constraint_name = tc.constraint_name
 WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
 ORDER BY ccu.table_name, tc.table_name;


-- 3. POLÍTICAS RLS ACTIVAS con su expresión
SELECT tablename AS tabla, policyname AS politica, cmd AS comando, qual AS condicion
  FROM pg_policies WHERE schemaname = 'public'
 ORDER BY tablename;


-- 4. TABLAS SIN RLS — revisar una por una
--    Esperado: tenants (no tiene tenant_id, se protege por GRANT) y
--    mutable_fields (catálogo de referencia compartido). Cualquier otra
--    en esta lista es un error.
SELECT c.relname AS tabla_sin_rls
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'public' AND c.relkind = 'r' AND NOT c.relrowsecurity
 ORDER BY 1;


-- 5. LISTA BLANCA DE CAMPOS MUTABLES
--    Esto es lo que el extractor puede modificar. Nada más existe para él.
SELECT entity_type AS entidad, field_name AS campo, value_kind AS tipo,
       min_value AS min, max_value AS max,
       array_to_string(allowed_values, ' | ') AS valores
  FROM mutable_fields
 ORDER BY entity_type, field_name;


-- 6. TIPOS ENUM y sus valores
SELECT t.typname AS tipo, string_agg(e.enumlabel, ' | ' ORDER BY e.enumsortorder) AS valores
  FROM pg_type t
  JOIN pg_enum e ON t.oid = e.enumtypid
  JOIN pg_namespace n ON n.oid = t.typnamespace
 WHERE n.nspname = 'public'
 GROUP BY t.typname ORDER BY t.typname;


-- 7. FUNCIONES PROPIAS con su firma
SELECT p.proname AS funcion,
       pg_get_function_arguments(p.oid) AS argumentos,
       pg_get_function_result(p.oid)    AS retorna
  FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
 WHERE n.nspname = 'public'
   AND p.proname IN ('apply_delta','advance_clocks','decay_dispositions',
                     'get_visible_state','location_context','stagnation_check',
                     'disposition_band','current_tenant')
 ORDER BY p.proname;


-- 8. ÍNDICES, separando los vectoriales
SELECT tablename AS tabla, indexname AS indice,
       CASE WHEN indexdef LIKE '%hnsw%' THEN 'HNSW (vectorial)'
            WHEN indexdef LIKE '%UNIQUE%' THEN 'único'
            ELSE 'btree' END AS tipo
  FROM pg_indexes WHERE schemaname = 'public'
 ORDER BY (indexdef LIKE '%hnsw%') DESC, tablename;


-- 9. COLUMNAS DE UNA TABLA CONCRETA (cambiar el nombre)
SELECT ordinal_position AS n, column_name AS columna, data_type AS tipo,
       is_nullable AS nullable, column_default AS por_defecto
  FROM information_schema.columns
 WHERE table_schema = 'public' AND table_name = 'npcs'
 ORDER BY ordinal_position;


-- ============================================================================
-- CONSULTAS DE DIAGNÓSTICO — una vez haya datos reales
-- ============================================================================

-- 10. SALUD DEL EXTRACTOR — el fallo silencioso que más importa vigilar.
--     Si deltas_extraidos cae a 0 en sesiones que tuvieron eventos, el
--     pipeline está roto y desde fuera parece "el modelo no recuerda bien".
SELECT s.ordinal AS sesion,
       count(*) FILTER (WHERE d.source = 'extracted')  AS deltas_extraidos,
       count(*) FILTER (WHERE d.source = 'mechanical') AS deltas_mecanicos,
       (SELECT count(*) FROM rejected_deltas r
         WHERE r.campaign_id = s.campaign_id)          AS rechazados,
       count(DISTINCT d.entity_id)                     AS entidades_tocadas
  FROM sessions s LEFT JOIN state_deltas d ON d.session_id = s.id
 GROUP BY s.id, s.ordinal, s.campaign_id
 ORDER BY s.ordinal;


-- 11. TASA DE PASO DE LA COMPUERTA
--     Esperado ~30%. Cerca de 0 = compuerta rota. Cerca de 100 = no filtra.
SELECT campaign_id,
       count(*)                                        AS turnos,
       count(*) FILTER (WHERE gate_passed)             AS pasaron,
       round(100.0 * count(*) FILTER (WHERE gate_passed) / nullif(count(*),0), 1) AS pct
  FROM turn_log GROUP BY campaign_id;


-- 12. ECONOMÍA POR ARQUITECTURA — el dato imposible de reconstruir después.
--     Es lo que responderá si el MAS gana lo suficiente para justificar
--     costar varias veces más por turno.
SELECT c.architecture,
       count(DISTINCT m.turn_id)                       AS turnos,
       round(count(*)::numeric / nullif(count(DISTINCT m.turn_id),0), 2) AS llamadas_por_turno,
       sum(m.input_tokens)                             AS tokens_in,
       sum(m.output_tokens)                            AS tokens_out,
       round(avg(m.latency_ms))                        AS latencia_media_ms
  FROM model_calls m JOIN campaigns c ON c.id = m.campaign_id
 GROUP BY c.architecture;


-- 13. AUDITORÍA DE VALIDEZ — todas las campañas deben compartir
--     proveedor, modelo y cuantización. Más de una fila = experimento
--     contaminado.
SELECT provider, model_id, quantization, count(*) AS llamadas,
       min(created_at) AS desde, max(created_at) AS hasta
  FROM model_calls
 GROUP BY provider, model_id, quantization;


-- 14. RELOJES: qué disparó y qué está por disparar
SELECT f.name AS faccion, fc.agenda, fc.progress, fc.threshold,
       round(100.0 * fc.progress / nullif(fc.threshold,0), 1) AS pct,
       fc.fired_at_turn
  FROM faction_clocks fc JOIN factions f ON f.id = fc.faction_id
 ORDER BY fc.fired_at_turn NULLS FIRST, pct DESC;


-- 15. DISPOSICIONES con su banda conductual
SELECT n.name AS pnj,
       round(d.affinity,1) AS aprecio, disposition_band(d.affinity) AS banda_aprecio,
       round(d.trust,1)    AS confianza, disposition_band(d.trust)  AS banda_confianza,
       round(d.respect,1)  AS respeto,   disposition_band(d.respect) AS banda_respeto,
       d.updated_at_turn
  FROM npc_disposition d JOIN npcs n ON n.id = d.npc_id
 WHERE d.pc_id IS NULL
 ORDER BY abs(d.affinity) DESC;


-- 16. HISTORIA DE UNA ENTIDAD — reconstrucción desde el ledger.
--     Esto es lo que reemplaza al versionado de filas: el estado actual
--     está en la tabla, la historia se lee aquí.
SELECT turn_id, field_name, old_value, new_value, source, left(evidence, 60) AS evidencia
  FROM state_deltas
 WHERE entity_id = '00000000-0000-0000-0000-000000000000'  -- ← poner el uuid
 ORDER BY turn_id;
