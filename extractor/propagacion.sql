-- ============================================================================
-- PROPAGACIÓN — cierra el fallo de `knows_about_party`
-- El extractor NO debe inferir que el testigo del puente pertenece al Gremio.
-- Reporta `witnessed`; el sistema recorre entity_relations y decide.
-- ============================================================================

CREATE OR REPLACE FUNCTION propagate_from_delta(
  p_campaign_id uuid,
  p_entity_type entity_type,
  p_entity_id   uuid,
  p_field       text,
  p_value       jsonb,
  p_turn_id     bigint,
  p_witnessed   boolean DEFAULT NULL
) RETURNS TABLE (faction_id uuid, faction_name text, event event_kind, motivo text)
LANGUAGE plpgsql AS $$
BEGIN
  -- Sin testigo declarado no se propaga. "No consta" no es "sí ocurrió".
  IF p_witnessed IS NOT TRUE THEN
    RETURN;
  END IF;

  -- Daño a un PNJ → sus facciones se enteran y reaccionan.
  IF p_entity_type = 'npc' AND p_field = 'status'
     AND (p_value #>> '{}') IN ('dead','missing','captured') THEN

    RETURN QUERY
    WITH afectadas AS (
      SELECT r.to_id AS fid
        FROM entity_relations r
       WHERE r.campaign_id = p_campaign_id
         AND r.from_type = 'npc' AND r.from_id = p_entity_id
         AND r.to_type = 'faction'
         AND r.rel_type IN ('member_of','serves','kin')
         AND r.valid_to_turn IS NULL
    ), marcadas AS (
      UPDATE factions f
         SET knows_about_party = true
        FROM afectadas a
       WHERE f.id = a.fid AND f.campaign_id = p_campaign_id
      RETURNING f.id, f.name
    )
    SELECT m.id, m.name, 'bond_target_harmed'::event_kind,
           format('un miembro de la facción pasó a %s con testigos', p_value #>> '{}')
      FROM marcadas m;
  END IF;

  -- Daño a un lugar controlado por una facción.
  IF p_entity_type = 'location' AND p_field = 'state'
     AND (p_value #>> '{}') IN ('damaged','destroyed') THEN
    RETURN QUERY
    WITH marcadas AS (
      UPDATE factions f SET knows_about_party = true
       WHERE f.campaign_id = p_campaign_id
         AND f.id = (SELECT controlling_faction_id FROM locations WHERE id = p_entity_id)
      RETURNING f.id, f.name)
    SELECT m.id, m.name, 'bond_target_harmed'::event_kind,
           'un lugar bajo su control resultó dañado con testigos'
      FROM marcadas m;
  END IF;
END;
$$;