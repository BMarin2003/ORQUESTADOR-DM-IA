-- GENERADO por generar_seed.py — no editar a mano.
-- Regenerar tras cualquier cambio en world.json o personas.json.
BEGIN;
SET LOCAL row_security = off;

-- Idempotente: borra la campaña de fixtures y la recrea.
DELETE FROM campaigns WHERE id = '766c0249-41ff-596e-b594-cbfc5c511c34';
DELETE FROM users     WHERE id = 'f79e1783-a941-595a-a198-40d780e004c2';
DELETE FROM tenants   WHERE id = '117003ad-9e5d-5053-bdaa-50e623b78945';

INSERT INTO tenants (id, name) VALUES ('117003ad-9e5d-5053-bdaa-50e623b78945', 'Fixtures');
INSERT INTO users (id, tenant_id, email, display_name) VALUES ('f79e1783-a941-595a-a198-40d780e004c2', '117003ad-9e5d-5053-bdaa-50e623b78945', 'fixtures@local.dev', 'DM de pruebas');
INSERT INTO campaigns (id, tenant_id, owner_id, title, architecture, profile,
  world_tone, party_register, rules_visibility, game_day, current_turn)
 VALUES ('766c0249-41ff-596e-b594-cbfc5c511c34', '117003ad-9e5d-5053-bdaa-50e623b78945', 'f79e1783-a941-595a-a198-40d780e004c2', 'El Vado de Ceniza', 'monolithic', 'adventure',
  'mixed', 'mixed', 50,
  12, 0);
INSERT INTO campaign_members (campaign_id, user_id, is_dm) VALUES ('766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', true);

-- Lugares (orden de inserción respeta la jerarquía padre→hijo)
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ('a2f54c94-3168-53ff-8663-aa7cadbca0a6', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34',
  NULL,
  'region'::location_kind, 'La Marca Gris',
  'sketch'::detail_level, NULL,
  NULL, '{"language": "común", "currency": "coronas de plata", "attitude_to_outsiders": "indiferente"}'::jsonb,
  'party'::visibility_level);
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ('a98cfa3b-9e6c-5a7c-9066-70b1d6a71107', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34',
  'a2f54c94-3168-53ff-8663-aa7cadbca0a6',
  'settlement'::location_kind, 'Vado de Ceniza',
  'observed'::detail_level, NULL,
  'Un pueblo de tablones grises apretado contra el único puente de piedra en cuarenta leguas. Huele a río y a brea. Todo el que pasa, paga.', '{"notable_laws": "el paso del puente se cobra por cabeza y por bestia", "attitude_to_outsiders": "receloso", "tensions": "el Gremio subió el peaje tres veces en un año"}'::jsonb,
  'party'::visibility_level);
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ('9e0fdc9e-5502-5365-a0c8-f2f551a26390', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34',
  'a98cfa3b-9e6c-5a7c-9066-70b1d6a71107',
  'district'::location_kind, 'El Mercado Bajo',
  'observed'::detail_level, NULL,
  'Doce puestos bajo toldos remendados, en la ribera que se inunda cada primavera. Nadie construye en piedra aquí.', '{"tensions": "los puestos sin licencia del Gremio son desmontados a la fuerza"}'::jsonb,
  'party'::visibility_level);
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ('5b1a45eb-c234-5f53-985a-4105d82a70b9', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34',
  'a98cfa3b-9e6c-5a7c-9066-70b1d6a71107',
  'building'::location_kind, 'La Casa del Peaje',
  'sketch'::detail_level, 'Una torre achaparrada en la cabecera del puente, con una ventanilla enrejada a la altura del pecho.',
  NULL, '{}'::jsonb,
  'party'::visibility_level);
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ('a6b9276e-894c-5a4f-8b2a-c1bc38896854', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34',
  '9e0fdc9e-5502-5365-a0c8-f2f551a26390',
  'building'::location_kind, 'Posada del Remo Roto',
  'observed'::detail_level, NULL,
  'Techo bajo, ocho mesas, un remo partido clavado sobre el hogar. La única puerta da al mercado.', '{}'::jsonb,
  'party'::visibility_level);
