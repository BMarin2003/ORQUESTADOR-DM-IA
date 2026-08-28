\set ON_ERROR_STOP on
SET session_replication_role = replica;  -- RLS off for setup convenience
SET row_security = off;

-- Semilla
INSERT INTO tenants (id, name) VALUES ('11111111-1111-1111-1111-111111111111','Test') ;
INSERT INTO users (id, tenant_id, email, display_name)
  VALUES ('22222222-2222-2222-2222-222222222222','11111111-1111-1111-1111-111111111111','k@x.pe','Kmotin');
INSERT INTO campaigns (id, tenant_id, owner_id, title, architecture, profile, current_turn)
  VALUES ('33333333-3333-3333-3333-333333333333','11111111-1111-1111-1111-111111111111',
          '22222222-2222-2222-2222-222222222222','Sangre y Zafiro','mas','chronicle', 100);
INSERT INTO campaign_members (campaign_id, user_id, is_dm)
  VALUES ('33333333-3333-3333-3333-333333333333','22222222-2222-2222-2222-222222222222', true);

-- Jerarquía de lugares: reino -> ciudad -> distrito
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name, culture_overrides) VALUES
 ('a0000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333',NULL,'realm','Reino de Vorren','{"language":"vorrenio","currency":"zafiros"}'),
 ('a0000000-0000-0000-0000-000000000002','11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333','a0000000-0000-0000-0000-000000000001','settlement','Puerto Cenizo','{"attitude_to_outsiders":"receloso"}'),
 ('a0000000-0000-0000-0000-000000000003','11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333','a0000000-0000-0000-0000-000000000002','district','Mercado Bajo','{"language":"vorrenio arcaico"}');

-- PNJ tipo Walder Frey: incapaz estructuralmente de confiar
INSERT INTO npcs (id, tenant_id, campaign_id, name, species, warmth, candor, principle, boldness,
                  voice_notes, internal_contradiction, location_id)
  VALUES ('b0000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111',
          '33333333-3333-3333-3333-333333333333','Walder de Vorren','humano',-70,-85,-90,-30,
          'formalidad excesiva, menciona agravios como cortesías',
          'ansía respeto pero solo entiende el miedo','a0000000-0000-0000-0000-000000000003');
INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, trust_ceiling)
  VALUES ('b0000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111',NULL, 20);

-- Facción con reloj
INSERT INTO factions (id, tenant_id, campaign_id, name)
  VALUES ('c0000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333','Culto del Sello');
INSERT INTO faction_clocks (tenant_id, campaign_id, faction_id, agenda, threshold, rate_per_game_day, on_fire_event)
  VALUES ('11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333',
          'c0000000-0000-0000-0000-000000000001','Abrir el sello del sótano', 10, 1.0,
          '{"headline":"El sello se quiebra","scope":"district"}');

SET session_replication_role = origin;

\echo '=== 1. apply_delta mecánico (sin evidencia) ==='
SELECT apply_delta('33333333-3333-3333-3333-333333333333','npc',
  'b0000000-0000-0000-0000-000000000001','status','"dead"'::jsonb, 101,'mechanical') AS delta_id;
SELECT status FROM npcs WHERE id='b0000000-0000-0000-0000-000000000001';

\echo '=== 2. rollback: revivir para seguir probando ==='
SELECT apply_delta('33333333-3333-3333-3333-333333333333','npc',
  'b0000000-0000-0000-0000-000000000001','status','"alive"'::jsonb, 102,'authored') AS delta_id;

\echo '=== 3. apply_delta extraído SIN evidencia -> debe FALLAR ==='
DO $$
BEGIN
  PERFORM apply_delta('33333333-3333-3333-3333-333333333333','npc',
    'b0000000-0000-0000-0000-000000000001','affinity','-5'::jsonb, 103,'extracted');
  RAISE EXCEPTION 'FALLO: aceptó delta extraído sin evidencia';
EXCEPTION WHEN others THEN
  IF position('requires evidence' in SQLERRM) > 0 THEN
    RAISE NOTICE 'OK rechazado: %', SQLERRM;
  ELSE RAISE; END IF;
END $$;

