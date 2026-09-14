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
  world_tone, party_register, rules_visibility, game_day, current_turn,
  content_boundaries)
 VALUES ('766c0249-41ff-596e-b594-cbfc5c511c34', '117003ad-9e5d-5053-bdaa-50e623b78945', 'f79e1783-a941-595a-a198-40d780e004c2', 'El Vado de Ceniza', 'monolithic', 'adventure',
  'mixed', 'mixed', 50,
  12, 0, '{"hard_lines": ["violencia sexual", "tortura descrita en detalle", "genocidio o limpieza étnica", "daño a menores"], "veils": ["muerte de animales", "ejecuciones públicas"]}'::jsonb);
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
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('340e6d03-c6bd-51be-8e70-6c2a2caa3026', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Ilvard', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('b004bb51-ef63-5172-977f-ef5687d72e6d', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Senna', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('7a63e03c-c442-5d47-a0a2-d374b60ac2e3', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Torvald', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('838fe927-630e-500a-b3b1-bf5aaa729026', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Maelis', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('972984f2-4c92-51a4-80b0-cae25ce8692d', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Corvin', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('0258213e-a20f-55f6-83a2-cdb5d62612d1', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Yarah', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('6089093a-4d5a-5106-9b8a-6b67652eac66', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Dunmar', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('2c884ffc-7ea3-58b9-a4de-b588ab825aa5', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Reia', NULL,
  20, 20);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('3593d228-b63c-524d-b4fa-721d52c8cae4', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Aldric', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('87074499-305d-5707-9879-6d8b7488b852', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Bexa', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('56cdc13d-4e63-5a3c-b5d2-58d7d302b89d', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Solvei', NULL,
  20, 20);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('01ca3f0f-ff54-5f45-9709-399a84bdd637', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Harn', NULL,
  32, 32);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('46460078-17df-5356-9cf6-8548620d4612', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Mirek', NULL,
  32, 32);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('4660e60f-c7a1-5c02-a4e3-0d6a02f8f3d1', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Vessa', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('c665192d-dcca-5cbc-aee7-aede3a2257f8', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Otto', NULL,
  20, 20);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('b5f6ff90-5d74-5884-8039-d0ab20ed10c1', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Lianne', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('71647b09-05e0-5cef-88d5-d92156797ed0', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Garrek', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('7d31983b-04ef-5615-8e27-7b488926c38b', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Nadia', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('43fd2f50-b7f6-5b4e-80a9-bfc4415cfa96', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Bram', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('4985be84-f384-5b17-bafe-474868c2f1e7', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Kestra', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('d5ad6a0c-8746-5e57-a81c-2525a65c56e4', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Elior', NULL,
  20, 20);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('9484ca5a-e13f-59f5-b057-b480093b4456', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Wynn', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('642b5a6f-a589-5c5c-9048-b2d54fe51518', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Tarq', NULL,
  20, 20);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('0b08f6a3-30b6-5fa8-b734-9fd2a35af639', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Isolde', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('9a69b847-3407-51cd-ba50-f5d71881d412', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Fenn', NULL,
  28, 28);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('65f20e52-426d-5396-9a98-5519798208b2', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Marta', NULL,
  24, 24);
INSERT INTO characters (id, tenant_id, campaign_id, user_id, name, species,
  hp_current, hp_max)
 VALUES ('41e7a160-b2c8-519e-a007-322840421df5', '117003ad-9e5d-5053-bdaa-50e623b78945', '766c0249-41ff-596e-b594-cbfc5c511c34', 'f79e1783-a941-595a-a198-40d780e004c2', 'Osric', NULL,
  32, 32);

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