INSERT INTO locations (id, tenant_id, campaign_id, parent_id, kind, name,
  detail, sketch_text, description_canonical, culture_overrides, visibility)
 VALUES ('d9e6c48a-c933-5bc7-b332-b8900b473d05', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34',
  'a2f54c94-3168-53ff-8663-aa7cadbca0a6',
  'ruin'::location_kind, 'El Molino Viejo',
  'sketch'::detail_level, 'Río arriba, media rueda todavía en pie. Nadie lo usa desde la crecida.',
  NULL, '{}'::jsonb,
  'dm_only'::visibility_level);

-- Facciones y relojes
INSERT INTO factions (id, tenant_id, campaign_id, name, description,
  seat_location_id, stance_party, knows_about_party)
 VALUES ('1047de29-8887-553a-84d2-75c0e4eefd21', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'El Gremio del Vado', 'Cobra el paso del puente desde hace ochenta años. Tiene la única licencia de comercio del pueblo y su propia guardia pagada.',
  '5b1a45eb-c234-5f53-985a-4105d82a70b9', 0,
  false);
INSERT INTO faction_clocks (tenant_id, campaign_id, faction_id, agenda,
  progress, threshold, rate_per_game_day, on_fire_event)
 VALUES ('117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', '1047de29-8887-553a-84d2-75c0e4eefd21', 'Desmontar todos los puestos sin licencia del Mercado Bajo',
  6, 10, 0.5, '{"headline": "La guardia del Gremio entra en el Mercado Bajo al amanecer", "scope": "mercado_bajo", "consequence": "Los puestos sin licencia arden. Dos vendedores heridos."}'::jsonb);

-- Misiones
INSERT INTO quests (id, tenant_id, campaign_id, title, description, status,
  next_step_known, visibility)
 VALUES ('18f6f1a9-d80a-52a8-8597-885d52618e56', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'El peaje que no consta en el libro', 'Alguien cobra un segundo peaje en el turno de noche y no lo registra.',
  'active'::quest_status, true,
  'party'::visibility_level);
INSERT INTO quests (id, tenant_id, campaign_id, title, description, status,
  next_step_known, visibility)
 VALUES ('54cec31d-08a4-5243-98cc-4885b56c12a2', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'Lo que quedó en el molino', 'El molino viejo no está tan vacío como dicen.',
  'unknown'::quest_status, false,
  'dm_only'::visibility_level);

-- Personajes jugadores
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('19b9ce93-39dc-5faa-bfce-51d40a4ed5b5', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Kael', 'humano',
  28, 31);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('10c6d57a-5d9c-5dd8-9906-cdd5b0d838f2', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Mira', 'halfling',
  19, 22);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('4091d24a-3159-538e-85b4-a2839ae06cd8', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Tobi', 'elfo',
  14, 17);

-- PNJ, persona, IBF, disposición, conocimiento y secretos
INSERT INTO npcs (id, tenant_id, campaign_id, name, species, social_role,
  appearance, status, location_id, warmth, candor, principle, boldness,
  traits, internal_contradiction, taboos, voice_notes,
  stated_desire, actual_need, fear)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'Ordulf Bec', 'humano',
  'recaudador del peaje, tercera generación', 'Sesenta años, manos manchadas de tinta, un anillo del Gremio demasiado apretado que nunca se quita.',
  'alive'::npc_status,
  '5b1a45eb-c234-5f53-985a-4105d82a70b9',
  -70, -85, -90, -30,
  ARRAY['meticuloso','rencoroso','servil hacia arriba']::text[], 'Ansía que lo traten como a un señor, y solo sabe conseguir que lo traten como a un cobrador.', ARRAY['hablar mal del Gremio en voz alta','perdonar una deuda']::text[],
  'Formalidad excesiva con todo el mundo. Dice ''vuestra merced'' incluso al insultar. Menciona agravios viejos como si fueran cortesías: ''como aquella vez que vuestro amigo olvidó pagar, que no se lo tengo en cuenta''. Nunca alza la voz. Nunca dice ''no'' directamente: dice ''sería irregular''.', 'Que el libro de peajes cuadre al céntimo.', 'Que alguien del Gremio lo llame por su apellido y no por su cargo.',
  'Que descubran que lleva ocho años redondeando a su favor.');