\echo '=== 4. campo fuera de la lista blanca -> debe FALLAR ==='
DO $$
BEGIN
  PERFORM apply_delta('33333333-3333-3333-3333-333333333333','npc',
    'b0000000-0000-0000-0000-000000000001','voice_notes','"cambiado"'::jsonb, 104,'authored');
  RAISE EXCEPTION 'FALLO: aceptó campo no delta-able';
EXCEPTION WHEN others THEN
  IF position('not delta-able' in SQLERRM) > 0 THEN
    RAISE NOTICE 'OK rechazado: %', SQLERRM;
  ELSE RAISE; END IF;
END $$;

\echo '=== 5. valor de enum inválido -> debe FALLAR ==='
DO $$
BEGIN
  PERFORM apply_delta('33333333-3333-3333-3333-333333333333','npc',
    'b0000000-0000-0000-0000-000000000001','status','"zombificado"'::jsonb, 105,'authored');
  RAISE EXCEPTION 'FALLO: aceptó enum inválido';
EXCEPTION WHEN others THEN
  IF position('not allowed' in SQLERRM) > 0 THEN
    RAISE NOTICE 'OK rechazado: %', SQLERRM;
  ELSE RAISE; END IF;
END $$;

\echo '=== 6. numérico fuera de rango -> debe FALLAR ==='
DO $$
BEGIN
  PERFORM apply_delta('33333333-3333-3333-3333-333333333333','npc',
    'b0000000-0000-0000-0000-000000000001','affinity','500'::jsonb, 106,'authored');
  RAISE EXCEPTION 'FALLO: aceptó fuera de rango';
EXCEPTION WHEN others THEN
  IF position('above maximum' in SQLERRM) > 0 THEN
    RAISE NOTICE 'OK rechazado: %', SQLERRM;
  ELSE RAISE; END IF;
END $$;

\echo '=== 7. disposición con evidencia + bandas ==='
SELECT apply_delta('33333333-3333-3333-3333-333333333333','npc',
  'b0000000-0000-0000-0000-000000000001','affinity','-45'::jsonb, 107,'extracted',
  'Walder escupe al suelo cuando mencionan a la Casa Renna') AS delta_id;
SELECT affinity, disposition_band(affinity) AS banda,
       trust, disposition_band(trust) AS banda_trust
  FROM npc_disposition WHERE npc_id='b0000000-0000-0000-0000-000000000001';

\echo '=== 8. old_value quedó registrado en el ledger ==='
SELECT field_name, old_value, new_value, source, left(evidence,40) AS evidencia
  FROM state_deltas WHERE campaign_id='33333333-3333-3333-3333-333333333333'
  ORDER BY id;

\echo '=== 9. advance_clocks: 9 días (no dispara) ==='
SELECT count(*) AS eventos FROM advance_clocks('33333333-3333-3333-3333-333333333333', 9, 108);
SELECT progress, threshold, fired_at_turn FROM faction_clocks;

\echo '=== 10. advance_clocks: +2 días (cruza umbral, DISPARA) ==='
SELECT agenda, event->>'headline' AS titular
  FROM advance_clocks('33333333-3333-3333-3333-333333333333', 2, 109);
SELECT progress, threshold, fired_at_turn FROM faction_clocks;

\echo '=== 11. no vuelve a disparar ==='
SELECT count(*) AS eventos_repetidos FROM advance_clocks('33333333-3333-3333-3333-333333333333', 5, 110);

\echo '=== 12. location_context: herencia jerárquica de cultura ==='
SELECT jsonb_pretty(location_context('a0000000-0000-0000-0000-000000000003'));

\echo '=== 13. decay proporcional (chronicle 3%) ==='
SELECT decay_dispositions('33333333-3333-3333-3333-333333333333', 111) AS filas;
SELECT round(affinity,2) AS affinity_tras_decay, disposition_band(affinity) AS banda
  FROM npc_disposition WHERE npc_id='b0000000-0000-0000-0000-000000000001';

\echo '=== 14. get_visible_state como DM ==='
SELECT entity_type, name, payload->>'affinity_band' AS banda
  FROM get_visible_state('33333333-3333-3333-3333-333333333333',
                         '22222222-2222-2222-2222-222222222222','npc');

\echo '=== 15. world game_day via apply_delta ==='
SELECT apply_delta('33333333-3333-3333-3333-333333333333','world',NULL,'game_day','11'::jsonb,112,'clock');
SELECT game_day FROM campaigns WHERE id='33333333-3333-3333-3333-333333333333';