INSERT INTO npc_ibf (npc_id, tenant_id, ideal_text, ideal_tags, bond_text,
  bond_strength, flaw_text, flaw_tags, flaw_exploit)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', 'El que paga, pasa. El que no paga, no pasa. Eso es todo el orden que hay.', ARRAY['orden','riqueza']::text[],
  'El apellido Bec lleva tres generaciones en esta torre. No se pierde conmigo.', 85,
  'No olvida un desaire de estatus. Nunca. Los anota mentalmente con fecha.', ARRAY['rencor']::text[], 'reconocimiento_publico_de_estatus');
INSERT INTO npc_bond_targets (npc_id, tenant_id, target_type, target_id)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', 'location'::entity_type, '5b1a45eb-c234-5f53-985a-4105d82a70b9');
INSERT INTO npc_bond_targets (npc_id, tenant_id, target_type, target_id)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', 'faction'::entity_type, '1047de29-8887-553a-84d2-75c0e4eefd21');
INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, affinity, trust, respect,
  trust_ceiling, updated_at_turn)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', NULL, -10, -55,
  0, 20, 0);
INSERT INTO npc_knowledge (npc_id, tenant_id, fact, learned_at_turn)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', 'El turno de noche del puente lo cubre su sobrino Hettir desde hace dos meses', 0);
INSERT INTO npc_knowledge (npc_id, tenant_id, fact, learned_at_turn)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', 'Ha estado redondeando el peaje a su favor durante ocho años', 0);
INSERT INTO npc_secrets (npc_id, tenant_id, content, reveal_condition, visibility)
 VALUES ('4021ec1c-11fe-5939-833b-67f6a85b6e54', '117003ad-9e5d-5053-bdaa-50e623b78945', 'Su sobrino Hettir cobra un segundo peaje de noche y Ordulf lo sabe, pero callar le sale más barato que denunciarlo.', 'Solo si alguien le demuestra que el Gremio ya sospecha de ÉL, y ofrecerle a Hettir es la única salida.',
  'dm_only'::visibility_level);
INSERT INTO npcs (id, tenant_id, campaign_id, name, species, social_role,
  appearance, status, location_id, warmth, candor, principle, boldness,
  traits, internal_contradiction, taboos, voice_notes,
  stated_desire, actual_need, fear)
 VALUES ('550bd81d-b9ff-57d1-a36b-a5ee8fa47098', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'Sargento Brea', 'enana',
  'guardia del puente, no pertenece al Gremio', 'Cuarenta y tantos, una cicatriz que le cruza la ceja, la cota siempre limpia aunque esté remendada.',
  'alive'::npc_status,
  'a98cfa3b-9e6c-5a7c-9066-70b1d6a71107',
  55, 90, 95, 60,
  ARRAY['directa','incómodamente honesta','leal a la gente antes que al cargo']::text[], 'Su deber es hacer cumplir las órdenes del Gremio, y sabe que el Gremio está podrido. No se ha ido porque irse sería dejar el puesto a alguien peor.', ARRAY['mentir, ni siquiera por conveniencia','cobrar por hacer su trabajo']::text[],
  'Frases cortas. Dice lo que piensa antes de calcular si conviene. Si algo le parece mal lo dice en el momento y delante de quien sea. Usa ''muchacho'' y ''muchacha'' con todo el mundo, incluidos los que le doblan la edad.', 'Que el puente esté vigilado y nadie muera en su turno.', 'Que alguien le dé una razón para creer que el pueblo se puede arreglar.',
  'Convertirse en lo que vigila.');
INSERT INTO npc_ibf (npc_id, tenant_id, ideal_text, ideal_tags, bond_text,
  bond_strength, flaw_text, flaw_tags, flaw_exploit)
 VALUES ('550bd81d-b9ff-57d1-a36b-a5ee8fa47098', '117003ad-9e5d-5053-bdaa-50e623b78945', 'La palabra dada vale más que el contrato firmado. El contrato lo redacta un abogado; la palabra la sostiene uno.', ARRAY['honor','honestidad','deber']::text[],
  'Los vendedores del Mercado Bajo. Los conoce a todos por su nombre y ninguno ha muerto en su turno.', 80,
  'Rígida. No miente ni cuando mentir salvaría a alguien, y eso ya le costó un amigo.', ARRAY['rigidez']::text[], 'forzarla_a_jurar_algo');
INSERT INTO npc_bond_targets (npc_id, tenant_id, target_type, target_id)
 VALUES ('550bd81d-b9ff-57d1-a36b-a5ee8fa47098', '117003ad-9e5d-5053-bdaa-50e623b78945', 'location'::entity_type, '9e0fdc9e-5502-5365-a0c8-f2f551a26390');
INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, affinity, trust, respect,
  trust_ceiling, updated_at_turn)
 VALUES ('550bd81d-b9ff-57d1-a36b-a5ee8fa47098', '117003ad-9e5d-5053-bdaa-50e623b78945', NULL, 15, 10,
  0, 90, 0);
INSERT INTO npc_knowledge (npc_id, tenant_id, fact, learned_at_turn)
 VALUES ('550bd81d-b9ff-57d1-a36b-a5ee8fa47098', '117003ad-9e5d-5053-bdaa-50e623b78945', 'El Gremio le ordenó desmontar los puestos sin licencia y ella lleva tres semanas retrasándolo', 0);
INSERT INTO npc_secrets (npc_id, tenant_id, content, reveal_condition, visibility)
 VALUES ('550bd81d-b9ff-57d1-a36b-a5ee8fa47098', '117003ad-9e5d-5053-bdaa-50e623b78945', 'Tiene la orden firmada de desalojo del Mercado Bajo guardada sin ejecutar. Si el Gremio se entera, la despiden y mandan a alguien que sí la cumpla.', 'Se lo cuenta a quien le haya demostrado con hechos que se preocupa por los vendedores, y solo si le preguntan directamente.',
  'dm_only'::visibility_level);
INSERT INTO npcs (id, tenant_id, campaign_id, name, species, social_role,
  appearance, status, location_id, warmth, candor, principle, boldness,
  traits, internal_contradiction, taboos, voice_notes,
  stated_desire, actual_need, fear)
 VALUES ('db3b0b07-4196-5823-961f-adaf3fbe1864', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'Nena', 'humana',
  'posadera del Remo Roto', 'Delantal, antebrazos de cargar barriles.',
  'alive'::npc_status,
  'a6b9276e-894c-5a4f-8b2a-c1bc38896854',
  0, 0, 0, 0,
  '{}', NULL, '{}',
  'Práctica. Habla de precios y de cuartos.', NULL, NULL,
  NULL);
INSERT INTO npc_ibf (npc_id, tenant_id, ideal_text, ideal_tags, bond_text,
  bond_strength, flaw_text, flaw_tags, flaw_exploit)
 VALUES ('db3b0b07-4196-5823-961f-adaf3fbe1864', '117003ad-9e5d-5053-bdaa-50e623b78945', NULL, '{}',
  NULL, NULL,
  NULL, '{}', NULL);
INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, affinity, trust, respect,
  trust_ceiling, updated_at_turn)
 VALUES ('db3b0b07-4196-5823-961f-adaf3fbe1864', '117003ad-9e5d-5053-bdaa-50e623b78945', NULL, 0, 0,
  0, 100, 0);

COMMIT;

-- Comprobación
SELECT 'lugares' AS tabla, count(*) FROM locations
UNION ALL SELECT 'pnj', count(*) FROM npcs
UNION ALL SELECT 'disposiciones', count(*) FROM npc_disposition
UNION ALL SELECT 'vinculos', count(*) FROM npc_bond_targets
UNION ALL SELECT 'secretos', count(*) FROM npc_secrets
UNION ALL SELECT 'relojes', count(*) FROM faction_clocks;