\echo '=== 16. cola de trabajos: FOR UPDATE SKIP LOCKED ==='
INSERT INTO turn_jobs (tenant_id, campaign_id, kind, payload) VALUES
 ('11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333','turn','{"turn_id":113}'),
 ('11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333','lore_ingest','{}');
UPDATE turn_jobs SET priority = 900 WHERE kind = 'lore_ingest';
WITH claimed AS (
  SELECT id FROM turn_jobs WHERE status='pending'
   ORDER BY priority, created_at FOR UPDATE SKIP LOCKED LIMIT 1)
UPDATE turn_jobs j SET status='running', locked_at=now()
  FROM claimed c WHERE j.id = c.id RETURNING j.kind, j.priority;

\echo '=== 17. pgvector + HNSW operativo ==='
INSERT INTO narrative_chunks (tenant_id, campaign_id, turn_id, content, embedding)
 VALUES ('11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333',107,
         'Walder escupe al suelo', ('[' || array_to_string(array_fill(0.1::real,ARRAY[1024]), ',') || ']')::vector);
SELECT content, round((embedding <=> ('[' || array_to_string(array_fill(0.1::real,ARRAY[1024]),',') || ']')::vector)::numeric, 6) AS distancia
  FROM narrative_chunks ORDER BY embedding <=> ('[' || array_to_string(array_fill(0.1::real,ARRAY[1024]),',') || ']')::vector LIMIT 1;

\echo '=== 18. bond propagation: quien tiene vínculo hacia X ==='
INSERT INTO npc_bond_targets (npc_id, tenant_id, target_type, target_id)
 VALUES ('b0000000-0000-0000-0000-000000000001','11111111-1111-1111-1111-111111111111',
         'location','a0000000-0000-0000-0000-000000000003');
SELECT n.name AS reacciona
  FROM npc_bond_targets b JOIN npcs n ON n.id = b.npc_id
 WHERE b.target_type='location' AND b.target_id='a0000000-0000-0000-0000-000000000003';

\echo '=== 19. entity_relations: CTE recursivo multi-hop ==='
INSERT INTO entity_relations (tenant_id, campaign_id, from_type, from_id, rel_type, to_type, to_id) VALUES
 ('11111111-1111-1111-1111-111111111111','33333333-3333-3333-3333-333333333333','npc','b0000000-0000-0000-0000-000000000001','member_of','faction','c0000000-0000-0000-0000-000000000001');
WITH RECURSIVE walk AS (
  SELECT from_type, from_id, rel_type, to_type, to_id, 1 AS hop
    FROM entity_relations
   WHERE from_id='b0000000-0000-0000-0000-000000000001' AND valid_to_turn IS NULL
  UNION ALL
  SELECT r.from_type, r.from_id, r.rel_type, r.to_type, r.to_id, w.hop+1
    FROM entity_relations r JOIN walk w ON r.from_id = w.to_id
   WHERE w.hop < 3 AND r.valid_to_turn IS NULL)
SELECT rel_type, to_type, hop FROM walk;

\echo '=== 20. stagnation_check (capas SQL) ==='
SELECT jsonb_pretty(stagnation_check('33333333-3333-3333-3333-333333333333', 15));

\echo '=== 21. RLS: aislamiento por tenant ==='
DROP ROLE IF EXISTS app_user;
CREATE ROLE app_user NOLOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_user;
SET row_security = on;
SET ROLE app_user;
SET app.tenant_id = '99999999-9999-9999-9999-999999999999';
SELECT count(*) AS npcs_de_otro_tenant FROM npcs;
SET app.tenant_id = '11111111-1111-1111-1111-111111111111';
SELECT count(*) AS npcs_de_mi_tenant FROM npcs;
RESET ROLE;

\echo '=== 22. RLS en campaign_members (tabla puente sin tenant_id) ==='
SET row_security = on;
SET ROLE app_user;
SET app.tenant_id = '99999999-9999-9999-9999-999999999999';
SELECT count(*) AS membresias_ajenas FROM campaign_members;
SET app.tenant_id = '11111111-1111-1111-1111-111111111111';
SELECT count(*) AS membresias_propias FROM campaign_members;
RESET ROLE;

\echo '=== TODAS LAS PRUEBAS PASARON ==='
