-- ============================================================================
-- QuestMasters / DM-IA  —  Esquema canónico
-- PostgreSQL 16 + pgvector
--
-- Principios de diseño:
--   1. Multi-tenant desde el día uno: tenant_id en toda tabla, RLS activo.
--   2. Estado actual en la tabla de entidad; historia en el ledger de deltas.
--      La reconstrucción a un turno pasado se hace revirtiendo deltas.
--   3. Toda escritura narrativa pasa por apply_delta(). Si no pasó por ahí,
--      no ocurrió.
--   4. Lista blanca de campos mutables como DATO (tabla), no como código.
--   5. La creación de entidades NO es un delta: es operación explícita.
--   6. turn_log es append-only y es la fuente de verdad reproducible.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- 1. TIPOS
-- ============================================================================

-- Visibilidad por fila/campo. La asimetría de información es estructural:
-- lo que el DM sabe no es lo que el grupo sabe.
CREATE TYPE visibility_level AS ENUM ('dm_only', 'party', 'player');

-- Perfil de campaña: gobierna sensibilidad, decay y densidad de rastreo.
CREATE TYPE campaign_profile AS ENUM ('chronicle', 'adventure', 'episodic');

-- Tono del mundo y registro del grupo son EJES INDEPENDIENTES.
-- Un payaso en un mundo grimdark es configuración válida, no error.
CREATE TYPE world_tone     AS ENUM ('grimdark', 'heroic', 'light', 'mixed');
CREATE TYPE party_register  AS ENUM ('serious', 'mixed', 'comedic');

-- Nivel de detalle de un lugar. 'sketch' no persiste entidades hijas;
-- colapsa a 'observed' cuando el grupo pregunta.
CREATE TYPE detail_level AS ENUM ('sketch', 'observed', 'full');

-- Los tipos que exigen pre-generación completa (topología acoplada) vs.
-- los que admiten boceto.
CREATE TYPE location_kind AS ENUM (
  'region', 'realm', 'settlement', 'district', 'building',
  'dungeon', 'ruin', 'crypt', 'wilderness', 'landmark'
);

CREATE TYPE npc_status     AS ENUM ('alive', 'dead', 'missing', 'captured');
CREATE TYPE location_state AS ENUM ('intact', 'damaged', 'destroyed', 'occupied', 'abandoned');
CREATE TYPE quest_status   AS ENUM ('unknown', 'active', 'completed', 'failed', 'abandoned');

CREATE TYPE entity_type AS ENUM ('npc', 'location', 'faction', 'quest', 'character', 'item', 'world');

CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed');
CREATE TYPE job_kind   AS ENUM ('turn', 'session_close', 'lore_ingest', 'backfill');

-- Origen de un delta. Gobierna la política de escritura:
-- 'mechanical' escribe inmediato sin modelo; 'extracted' requiere evidencia.
CREATE TYPE delta_source AS ENUM ('mechanical', 'extracted', 'authored', 'clock');

-- Arquitectura que produjo un turno. Para la comparación experimental
-- y para el análisis de economía por turno.
CREATE TYPE architecture AS ENUM ('monolithic', 'mas');

CREATE TYPE agent_role AS ENUM (
  'monolithic', 'router', 'narrator', 'arbiter', 'npc_actor', 'world', 'extractor'
);

-- ============================================================================
-- 2. TENANCÍA
-- ============================================================================

CREATE TABLE tenants (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email       text NOT NULL,
  display_name text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, email)
);

-- ============================================================================
-- 3. CAMPAÑA Y CONFIGURACIÓN
-- ============================================================================

CREATE TABLE campaigns (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  owner_id        uuid NOT NULL REFERENCES users(id),
  title           text NOT NULL,

  -- Variable independiente del experimento. Fija por campaña.
  architecture    architecture NOT NULL,

  -- Perfil: gobierna decay, densidad de rastreo, mecánicas opcionales.
  profile         campaign_profile NOT NULL DEFAULT 'adventure',

  -- Tono: dos ejes independientes + si el contraste es rasgo o problema.
  world_tone      world_tone     NOT NULL DEFAULT 'heroic',
  party_register  party_register NOT NULL DEFAULT 'mixed',
  tone_contrast_allowed boolean  NOT NULL DEFAULT true,

  -- 0 = cuentacuentos (reglas invisibles), 100 = manual estricto (todo expuesto).
  -- El Árbitro calcula igual en todos los niveles; cambia la VISIBILIDAD.
  rules_visibility  smallint NOT NULL DEFAULT 50
                    CHECK (rules_visibility BETWEEN 0 AND 100),

  -- Sensibilidad de disposición y decaimiento PROPORCIONAL por sesión.
  -- Proporcional, no fijo: un +3 de cortesía se disuelve, un -40 de traición no.
  disposition_sensitivity numeric(4,2) NOT NULL DEFAULT 1.00
                          CHECK (disposition_sensitivity BETWEEN 0 AND 2),
  disposition_decay_pct   numeric(4,2) NOT NULL DEFAULT 3.00
                          CHECK (disposition_decay_pct BETWEEN 0 AND 50),

  -- Mecánicas opcionales activas (hambre, sed, heridas, descanso extendido).
  optional_mechanics jsonb NOT NULL DEFAULT '{}'::jsonb,

  -- RESTRICCIÓN, no preferencia. Se aplica en la salida, no en el prompt.
  -- Sobrescribe tono, perfil y cualquier semilla. Editable en cualquier momento.
  content_boundaries jsonb NOT NULL DEFAULT
    '{"hard_lines": [], "veils": []}'::jsonb,

  -- Reloj de mundo. Independiente de turn_id y session_id.
  game_day        integer NOT NULL DEFAULT 0,
  current_turn    bigint  NOT NULL DEFAULT 0,

  created_at      timestamptz NOT NULL DEFAULT now(),
  archived_at     timestamptz
);

CREATE INDEX ON campaigns (tenant_id, owner_id);

CREATE TABLE campaign_members (
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  is_dm       boolean NOT NULL DEFAULT false,
  PRIMARY KEY (campaign_id, user_id)
);

CREATE TABLE sessions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  ordinal     integer NOT NULL,
  start_turn  bigint  NOT NULL,
  end_turn    bigint,
  game_day_start integer NOT NULL DEFAULT 0,
  game_day_end   integer,
  opened_at   timestamptz NOT NULL DEFAULT now(),
  closed_at   timestamptz,
  UNIQUE (campaign_id, ordinal)
);

-- ============================================================================
-- 4. LOG DE TURNOS Y COLA DE TRABAJOS
-- ============================================================================

-- Append-only. Nunca se actualiza ni se borra. Es lo que permite reprocesar
-- con un prompt mejor sin haber perdido nada (red de seguridad del recall).
CREATE TABLE turn_log (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id    uuid REFERENCES sessions(id),
  turn_id       bigint NOT NULL,

  -- El buffer: los jugadores escriben varias veces antes de cerrar la
  -- interacción. El rol entre jugadores cuesta CERO llamadas al modelo.
  player_buffer jsonb NOT NULL,           -- [{user_id, pc_id, text, at}]
  dm_output     text,

  scene_tone    text,                     -- volátil, por escena
  location_id   uuid,

  gate_passed   boolean,                  -- ¿pasó la compuerta determinista?
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, turn_id)
);

CREATE INDEX ON turn_log (campaign_id, turn_id DESC);
CREATE INDEX ON turn_log (session_id);

-- Cola en tabla. FOR UPDATE SKIP LOCKED. Sin Redis, sin SQS.
-- Existe desde el día uno porque el navegador SE VA A DESCONECTAR durante
-- un turno de 60-90s, y el turno debe completarse igual.
CREATE TABLE turn_jobs (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  kind        job_kind   NOT NULL,
  status      job_status NOT NULL DEFAULT 'pending',
  priority    smallint   NOT NULL DEFAULT 100,  -- lore_ingest: baja prioridad
  payload     jsonb      NOT NULL DEFAULT '{}'::jsonb,
  attempts    smallint   NOT NULL DEFAULT 0,
  last_error  text,
  locked_at   timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz
);

CREATE INDEX ON turn_jobs (status, priority, created_at) WHERE status = 'pending';

-- Auditoría de validez experimental + economía por arquitectura.
-- Dato barato de recolectar ahora, imposible de reconstruir después.
CREATE TABLE model_calls (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id       bigint,
  role          agent_role NOT NULL,
  provider      text NOT NULL,            -- 'deepinfra' — UN proveedor, fijo
  model_id      text NOT NULL,
  quantization  text,                     -- registrado: variación invalida
  input_tokens  integer NOT NULL,
  output_tokens integer NOT NULL,
  latency_ms    integer,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON model_calls (campaign_id, turn_id);

-- ============================================================================
-- 5. MUNDO: LUGARES (JERÁRQUICOS), FACCIONES, MISIONES
-- ============================================================================

-- Herencia jerárquica: región → reino → asentamiento → distrito → edificio.
-- Cada nivel declara solo lo que DIFIERE de su padre. "Coherente con la
-- cultura local" pasa a ser un SELECT sobre la cadena de ancestros, no una
-- instrucción al modelo que puede olvidar.
CREATE TABLE locations (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  parent_id     uuid REFERENCES locations(id) ON DELETE CASCADE,
  kind          location_kind NOT NULL,
  name          text NOT NULL,

  -- Boceto vs. observado. Al colapsar, description_canonical se CONGELA:
  -- si vuelven, reciben la misma descripción desde el registro.
  -- Y si el estado del mundo cambió, el diff ES contenido narrativo.
  detail         detail_level NOT NULL DEFAULT 'sketch',
  sketch_text    text,
  description_canonical text,
  observed_at_turn bigint,

  state          location_state NOT NULL DEFAULT 'intact',
  controlling_faction_id uuid,

  -- Solo lo que difiere del padre. NULL = hereda.
  culture_overrides jsonb NOT NULL DEFAULT '{}'::jsonb,
  -- {language, currency, notable_laws, attitude_to_outsiders, tensions}

  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON locations (campaign_id, parent_id);
CREATE INDEX ON locations (campaign_id, kind);

CREATE TABLE factions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name          text NOT NULL,
  description   text,
  seat_location_id uuid REFERENCES locations(id),

  -- Disposición de facción hacia el grupo (acumulador continuo).
  stance_party  numeric(6,2) NOT NULL DEFAULT 0
                CHECK (stance_party BETWEEN -100 AND 100),
  knows_about_party boolean NOT NULL DEFAULT false,

  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0
);

CREATE INDEX ON factions (campaign_id);

-- Los relojes convierten las repercusiones de propiedad emergente FRÁGIL
-- en GARANTÍA del sistema. El evento ocurre porque el contador llegó al
-- umbral, no porque el modelo se acordó. El modelo solo narra un hecho
-- que ya es verdad en la base.
CREATE TABLE faction_clocks (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  faction_id    uuid NOT NULL REFERENCES factions(id) ON DELETE CASCADE,
  agenda        text NOT NULL,
  progress      numeric(6,2) NOT NULL DEFAULT 0,
  threshold     numeric(6,2) NOT NULL,
  rate_per_game_day numeric(6,3) NOT NULL DEFAULT 1.0,
  paused        boolean NOT NULL DEFAULT false,
  fired_at_turn bigint,
  on_fire_event jsonb NOT NULL DEFAULT '{}'::jsonb,
  visibility    visibility_level NOT NULL DEFAULT 'dm_only'
);

CREATE INDEX ON faction_clocks (campaign_id) WHERE NOT paused AND fired_at_turn IS NULL;

CREATE TABLE quests (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  title         text NOT NULL,
  description   text,
  status        quest_status NOT NULL DEFAULT 'unknown',

  -- Capa 1 de la detección de estancamiento: ¿hay algún objetivo con
  -- paso siguiente conocido? Puro SQL, gratis.
  next_step_known boolean NOT NULL DEFAULT false,

  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0
);

CREATE INDEX ON quests (campaign_id, status);

-- Semillas SIN ubicación. El plan es inventario de material disponible,
-- no secuencia de escenas. Se plantan DONDE EL GRUPO ESTÉ.
-- El grupo que monta un puesto en el mercado no está estancado: está
-- jugando, y el material planificado no se desperdicia.
CREATE TABLE session_seeds (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id    uuid REFERENCES sessions(id),
  kind          text NOT NULL,     -- threat | npc_agenda | revelation | hook
  content       text NOT NULL,
  location_id   uuid REFERENCES locations(id),  -- NULL = sin ubicar (default)
  planted_at_turn bigint,
  visibility    visibility_level NOT NULL DEFAULT 'dm_only'
);

CREATE INDEX ON session_seeds (campaign_id) WHERE planted_at_turn IS NULL;

-- ============================================================================
-- 6. PNJ: NÚCLEO, PERSONA, DISPOSICIÓN, CONOCIMIENTO
-- ============================================================================

-- Un solo agente ACTOR habita todas las fichas ("un actor para toda la obra").
-- La consistencia de personaje NO es propiedad emergente del modelo: es
-- propiedad del registro en base de datos. Si Elara suena igual en la sesión
-- 8 que en la 1, es porque voice_notes contiene la misma cadena.
CREATE TABLE npcs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name          text NOT NULL,
  species       text,
  culture_id    uuid,                -- cultura AUTORADA, desacoplada de especie
  social_role   text,
  appearance    text,

  status        npc_status NOT NULL DEFAULT 'alive',
  location_id   uuid REFERENCES locations(id),

  -- Personalidad: rasgo ESTABLE. No se mueve porque el grupo le caiga bien.
  -- Cuatro ejes (barato: inmutable, autorado, sin extractor que lo juzgue).
  warmth        smallint NOT NULL DEFAULT 0 CHECK (warmth    BETWEEN -100 AND 100),
  candor        smallint NOT NULL DEFAULT 0 CHECK (candor    BETWEEN -100 AND 100),
  principle     smallint NOT NULL DEFAULT 0 CHECK (principle BETWEEN -100 AND 100),
  boldness      smallint NOT NULL DEFAULT 0 CHECK (boldness  BETWEEN -100 AND 100),

  -- La riqueza vive aquí: contradicción interna, deseo vs. necesidad.
  traits            text[],
  internal_contradiction text,
  taboos            text[],
  voice_notes       text,             -- registro, muletillas, qué NO diría
  stated_desire     text,
  actual_need       text,
  fear              text,

  -- Solo la escala TEMPORAL depende de la especie, no el temperamento.
  -- Un elfo guarda un rencor más tiempo; eso no lo hace altivo.
  decay_multiplier numeric(4,2) NOT NULL DEFAULT 1.00,

  -- Efímero vs. persistido. Por defecto los PNJ de paso NO tocan la BD;
  -- se promueven cuando el grupo les presta atención (los 3 kobolds con
  -- gabardina se vuelven personajes porque los jugadores lo decidieron).
  is_persistent    boolean NOT NULL DEFAULT true,
  promoted_at_turn bigint,
  appearance_count integer NOT NULL DEFAULT 0,

  visibility       visibility_level NOT NULL DEFAULT 'party',
  created_at_turn  bigint NOT NULL DEFAULT 0,
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON npcs (campaign_id, status);
CREATE INDEX ON npcs (campaign_id, location_id);

-- Ideal / Vínculo / Defecto: prosa para el ACTOR, referencias tipadas para
-- el EXTRACTOR. El extractor nunca juzga "¿tocó su vínculo?" — pregunta
-- "¿alguna entidad afectada está en bond_targets?", que es un WHERE IN.
-- Nulo es estado normal: un tabernero de paso no modula nada.
CREATE TABLE npc_ibf (
  npc_id        uuid PRIMARY KEY REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

  ideal_text    text,
  ideal_tags    text[],       -- vocabulario CERRADO de 15 etiquetas
  bond_text     text,
  bond_strength smallint DEFAULT 50 CHECK (bond_strength BETWEEN 0 AND 100),
  flaw_text     text,
  flaw_tags     text[],
  flaw_exploit  text          -- enum de superficie de manipulación
);

-- Los vínculos apuntan a ENTIDADES. Consultables en ambas direcciones:
-- "¿quién tiene un vínculo hacia X?" propaga deltas sin programar nada.
-- Un salto, y solo si el PNJ PUDO enterarse (ver npc_knowledge).
CREATE TABLE npc_bond_targets (
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  target_type   entity_type NOT NULL,
  target_id     uuid NOT NULL,
  PRIMARY KEY (npc_id, target_type, target_id)
);

CREATE INDEX ON npc_bond_targets (target_type, target_id);

-- Disposición: acumuladores CONTINUOS, presentados al modelo en BANDAS.
-- Continuo resuelve que muchos gestos pequeños sumen; las bandas resuelven
-- que el actor pueda interpretarlo. El modelo NUNCA ve el número.
-- Tres ejes permiten estados imposibles en uno: "te aprecia y no te cuenta",
-- "te desprecia y te teme".
CREATE TABLE npc_disposition (
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  -- NULL = hacia el grupo entero; UUID = hacia un PJ concreto.
  -- En intriga, que un PNJ prefiera a un PJ sobre otro es medio juego.
  pc_id         uuid,

  affinity      numeric(6,2) NOT NULL DEFAULT 0 CHECK (affinity BETWEEN -100 AND 100),
  trust         numeric(6,2) NOT NULL DEFAULT 0 CHECK (trust    BETWEEN -100 AND 100),
  respect       numeric(6,2) NOT NULL DEFAULT 0 CHECK (respect  BETWEEN -100 AND 100),

  -- Topes por personalidad: Walder Frey es ESTRUCTURALMENTE incapaz de
  -- confiar (trust máx +20); Ned Stark rompe una vez y para siempre.
  trust_ceiling numeric(6,2) NOT NULL DEFAULT 100,
  trust_floor   numeric(6,2) NOT NULL DEFAULT -100,

  updated_at_turn bigint NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX npc_disposition_key
  ON npc_disposition (npc_id, COALESCE(pc_id, '00000000-0000-0000-0000-000000000000'::uuid));

-- APPEND-ONLY. Un PNJ nunca "desaprende". "¿Qué sabía Elara en el turno 340?"
-- es un WHERE learned_at_turn <= 340. Resuelve la asimetría de información
-- sin lógica adicional, y es el filtro que evita que todos sepan todo al instante.
CREATE TABLE npc_knowledge (
  id            bigserial PRIMARY KEY,
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  fact          text NOT NULL,
  learned_at_turn bigint NOT NULL,
  source        text
);

CREATE INDEX ON npc_knowledge (npc_id, learned_at_turn);

-- Secretos con CONDICIÓN de revelación explícita: el actor sabe qué puede
-- soltar y bajo qué presión, en vez de improvisar revelaciones que rompen trama.
CREATE TABLE npc_secrets (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  content       text NOT NULL,
  reveal_condition text NOT NULL,
  revealed_at_turn bigint,
  visibility    visibility_level NOT NULL DEFAULT 'dm_only'
);

CREATE INDEX ON npc_secrets (npc_id) WHERE revealed_at_turn IS NULL;

-- ============================================================================
-- 7. PERSONAJES JUGADORES
-- ============================================================================

-- Asimetría fundamental: en un PNJ el sistema es dueño de todo.
-- En un PJ, el JUGADOR escribió esos campos y el sistema NO los reescribe.
-- El sistema observa y reporta; el jugador decide y escribe.
CREATE TABLE characters (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  user_id       uuid NOT NULL REFERENCES users(id),

  -- Propiedad del jugador. El sistema solo LEE.
  name          text NOT NULL,
  species       text,
  class_levels  jsonb NOT NULL DEFAULT '[]'::jsonb,
  background    text,
  ideal_text    text,
  bond_text     text,
  flaw_text     text,
  backstory     text,

  -- Propiedad del sistema (mecánico, validado contra SRD).
  hp_current    integer,
  hp_max        integer,
  conditions    text[] NOT NULL DEFAULT '{}',
  inventory     jsonb NOT NULL DEFAULT '[]'::jsonb,
  currency      jsonb NOT NULL DEFAULT '{}'::jsonb,
  xp            integer NOT NULL DEFAULT 0,
  inspiration   boolean NOT NULL DEFAULT false,
  exhaustion    smallint NOT NULL DEFAULT 0 CHECK (exhaustion BETWEEN 0 AND 6),

  -- Mecánicas opcionales (solo si el perfil las activa).
  hunger        smallint,
  thirst        smallint,

  location_id   uuid REFERENCES locations(id),
  is_active     boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON characters (campaign_id, user_id);

-- El PJ vinculado a entidades del mundo. Misma propagación que los PNJ.
CREATE TABLE pc_bond_targets (
  pc_id         uuid NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  target_type   entity_type NOT NULL,
  target_id     uuid NOT NULL,
  PRIMARY KEY (pc_id, target_type, target_id)
);

CREATE INDEX ON pc_bond_targets (target_type, target_id);

-- APPEND-ONLY, y NUNCA reescribe la hoja. Registra cuándo las acciones
-- del jugador honran o contradicen lo que declaró.
-- Registrar es gratis; no registrar es irreversible. Si a mitad de una
-- campaña episódica el grupo se engancha y suben el slider, el historial
-- ya está y la evolución es visible retroactivamente.
CREATE TABLE pc_ibf_tension (
  id            bigserial PRIMARY KEY,
  pc_id         uuid NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  element       text NOT NULL CHECK (element IN ('ideal', 'bond', 'flaw')),
  alignment     smallint NOT NULL CHECK (alignment IN (-1, 1)),
  evidence      text NOT NULL,
  turn_id       bigint NOT NULL
);

CREATE INDEX ON pc_ibf_tension (pc_id, turn_id);

-- ============================================================================
-- 8. ITEMS Y RELACIONES
-- ============================================================================

CREATE TABLE items (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name          text NOT NULL,
  description   text,
  holder_type   entity_type,
  holder_id     uuid,
  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0
);

-- El grafo ES una tabla. Una campaña tiene cientos de entidades, no millones:
-- multi-hop exacto = CTE recursivo. No hace falta Neo4j ni Kuzu.
-- Aquí SÍ hay vigencia directa: una relación nace y muere en turnos concretos.
CREATE TABLE entity_relations (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  from_type     entity_type NOT NULL,
  from_id       uuid NOT NULL,
  rel_type      text NOT NULL,      -- member_of | owes | rules | kin | rival...
  to_type       entity_type NOT NULL,
  to_id         uuid NOT NULL,
  strength      smallint,
  valid_from_turn bigint NOT NULL DEFAULT 0,
  valid_to_turn   bigint,           -- NULL = vigente
  visibility    visibility_level NOT NULL DEFAULT 'party'
);

CREATE INDEX ON entity_relations (campaign_id, from_type, from_id) WHERE valid_to_turn IS NULL;
CREATE INDEX ON entity_relations (campaign_id, to_type, to_id)     WHERE valid_to_turn IS NULL;

-- ============================================================================
-- 9. LISTA BLANCA DE CAMPOS MUTABLES  +  LEDGER DE DELTAS
-- ============================================================================

-- El apalancamiento real NO está en el clasificador, está aquí.
-- Si un delta puede ser cualquier cosa sobre cualquier campo, ningún
-- clasificador es lo bastante bueno. Si solo puede tomar ~18 formas, el
-- modelo puede equivocarse sobre SI algo pasó, pero no puede inventar
-- QUÉ TIPO de cosa pasó. La alucinación queda acotada estructuralmente.
CREATE TABLE mutable_fields (
  entity_type   entity_type NOT NULL,
  field_name    text NOT NULL,
  value_kind    text NOT NULL CHECK (value_kind IN ('enum','numeric','uuid','bool','append')),
  min_value     numeric,
  max_value     numeric,
  max_delta_per_turn numeric,
  allowed_values text[],
  PRIMARY KEY (entity_type, field_name)
);

INSERT INTO mutable_fields (entity_type, field_name, value_kind, min_value, max_value, max_delta_per_turn, allowed_values) VALUES
  ('npc',      'status',            'enum',    NULL, NULL, NULL, ARRAY['alive','dead','missing','captured']),
  ('npc',      'location_id',       'uuid',    NULL, NULL, NULL, NULL),
  ('npc',      'affinity',          'numeric', -100, 100, 50,   NULL),
  ('npc',      'trust',             'numeric', -100, 100, 50,   NULL),
  ('npc',      'respect',           'numeric', -100, 100, 50,   NULL),
  ('npc',      'knowledge',         'append',  NULL, NULL, NULL, NULL),
  ('npc',      'secret_revealed',   'append',  NULL, NULL, NULL, NULL),
  ('location', 'state',             'enum',    NULL, NULL, NULL, ARRAY['intact','damaged','destroyed','occupied','abandoned']),
  ('location', 'detail',            'enum',    NULL, NULL, NULL, ARRAY['sketch','observed','full']),
  ('location', 'controlling_faction_id','uuid', NULL, NULL, NULL, NULL),
  ('faction',  'stance_party',      'numeric', -100, 100, 50,   NULL),
  ('faction',  'knows_about_party', 'bool',    NULL, NULL, NULL, NULL),
  ('faction',  'clock_progress',    'numeric', 0,    9999, NULL, NULL),
  ('quest',    'status',            'enum',    NULL, NULL, NULL, ARRAY['unknown','active','completed','failed','abandoned']),
  ('quest',    'next_step_known',   'bool',    NULL, NULL, NULL, NULL),
  ('character','hp_current',        'numeric', -99,  999,  NULL, NULL),
  ('character','conditions',        'append',  NULL, NULL, NULL, NULL),
  ('character','inventory',         'append',  NULL, NULL, NULL, NULL),
  ('world',    'game_day',          'numeric', 0,    999999, NULL, NULL);

-- El ledger. Fuente del recap: los hechos se DERIVAN del diff, no se generan.
-- Un recap malo envenena la campaña permanentemente; derivar de deltas
-- elimina el compounding porque los deltas no acumulan error.
CREATE TABLE state_deltas (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id    uuid REFERENCES sessions(id),
  turn_id       bigint NOT NULL,

  entity_type   entity_type NOT NULL,
  entity_id     uuid,                    -- NULL solo para entity_type='world'
  field_name    text NOT NULL,
  old_value     jsonb,
  new_value     jsonb NOT NULL,

  source        delta_source NOT NULL,
  -- El campo que hace TODO el trabajo antialucinación: span LITERAL del turno.
  -- Se valida en código antes de escribir. Un modelo que debe citar el texto
  -- que justifica el cambio no puede inventar el cambio.
  evidence      text,
  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at    timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT extracted_requires_evidence
    CHECK (source <> 'extracted' OR evidence IS NOT NULL)
);

CREATE INDEX ON state_deltas (campaign_id, turn_id);
CREATE INDEX ON state_deltas (campaign_id, entity_type, entity_id, turn_id DESC);
CREATE INDEX ON state_deltas (session_id);

-- Los rechazados se GUARDAN. Es la instrumentación que separa
-- "sé que funciona" de "asumo que funciona": si la tasa de rechazo sube,
-- el prompt derivó. El no-op silencioso es el fallo que muerde.
CREATE TABLE rejected_deltas (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id       bigint NOT NULL,
  payload       jsonb NOT NULL,
  reason        text NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- ============================================================================
-- 9b. TABLA DE MAGNITUDES
-- El extractor clasifica el TIPO de evento (enum cerrado). Nunca elige números.
-- Los números salen de aquí, modulados por el eje de personalidad del PNJ.
-- Un mismo evento produce deltas distintos, e incluso de signo opuesto,
-- según a quién le ocurra.
-- ============================================================================

CREATE TYPE event_kind AS ENUM (
  'bribe_offered', 'promise_kept', 'promise_broken', 'courtesy',
  'bond_target_protected', 'bond_target_harmed', 'life_saved',
  'betrayal_proven', 'threat_made', 'competence_shown',
  'ideal_honored', 'ideal_violated', 'public_status_given', 'secret_entrusted'
);

CREATE TABLE event_magnitudes (
  event         event_kind NOT NULL,
  -- Qué eje de personalidad decide la reacción.
  modulator     text NOT NULL CHECK (modulator IN ('principle','warmth','candor','boldness','none')),
  -- Banda del modulador: high > 50, mid -50..50, low < -50.
  band          text NOT NULL CHECK (band IN ('high','mid','low','any')),
  d_affinity    numeric(5,1) NOT NULL DEFAULT 0,
  d_trust       numeric(5,1) NOT NULL DEFAULT 0,
  d_respect     numeric(5,1) NOT NULL DEFAULT 0,
  -- Qué ocurre narrativamente. El Actor lo lee; no lo improvisa.
  outcome       text NOT NULL,
  PRIMARY KEY (event, band)
);

INSERT INTO event_magnitudes (event, modulator, band, d_affinity, d_trust, d_respect, outcome) VALUES
  -- SOBORNO. El caso que mejor muestra la inversión de signo.
  ('bribe_offered','principle','high',  -15, -20, -25, 'La oferta ES la ofensa. Se ofende aunque el grupo sea aliado: le acaban de decir quién creen que es. Rechaza sin negociar y lo recuerda.'),
  ('bribe_offered','principle','mid',    -4,  -6,  -2, 'Incómodo. Rechaza pero no lo convierte en un asunto personal. Cambia de tema.'),
  ('bribe_offered','principle','low',    +2,   0,  +5, 'NO se ofende. Si rechaza es por insuficiente, no por indigno. Contraoferta o insinúa el precio correcto.'),

  ('promise_kept','principle','high',    +8, +15, +12, 'Lo registra como prueba de carácter, no como favor.'),
  ('promise_kept','principle','mid',     +6,  +8,  +5, 'Agradece y lo tiene en cuenta.'),
  ('promise_kept','principle','low',     +1,  +2,  +8, 'Registra la capacidad de cumplir, no la virtud de haber cumplido.'),

  ('promise_broken','principle','high',  -6, -18, -10, 'La palabra rota pesa más que el daño causado. Lo dice a la cara.'),
  ('promise_broken','principle','mid',   -5,  -8,  -4, 'Molesto. Da margen si hay explicación.'),
  ('promise_broken','principle','low',   -2,  -3,  -6, 'Lo esperaba. Baja el respeto por ineptos, no por indignos.'),

  ('courtesy','warmth','high',           +3,  +1,   0, 'Responde con calidez.'),
  ('courtesy','warmth','mid',            +1,   0,   0, 'Lo nota, no lo comenta.'),
  ('courtesy','warmth','low',             0,   0,   0, 'Indiferente. La cortesía no le mueve nada.'),

  ('bond_target_protected','none','any',+25, +15, +12, 'Tocaron lo que protegería por encima de todo, en la buena dirección.'),
  ('bond_target_harmed','none','any',   -45, -30,  -5, 'Tocaron su vínculo. Es lo más grave que le pueden hacer sin matarlo.'),
  ('life_saved','none','any',           +30, +25, +15, 'Deuda de sangre. No se olvida.'),
  ('betrayal_proven','none','any',      -40, -70, -20, 'Traición demostrada. En PNJ de principios, además FIJA el techo de confianza.'),

  ('threat_made','boldness','high',      -8,  -5, +10, 'No se amilana. Sube el respeto por atreverse, baja el aprecio.'),
  ('threat_made','boldness','mid',      -10,  -8,   0, 'Cede en el momento, lo guarda.'),
  ('threat_made','boldness','low',      -12, -10, +15, 'Cede y teme. El miedo se lee como respeto y contamina la relación.'),

  ('competence_shown','none','any',       +2,  +3, +12, 'Reevalúa lo que el grupo puede hacer.'),
  ('ideal_honored','none','any',          +5,  +5, +12, 'Actuaron según lo que él considera correcto.'),
  ('ideal_violated','none','any',         -8,  -6, -15, 'Actuaron contra lo que él considera correcto.'),
  ('public_status_given','none','any',    +6,  +2,  +4, 'Le dieron en público el trato que cree merecer. Explota el defecto de estatus.'),
  ('secret_entrusted','none','any',       +5, +20,  +3, 'Confiarle algo que expone a quien lo cuenta es en sí un acto de confianza.');

-- ---------------------------------------------------------------------------
-- resolve_event: dado un PNJ y un tipo de evento, devuelve los tres deltas
-- ya modulados por SU personalidad, más lo que debe ocurrir narrativamente.
-- El modelo clasifica el evento; los números salen de aquí.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION resolve_event(p_npc_id uuid, p_event event_kind)
RETURNS TABLE (d_affinity numeric, d_trust numeric, d_respect numeric,
               band text, outcome text)
LANGUAGE plpgsql STABLE AS $$
DECLARE v_mod text; v_val numeric; v_band text;
BEGIN
  SELECT DISTINCT modulator INTO v_mod FROM event_magnitudes WHERE event = p_event;

  IF v_mod = 'none' THEN
    v_band := 'any';
  ELSE
    EXECUTE format('SELECT %I FROM npcs WHERE id = $1', v_mod)
      INTO v_val USING p_npc_id;
    v_band := CASE WHEN v_val >  50 THEN 'high'
                   WHEN v_val < -50 THEN 'low'
                   ELSE 'mid' END;
  END IF;

  RETURN QUERY
    SELECT m.d_affinity, m.d_trust, m.d_respect, m.band, m.outcome
      FROM event_magnitudes m
     WHERE m.event = p_event AND m.band = v_band;
END;
$$;


-- ============================================================================
-- 10. RECAPS DE SESIÓN
-- ============================================================================

-- Dos campos SEPARADOS: facts es autoritativo y derivado del ledger;
-- narrative_summary es prosa ADVISORIA. Si se contradicen, ganan los hechos.
-- El recap es un caché RECOMPUTABLE: el turn_log crudo queda íntegro,
-- así que un recap malo se arregla. Un resumen que reemplazó a su fuente, no.
CREATE TABLE session_recaps (
  session_id    uuid PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  facts         jsonb NOT NULL DEFAULT '[]'::jsonb,   -- derivado de state_deltas
  narrative_summary text,                             -- prosa, advisorio
  open_threads  jsonb NOT NULL DEFAULT '[]'::jsonb,
  generated_at  timestamptz NOT NULL DEFAULT now(),
  regenerated_count integer NOT NULL DEFAULT 0
);

-- ============================================================================
-- 11. INGESTA DE LORE (pgvector)
-- ============================================================================

-- Ingesta inicial opcional: el usuario sube su propio lore en .md.
-- Los wiki-links [[Casa Vorren]] son aristas EXPLÍCITAS que no requieren
-- inferencia: el grafo viene medio construido con la topología que él quiso.
CREATE TABLE lore_documents (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  filename      text NOT NULL,
  raw_content   text NOT NULL,
  ingested_at   timestamptz NOT NULL DEFAULT now()
);

-- Prosa de referencia: atmósfera, historia. Responde "¿cómo se siente
-- estar aquí?". Distinto de las entidades canónicas, que responden
-- "¿quién gobierna?" y son consultables exactamente.
CREATE TABLE lore_chunks (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  document_id   uuid REFERENCES lore_documents(id) ON DELETE CASCADE,
  heading_path  text,
  content       text NOT NULL,
  -- bge-m3 local, versión FIJA. Si un proveedor actualizara el modelo
  -- entre las campañas de G2 y G1, el espacio vectorial cambiaría a mitad
  -- de experimento. Un archivo en disco no cambia nunca.
  embedding     vector(1024),
  embedding_model text NOT NULL DEFAULT 'bge-m3'
);

CREATE INDEX ON lore_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON lore_chunks (campaign_id);

-- Narrativa pasada indexada. ÚNICO lugar donde la recuperación aproximada
-- es correcta: "¿ha pasado algo parecido antes?" no tiene respuesta exacta.
-- El estado de entidades NO va aquí: eso es un SELECT.
CREATE TABLE narrative_chunks (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id       bigint NOT NULL,
  session_id    uuid REFERENCES sessions(id),
  content       text NOT NULL,
  embedding     vector(1024),
  visibility    visibility_level NOT NULL DEFAULT 'party'
);

CREATE INDEX ON narrative_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON narrative_chunks (campaign_id, turn_id);

-- Corpus estático de reglas: SRD, mecánicas opcionales, homebrew.
-- No cambia, así que no tiene problema temporal. Sin campaign_id cuando
-- es SRD compartido.
CREATE TABLE rules_chunks (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid REFERENCES campaigns(id) ON DELETE CASCADE,
  source        text NOT NULL,       -- 'srd' | 'homebrew' | 'optional'
  heading_path  text,
  content       text NOT NULL,
  embedding     vector(1024)
);

CREATE INDEX ON rules_chunks USING hnsw (embedding vector_cosine_ops);

-- ============================================================================
-- 12. FUNCIONES
-- ============================================================================

-- Bandas conductuales. El modelo NUNCA ve el número: recibe CONDUCTA.
-- Siete bandas por eje. Un float de dos decimales no produce comportamiento
-- distinguible; una banda con guía conductual sí.
CREATE OR REPLACE FUNCTION disposition_band(raw numeric)
RETURNS text LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE
    WHEN raw <= -60 THEN 'hostile'
    WHEN raw <= -25 THEN 'wary'
    WHEN raw <=  -8 THEN 'cold'
    WHEN raw <   8  THEN 'neutral'
    WHEN raw <   25 THEN 'cordial'
    WHEN raw <   60 THEN 'loyal'
    ELSE                 'devoted'
  END;
$$;

-- ---------------------------------------------------------------------------
-- apply_delta: LA única puerta de escritura narrativa.
-- Es el caso de libro para procedimiento almacenado: validar contra lista
-- blanca, actualizar entidad y registrar en el ledger deben ser ATÓMICOS.
-- Hecho desde el orquestador en tres llamadas, un fallo deja estado corrupto.
-- Y como el orquestador es remoto, además ahorra round-trips.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION apply_delta(
  p_campaign_id  uuid,
  p_entity_type  entity_type,
  p_entity_id    uuid,
  p_field        text,
  p_value        jsonb,
  p_turn_id      bigint,
  p_source       delta_source,
  p_evidence     text DEFAULT NULL,
  p_visibility   visibility_level DEFAULT 'party',
  p_session_id   uuid DEFAULT NULL
) RETURNS bigint
LANGUAGE plpgsql AS $$
DECLARE
  v_tenant   uuid;
  v_spec     mutable_fields;
  v_old      jsonb;
  v_num      numeric;
  v_delta_id bigint;
  v_table    text;
BEGIN
  SELECT tenant_id INTO v_tenant FROM campaigns WHERE id = p_campaign_id;
  IF v_tenant IS NULL THEN
    RAISE EXCEPTION 'campaign % not found', p_campaign_id;
  END IF;

  -- 1. Lista blanca. Un campo fuera de ella no existe para el sistema.
  SELECT * INTO v_spec FROM mutable_fields
   WHERE entity_type = p_entity_type AND field_name = p_field;
  IF v_spec IS NULL THEN
    RAISE EXCEPTION 'field %.% is not delta-able', p_entity_type, p_field;
  END IF;

  -- 2. Evidencia obligatoria para lo extraído.
  IF p_source = 'extracted' AND (p_evidence IS NULL OR length(trim(p_evidence)) = 0) THEN
    RAISE EXCEPTION 'extracted delta requires evidence span';
  END IF;

  -- 3. Validación de dominio.
  IF v_spec.value_kind = 'enum' THEN
    IF NOT (p_value #>> '{}' = ANY (v_spec.allowed_values)) THEN
      RAISE EXCEPTION 'value % not allowed for %.%', p_value, p_entity_type, p_field;
    END IF;
  ELSIF v_spec.value_kind = 'numeric' THEN
    v_num := (p_value #>> '{}')::numeric;
    IF v_spec.min_value IS NOT NULL AND v_num < v_spec.min_value THEN
      RAISE EXCEPTION 'value % below minimum % for %.%', v_num, v_spec.min_value, p_entity_type, p_field;
    END IF;
    IF v_spec.max_value IS NOT NULL AND v_num > v_spec.max_value THEN
      RAISE EXCEPTION 'value % above maximum % for %.%', v_num, v_spec.max_value, p_entity_type, p_field;
    END IF;
  END IF;

  -- 4. Aplicar sobre la entidad. Los campos 'append' no se actualizan aquí:
  --    van a sus tablas append-only (npc_knowledge, etc.).
  IF v_spec.value_kind <> 'append' THEN
    IF p_entity_type = 'npc' AND p_field IN ('affinity','trust','respect') THEN
      -- Disposición vive en su propia tabla, con topes por personalidad.
      INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, updated_at_turn)
        VALUES (p_entity_id, v_tenant, NULL, p_turn_id)
        ON CONFLICT DO NOTHING;

      EXECUTE format(
        'SELECT to_jsonb(%I) FROM npc_disposition WHERE npc_id = $1 AND pc_id IS NULL',
        p_field
      ) INTO v_old USING p_entity_id;

      -- Los topes por personalidad se APLICAN aquí, no solo se almacenan.
      -- Walder Frey es estructuralmente incapaz de confiar: su techo de +20
      -- no es una etapa que se supere, es un límite de carácter.
      IF p_field = 'trust' THEN
        SELECT LEAST(GREATEST(v_num, trust_floor), trust_ceiling)
          INTO v_num
          FROM npc_disposition
         WHERE npc_id = p_entity_id AND pc_id IS NULL;
      END IF;

      EXECUTE format(
        'UPDATE npc_disposition SET %I = LEAST(GREATEST($1, -100), 100), updated_at_turn = $2
          WHERE npc_id = $3 AND pc_id IS NULL', p_field
      ) USING v_num, p_turn_id, p_entity_id;

    ELSIF p_entity_type = 'world' THEN
      SELECT to_jsonb(game_day) INTO v_old FROM campaigns WHERE id = p_campaign_id;
      UPDATE campaigns SET game_day = v_num::integer WHERE id = p_campaign_id;

    ELSE
      v_table := CASE p_entity_type
        WHEN 'npc' THEN 'npcs' WHEN 'location' THEN 'locations'
        WHEN 'faction' THEN 'factions' WHEN 'quest' THEN 'quests'
        WHEN 'character' THEN 'characters' WHEN 'item' THEN 'items' END;

      EXECUTE format('SELECT to_jsonb(%I) FROM %I WHERE id = $1', p_field, v_table)
        INTO v_old USING p_entity_id;

      IF v_spec.value_kind = 'uuid' THEN
        EXECUTE format('UPDATE %I SET %I = ($1 #>> ''{}'')::uuid WHERE id = $2', v_table, p_field)
          USING p_value, p_entity_id;
      ELSIF v_spec.value_kind = 'bool' THEN
        EXECUTE format('UPDATE %I SET %I = ($1 #>> ''{}'')::boolean WHERE id = $2', v_table, p_field)
          USING p_value, p_entity_id;
      ELSIF v_spec.value_kind = 'numeric' THEN
        EXECUTE format('UPDATE %I SET %I = $1 WHERE id = $2', v_table, p_field)
          USING v_num, p_entity_id;
      ELSE
        EXECUTE format('UPDATE %I SET %I = ($1 #>> ''{}'')::%s WHERE id = $2',
                       v_table, p_field,
                       CASE WHEN p_entity_type = 'npc' THEN 'npc_status'
                            WHEN p_entity_type = 'location' AND p_field = 'state' THEN 'location_state'
                            WHEN p_entity_type = 'location' AND p_field = 'detail' THEN 'detail_level'
                            WHEN p_entity_type = 'quest' THEN 'quest_status'
                            ELSE 'text' END)
          USING p_value, p_entity_id;
      END IF;
    END IF;
  END IF;

  -- 5. Ledger. En la MISMA transacción.
  INSERT INTO state_deltas (
    tenant_id, campaign_id, session_id, turn_id, entity_type, entity_id,
    field_name, old_value, new_value, source, evidence, visibility
  ) VALUES (
    v_tenant, p_campaign_id, p_session_id, p_turn_id, p_entity_type, p_entity_id,
    p_field, v_old, p_value, p_source, p_evidence, p_visibility
  ) RETURNING id INTO v_delta_id;

  RETURN v_delta_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- advance_clocks: las repercusiones como GARANTÍA, no como memoria del modelo.
-- Avanza contadores con el TIEMPO DE JUEGO (no con turnos), evalúa umbrales
-- y devuelve los eventos disparados. El modelo solo narra un hecho que ya
-- es verdad en la base.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION advance_clocks(
  p_campaign_id uuid,
  p_game_days   numeric,
  p_turn_id     bigint
) RETURNS TABLE (clock_id uuid, faction_id uuid, agenda text, event jsonb)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE faction_clocks c
     SET progress = c.progress + (p_game_days * c.rate_per_game_day)
   WHERE c.campaign_id = p_campaign_id
     AND NOT c.paused
     AND c.fired_at_turn IS NULL;

  UPDATE faction_clocks c
     SET fired_at_turn = p_turn_id
   WHERE c.campaign_id = p_campaign_id
     AND c.fired_at_turn IS NULL
     AND NOT c.paused
     AND c.progress >= c.threshold;

  RETURN QUERY
    SELECT c.id, c.faction_id, c.agenda, c.on_fire_event
      FROM faction_clocks c
     WHERE c.campaign_id = p_campaign_id
       AND c.fired_at_turn = p_turn_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- decay_dispositions: decaimiento PROPORCIONAL al cerrar sesión.
-- Se MATERIALIZA al escribir, no se calcula al leer: así mover el slider
-- no reescribe retroactivamente la historia. El pasado queda congelado.
-- Proporcional resuelve trivial-vs-grave sin clasificar sesiones:
-- un +3 de cortesía se disuelve; un -40 de traición sigue pesando.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION decay_dispositions(p_campaign_id uuid, p_turn_id bigint)
RETURNS integer LANGUAGE plpgsql AS $$
DECLARE v_pct numeric; v_count integer;
BEGIN
  SELECT disposition_decay_pct INTO v_pct FROM campaigns WHERE id = p_campaign_id;

  WITH updated AS (
    UPDATE npc_disposition d
       SET affinity = d.affinity * (1 - (v_pct/100) * n.decay_multiplier),
           trust    = d.trust    * (1 - (v_pct/100) * n.decay_multiplier),
           respect  = d.respect  * (1 - (v_pct/100) * n.decay_multiplier),
           updated_at_turn = p_turn_id
      FROM npcs n
     WHERE d.npc_id = n.id AND n.campaign_id = p_campaign_id
    RETURNING 1
  ) SELECT count(*) INTO v_count FROM updated;

  RETURN v_count;
END;
$$;

-- ---------------------------------------------------------------------------
-- get_visible_state: filtrado por visibilidad en UNA consulta.
-- El jugador ve lo que su grupo descubrió; el DM ve todo.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_visible_state(
  p_campaign_id uuid,
  p_viewer_id   uuid,
  p_entity_type entity_type DEFAULT NULL
) RETURNS TABLE (entity_type entity_type, entity_id uuid, name text, payload jsonb)
LANGUAGE plpgsql AS $$
DECLARE v_is_dm boolean;
BEGIN
  SELECT COALESCE(is_dm, false) INTO v_is_dm
    FROM campaign_members
   WHERE campaign_id = p_campaign_id AND user_id = p_viewer_id;

  RETURN QUERY
    SELECT 'npc'::entity_type, n.id, n.name,
           jsonb_build_object(
             'status', n.status, 'location_id', n.location_id,
             'affinity_band', disposition_band(COALESCE(d.affinity, 0)),
             'trust_band',    disposition_band(COALESCE(d.trust, 0)),
             'respect_band',  disposition_band(COALESCE(d.respect, 0))
           )
      FROM npcs n
      LEFT JOIN npc_disposition d ON d.npc_id = n.id AND d.pc_id IS NULL
     WHERE n.campaign_id = p_campaign_id
       AND (p_entity_type IS NULL OR p_entity_type = 'npc')
       AND (v_is_dm OR n.visibility <> 'dm_only')
  UNION ALL
    SELECT 'location'::entity_type, l.id, l.name,
           jsonb_build_object('kind', l.kind, 'state', l.state, 'detail', l.detail,
                              'description', COALESCE(l.description_canonical, l.sketch_text))
      FROM locations l
     WHERE l.campaign_id = p_campaign_id
       AND (p_entity_type IS NULL OR p_entity_type = 'location')
       AND (v_is_dm OR l.visibility <> 'dm_only')
  UNION ALL
    SELECT 'quest'::entity_type, q.id, q.title,
           jsonb_build_object('status', q.status, 'next_step_known', q.next_step_known)
      FROM quests q
     WHERE q.campaign_id = p_campaign_id
       AND (p_entity_type IS NULL OR p_entity_type = 'quest')
       AND (v_is_dm OR q.visibility <> 'dm_only');
END;
$$;

-- ---------------------------------------------------------------------------
-- location_context: la cadena de ancestros con herencia de cultura.
-- Hace que "coherente con la cultura local" sea un SELECT y no una
-- instrucción que el modelo puede olvidar.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION location_context(p_location_id uuid)
RETURNS jsonb LANGUAGE sql STABLE AS $$
  WITH RECURSIVE chain AS (
    SELECT id, parent_id, name, kind, culture_overrides, 0 AS depth
      FROM locations WHERE id = p_location_id
    UNION ALL
    SELECT l.id, l.parent_id, l.name, l.kind, l.culture_overrides, c.depth + 1
      FROM locations l JOIN chain c ON l.id = c.parent_id
  )
  SELECT jsonb_build_object(
    'path', (SELECT jsonb_agg(jsonb_build_object('name', name, 'kind', kind) ORDER BY depth DESC) FROM chain),
    -- El nivel más específico gana: se acumula desde la raíz hacia la hoja.
    'culture', (SELECT COALESCE(jsonb_object_agg(k, v), '{}'::jsonb)
                  FROM (SELECT DISTINCT ON (k) k, v
                          FROM chain, jsonb_each(culture_overrides) AS e(k, v)
                         ORDER BY k, depth ASC) s)
  );
$$;

-- ---------------------------------------------------------------------------
-- stagnation_check: capas 1-3, todas SQL, todas gratis.
-- El grupo que monta un puesto en el mercado NO está estancado: está
-- generando estado. Solo si las tres capas apuntan a estancamiento se paga
-- una llamada al modelo. La pregunta repetida como gag muere en la capa 2.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION stagnation_check(p_campaign_id uuid, p_window integer DEFAULT 15)
RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT jsonb_build_object(
    'has_known_next_step', EXISTS (
      SELECT 1 FROM quests
       WHERE campaign_id = p_campaign_id AND status = 'active' AND next_step_known),
    'new_state_generated', (
      SELECT count(*) FROM state_deltas
       WHERE campaign_id = p_campaign_id
         AND turn_id > (SELECT current_turn - p_window FROM campaigns WHERE id = p_campaign_id)),
    'entities_created', (
      SELECT count(*) FROM npcs
       WHERE campaign_id = p_campaign_id
         AND created_at_turn > (SELECT current_turn - p_window FROM campaigns WHERE id = p_campaign_id))
  );
$$;

-- ============================================================================
-- 12b. PROPAGACIÓN — cierra el fallo de `knows_about_party`
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


-- ============================================================================
-- 13. ROW LEVEL SECURITY
-- ============================================================================
-- Declarativo. Ningún endpoint puede "olvidarlo", que es exactamente el
-- riesgo de implementar visibilidad en lógica de aplicación.
-- El orquestador fija app.tenant_id por transacción.

CREATE OR REPLACE FUNCTION current_tenant() RETURNS uuid
LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid;
$$;

DO $$
DECLARE t text;
BEGIN
  FOR t IN SELECT unnest(ARRAY[
    'users','campaigns','sessions','turn_log','turn_jobs','model_calls',
    'locations','factions','faction_clocks','quests','session_seeds',
    'npcs','npc_ibf','npc_bond_targets','npc_disposition','npc_knowledge',
    'npc_secrets','characters','pc_bond_targets','pc_ibf_tension','items',
    'entity_relations','state_deltas','rejected_deltas','session_recaps',
    'lore_documents','lore_chunks','narrative_chunks'
  ]) LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format(
      'CREATE POLICY tenant_isolation ON %I USING (tenant_id = current_tenant())', t);
  END LOOP;
END $$;

-- rules_chunks: tenant_id NULLable (SRD compartido entre tenants).
ALTER TABLE rules_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON rules_chunks
  USING (tenant_id IS NULL OR tenant_id = current_tenant());

-- campaign_members no tiene tenant_id propio (es tabla puente), así que la
-- política va por subconsulta. Sin esto la tabla queda LEGIBLE entre tenants,
-- y get_visible_state la usa para decidir quién es DM.
ALTER TABLE campaign_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON campaign_members USING (
  EXISTS (SELECT 1 FROM campaigns c
           WHERE c.id = campaign_members.campaign_id
             AND c.tenant_id = current_tenant()));

-- mutable_fields es catálogo de referencia compartido: sin RLS a propósito.
-- tenants no puede llevar RLS (no tiene tenant_id); se protege por GRANT.-- ============================================================================
-- QuestMasters / DM-IA  —  Esquema canónico
-- PostgreSQL 16 + pgvector
--
-- Principios de diseño:
--   1. Multi-tenant desde el día uno: tenant_id en toda tabla, RLS activo.
--   2. Estado actual en la tabla de entidad; historia en el ledger de deltas.
--      La reconstrucción a un turno pasado se hace revirtiendo deltas.
--   3. Toda escritura narrativa pasa por apply_delta(). Si no pasó por ahí,
--      no ocurrió.
--   4. Lista blanca de campos mutables como DATO (tabla), no como código.
--   5. La creación de entidades NO es un delta: es operación explícita.
--   6. turn_log es append-only y es la fuente de verdad reproducible.
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- 1. TIPOS
-- ============================================================================

-- Visibilidad por fila/campo. La asimetría de información es estructural:
-- lo que el DM sabe no es lo que el grupo sabe.
CREATE TYPE visibility_level AS ENUM ('dm_only', 'party', 'player');

-- Perfil de campaña: gobierna sensibilidad, decay y densidad de rastreo.
CREATE TYPE campaign_profile AS ENUM ('chronicle', 'adventure', 'episodic');

-- Tono del mundo y registro del grupo son EJES INDEPENDIENTES.
-- Un payaso en un mundo grimdark es configuración válida, no error.
CREATE TYPE world_tone     AS ENUM ('grimdark', 'heroic', 'light', 'mixed');
CREATE TYPE party_register  AS ENUM ('serious', 'mixed', 'comedic');

-- Nivel de detalle de un lugar. 'sketch' no persiste entidades hijas;
-- colapsa a 'observed' cuando el grupo pregunta.
CREATE TYPE detail_level AS ENUM ('sketch', 'observed', 'full');

-- Los tipos que exigen pre-generación completa (topología acoplada) vs.
-- los que admiten boceto.
CREATE TYPE location_kind AS ENUM (
  'region', 'realm', 'settlement', 'district', 'building',
  'dungeon', 'ruin', 'crypt', 'wilderness', 'landmark'
);

CREATE TYPE npc_status     AS ENUM ('alive', 'dead', 'missing', 'captured');
CREATE TYPE location_state AS ENUM ('intact', 'damaged', 'destroyed', 'occupied', 'abandoned');
CREATE TYPE quest_status   AS ENUM ('unknown', 'active', 'completed', 'failed', 'abandoned');

CREATE TYPE entity_type AS ENUM ('npc', 'location', 'faction', 'quest', 'character', 'item', 'world');

CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed');
CREATE TYPE job_kind   AS ENUM ('turn', 'session_close', 'lore_ingest', 'backfill');

-- Origen de un delta. Gobierna la política de escritura:
-- 'mechanical' escribe inmediato sin modelo; 'extracted' requiere evidencia.
CREATE TYPE delta_source AS ENUM ('mechanical', 'extracted', 'authored', 'clock');

-- Arquitectura que produjo un turno. Para la comparación experimental
-- y para el análisis de economía por turno.
CREATE TYPE architecture AS ENUM ('monolithic', 'mas');

CREATE TYPE agent_role AS ENUM (
  'monolithic', 'router', 'narrator', 'arbiter', 'npc_actor', 'world', 'extractor'
);

-- ============================================================================
-- 2. TENANCÍA
-- ============================================================================

CREATE TABLE tenants (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email       text NOT NULL,
  display_name text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, email)
);

-- ============================================================================
-- 3. CAMPAÑA Y CONFIGURACIÓN
-- ============================================================================

CREATE TABLE campaigns (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  owner_id        uuid NOT NULL REFERENCES users(id),
  title           text NOT NULL,

  -- Variable independiente del experimento. Fija por campaña.
  architecture    architecture NOT NULL,

  -- Perfil: gobierna decay, densidad de rastreo, mecánicas opcionales.
  profile         campaign_profile NOT NULL DEFAULT 'adventure',

  -- Tono: dos ejes independientes + si el contraste es rasgo o problema.
  world_tone      world_tone     NOT NULL DEFAULT 'heroic',
  party_register  party_register NOT NULL DEFAULT 'mixed',
  tone_contrast_allowed boolean  NOT NULL DEFAULT true,

  -- 0 = cuentacuentos (reglas invisibles), 100 = manual estricto (todo expuesto).
  -- El Árbitro calcula igual en todos los niveles; cambia la VISIBILIDAD.
  rules_visibility  smallint NOT NULL DEFAULT 50
                    CHECK (rules_visibility BETWEEN 0 AND 100),

  -- Sensibilidad de disposición y decaimiento PROPORCIONAL por sesión.
  -- Proporcional, no fijo: un +3 de cortesía se disuelve, un -40 de traición no.
  disposition_sensitivity numeric(4,2) NOT NULL DEFAULT 1.00
                          CHECK (disposition_sensitivity BETWEEN 0 AND 2),
  disposition_decay_pct   numeric(4,2) NOT NULL DEFAULT 3.00
                          CHECK (disposition_decay_pct BETWEEN 0 AND 50),

  -- Mecánicas opcionales activas (hambre, sed, heridas, descanso extendido).
  optional_mechanics jsonb NOT NULL DEFAULT '{}'::jsonb,

  -- RESTRICCIÓN, no preferencia. Se aplica en la salida, no en el prompt.
  -- Sobrescribe tono, perfil y cualquier semilla. Editable en cualquier momento.
  content_boundaries jsonb NOT NULL DEFAULT
    '{"hard_lines": [], "veils": []}'::jsonb,

  -- Reloj de mundo. Independiente de turn_id y session_id.
  game_day        integer NOT NULL DEFAULT 0,
  current_turn    bigint  NOT NULL DEFAULT 0,

  created_at      timestamptz NOT NULL DEFAULT now(),
  archived_at     timestamptz
);

CREATE INDEX ON campaigns (tenant_id, owner_id);

CREATE TABLE campaign_members (
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  is_dm       boolean NOT NULL DEFAULT false,
  PRIMARY KEY (campaign_id, user_id)
);

CREATE TABLE sessions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  ordinal     integer NOT NULL,
  start_turn  bigint  NOT NULL,
  end_turn    bigint,
  game_day_start integer NOT NULL DEFAULT 0,
  game_day_end   integer,
  opened_at   timestamptz NOT NULL DEFAULT now(),
  closed_at   timestamptz,
  UNIQUE (campaign_id, ordinal)
);

-- ============================================================================
-- 4. LOG DE TURNOS Y COLA DE TRABAJOS
-- ============================================================================

-- Append-only. Nunca se actualiza ni se borra. Es lo que permite reprocesar
-- con un prompt mejor sin haber perdido nada (red de seguridad del recall).
CREATE TABLE turn_log (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id    uuid REFERENCES sessions(id),
  turn_id       bigint NOT NULL,

  -- El buffer: los jugadores escriben varias veces antes de cerrar la
  -- interacción. El rol entre jugadores cuesta CERO llamadas al modelo.
  player_buffer jsonb NOT NULL,           -- [{user_id, pc_id, text, at}]
  dm_output     text,

  scene_tone    text,                     -- volátil, por escena
  location_id   uuid,

  gate_passed   boolean,                  -- ¿pasó la compuerta determinista?
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, turn_id)
);

CREATE INDEX ON turn_log (campaign_id, turn_id DESC);
CREATE INDEX ON turn_log (session_id);

-- Cola en tabla. FOR UPDATE SKIP LOCKED. Sin Redis, sin SQS.
-- Existe desde el día uno porque el navegador SE VA A DESCONECTAR durante
-- un turno de 60-90s, y el turno debe completarse igual.
CREATE TABLE turn_jobs (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  kind        job_kind   NOT NULL,
  status      job_status NOT NULL DEFAULT 'pending',
  priority    smallint   NOT NULL DEFAULT 100,  -- lore_ingest: baja prioridad
  payload     jsonb      NOT NULL DEFAULT '{}'::jsonb,
  attempts    smallint   NOT NULL DEFAULT 0,
  last_error  text,
  locked_at   timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz
);

CREATE INDEX ON turn_jobs (status, priority, created_at) WHERE status = 'pending';

-- Auditoría de validez experimental + economía por arquitectura.
-- Dato barato de recolectar ahora, imposible de reconstruir después.
CREATE TABLE model_calls (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id       bigint,
  role          agent_role NOT NULL,
  provider      text NOT NULL,            -- 'deepinfra' — UN proveedor, fijo
  model_id      text NOT NULL,
  quantization  text,                     -- registrado: variación invalida
  input_tokens  integer NOT NULL,
  output_tokens integer NOT NULL,
  latency_ms    integer,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON model_calls (campaign_id, turn_id);

-- ============================================================================
-- 5. MUNDO: LUGARES (JERÁRQUICOS), FACCIONES, MISIONES
-- ============================================================================

-- Herencia jerárquica: región → reino → asentamiento → distrito → edificio.
-- Cada nivel declara solo lo que DIFIERE de su padre. "Coherente con la
-- cultura local" pasa a ser un SELECT sobre la cadena de ancestros, no una
-- instrucción al modelo que puede olvidar.
CREATE TABLE locations (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  parent_id     uuid REFERENCES locations(id) ON DELETE CASCADE,
  kind          location_kind NOT NULL,
  name          text NOT NULL,

  -- Boceto vs. observado. Al colapsar, description_canonical se CONGELA:
  -- si vuelven, reciben la misma descripción desde el registro.
  -- Y si el estado del mundo cambió, el diff ES contenido narrativo.
  detail         detail_level NOT NULL DEFAULT 'sketch',
  sketch_text    text,
  description_canonical text,
  observed_at_turn bigint,

  state          location_state NOT NULL DEFAULT 'intact',
  controlling_faction_id uuid,

  -- Solo lo que difiere del padre. NULL = hereda.
  culture_overrides jsonb NOT NULL DEFAULT '{}'::jsonb,
  -- {language, currency, notable_laws, attitude_to_outsiders, tensions}

  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON locations (campaign_id, parent_id);
CREATE INDEX ON locations (campaign_id, kind);

CREATE TABLE factions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name          text NOT NULL,
  description   text,
  seat_location_id uuid REFERENCES locations(id),

  -- Disposición de facción hacia el grupo (acumulador continuo).
  stance_party  numeric(6,2) NOT NULL DEFAULT 0
                CHECK (stance_party BETWEEN -100 AND 100),
  knows_about_party boolean NOT NULL DEFAULT false,

  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0
);

CREATE INDEX ON factions (campaign_id);

-- Los relojes convierten las repercusiones de propiedad emergente FRÁGIL
-- en GARANTÍA del sistema. El evento ocurre porque el contador llegó al
-- umbral, no porque el modelo se acordó. El modelo solo narra un hecho
-- que ya es verdad en la base.
CREATE TABLE faction_clocks (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  faction_id    uuid NOT NULL REFERENCES factions(id) ON DELETE CASCADE,
  agenda        text NOT NULL,
  progress      numeric(6,2) NOT NULL DEFAULT 0,
  threshold     numeric(6,2) NOT NULL,
  rate_per_game_day numeric(6,3) NOT NULL DEFAULT 1.0,
  paused        boolean NOT NULL DEFAULT false,
  fired_at_turn bigint,
  on_fire_event jsonb NOT NULL DEFAULT '{}'::jsonb,
  visibility    visibility_level NOT NULL DEFAULT 'dm_only'
);

CREATE INDEX ON faction_clocks (campaign_id) WHERE NOT paused AND fired_at_turn IS NULL;

CREATE TABLE quests (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  title         text NOT NULL,
  description   text,
  status        quest_status NOT NULL DEFAULT 'unknown',

  -- Capa 1 de la detección de estancamiento: ¿hay algún objetivo con
  -- paso siguiente conocido? Puro SQL, gratis.
  next_step_known boolean NOT NULL DEFAULT false,

  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0
);

CREATE INDEX ON quests (campaign_id, status);

-- Semillas SIN ubicación. El plan es inventario de material disponible,
-- no secuencia de escenas. Se plantan DONDE EL GRUPO ESTÉ.
-- El grupo que monta un puesto en el mercado no está estancado: está
-- jugando, y el material planificado no se desperdicia.
CREATE TABLE session_seeds (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id    uuid REFERENCES sessions(id),
  kind          text NOT NULL,     -- threat | npc_agenda | revelation | hook
  content       text NOT NULL,
  location_id   uuid REFERENCES locations(id),  -- NULL = sin ubicar (default)
  planted_at_turn bigint,
  visibility    visibility_level NOT NULL DEFAULT 'dm_only'
);

CREATE INDEX ON session_seeds (campaign_id) WHERE planted_at_turn IS NULL;

-- ============================================================================
-- 6. PNJ: NÚCLEO, PERSONA, DISPOSICIÓN, CONOCIMIENTO
-- ============================================================================

-- Un solo agente ACTOR habita todas las fichas ("un actor para toda la obra").
-- La consistencia de personaje NO es propiedad emergente del modelo: es
-- propiedad del registro en base de datos. Si Elara suena igual en la sesión
-- 8 que en la 1, es porque voice_notes contiene la misma cadena.
CREATE TABLE npcs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name          text NOT NULL,
  species       text,
  culture_id    uuid,                -- cultura AUTORADA, desacoplada de especie
  social_role   text,
  appearance    text,

  status        npc_status NOT NULL DEFAULT 'alive',
  location_id   uuid REFERENCES locations(id),

  -- Personalidad: rasgo ESTABLE. No se mueve porque el grupo le caiga bien.
  -- Cuatro ejes (barato: inmutable, autorado, sin extractor que lo juzgue).
  warmth        smallint NOT NULL DEFAULT 0 CHECK (warmth    BETWEEN -100 AND 100),
  candor        smallint NOT NULL DEFAULT 0 CHECK (candor    BETWEEN -100 AND 100),
  principle     smallint NOT NULL DEFAULT 0 CHECK (principle BETWEEN -100 AND 100),
  boldness      smallint NOT NULL DEFAULT 0 CHECK (boldness  BETWEEN -100 AND 100),

  -- La riqueza vive aquí: contradicción interna, deseo vs. necesidad.
  traits            text[],
  internal_contradiction text,
  taboos            text[],
  voice_notes       text,             -- registro, muletillas, qué NO diría
  stated_desire     text,
  actual_need       text,
  fear              text,

  -- Solo la escala TEMPORAL depende de la especie, no el temperamento.
  -- Un elfo guarda un rencor más tiempo; eso no lo hace altivo.
  decay_multiplier numeric(4,2) NOT NULL DEFAULT 1.00,

  -- Efímero vs. persistido. Por defecto los PNJ de paso NO tocan la BD;
  -- se promueven cuando el grupo les presta atención (los 3 kobolds con
  -- gabardina se vuelven personajes porque los jugadores lo decidieron).
  is_persistent    boolean NOT NULL DEFAULT true,
  promoted_at_turn bigint,
  appearance_count integer NOT NULL DEFAULT 0,

  visibility       visibility_level NOT NULL DEFAULT 'party',
  created_at_turn  bigint NOT NULL DEFAULT 0,
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON npcs (campaign_id, status);
CREATE INDEX ON npcs (campaign_id, location_id);

-- Ideal / Vínculo / Defecto: prosa para el ACTOR, referencias tipadas para
-- el EXTRACTOR. El extractor nunca juzga "¿tocó su vínculo?" — pregunta
-- "¿alguna entidad afectada está en bond_targets?", que es un WHERE IN.
-- Nulo es estado normal: un tabernero de paso no modula nada.
CREATE TABLE npc_ibf (
  npc_id        uuid PRIMARY KEY REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

  ideal_text    text,
  ideal_tags    text[],       -- vocabulario CERRADO de 15 etiquetas
  bond_text     text,
  bond_strength smallint DEFAULT 50 CHECK (bond_strength BETWEEN 0 AND 100),
  flaw_text     text,
  flaw_tags     text[],
  flaw_exploit  text          -- enum de superficie de manipulación
);

-- Los vínculos apuntan a ENTIDADES. Consultables en ambas direcciones:
-- "¿quién tiene un vínculo hacia X?" propaga deltas sin programar nada.
-- Un salto, y solo si el PNJ PUDO enterarse (ver npc_knowledge).
CREATE TABLE npc_bond_targets (
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  target_type   entity_type NOT NULL,
  target_id     uuid NOT NULL,
  PRIMARY KEY (npc_id, target_type, target_id)
);

CREATE INDEX ON npc_bond_targets (target_type, target_id);

-- Disposición: acumuladores CONTINUOS, presentados al modelo en BANDAS.
-- Continuo resuelve que muchos gestos pequeños sumen; las bandas resuelven
-- que el actor pueda interpretarlo. El modelo NUNCA ve el número.
-- Tres ejes permiten estados imposibles en uno: "te aprecia y no te cuenta",
-- "te desprecia y te teme".
CREATE TABLE npc_disposition (
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  -- NULL = hacia el grupo entero; UUID = hacia un PJ concreto.
  -- En intriga, que un PNJ prefiera a un PJ sobre otro es medio juego.
  pc_id         uuid,

  affinity      numeric(6,2) NOT NULL DEFAULT 0 CHECK (affinity BETWEEN -100 AND 100),
  trust         numeric(6,2) NOT NULL DEFAULT 0 CHECK (trust    BETWEEN -100 AND 100),
  respect       numeric(6,2) NOT NULL DEFAULT 0 CHECK (respect  BETWEEN -100 AND 100),

  -- Topes por personalidad: Walder Frey es ESTRUCTURALMENTE incapaz de
  -- confiar (trust máx +20); Ned Stark rompe una vez y para siempre.
  trust_ceiling numeric(6,2) NOT NULL DEFAULT 100,
  trust_floor   numeric(6,2) NOT NULL DEFAULT -100,

  updated_at_turn bigint NOT NULL DEFAULT 0
);

CREATE UNIQUE INDEX npc_disposition_key
  ON npc_disposition (npc_id, COALESCE(pc_id, '00000000-0000-0000-0000-000000000000'::uuid));

-- APPEND-ONLY. Un PNJ nunca "desaprende". "¿Qué sabía Elara en el turno 340?"
-- es un WHERE learned_at_turn <= 340. Resuelve la asimetría de información
-- sin lógica adicional, y es el filtro que evita que todos sepan todo al instante.
CREATE TABLE npc_knowledge (
  id            bigserial PRIMARY KEY,
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  fact          text NOT NULL,
  learned_at_turn bigint NOT NULL,
  source        text
);

CREATE INDEX ON npc_knowledge (npc_id, learned_at_turn);

-- Secretos con CONDICIÓN de revelación explícita: el actor sabe qué puede
-- soltar y bajo qué presión, en vez de improvisar revelaciones que rompen trama.
CREATE TABLE npc_secrets (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  npc_id        uuid NOT NULL REFERENCES npcs(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  content       text NOT NULL,
  reveal_condition text NOT NULL,
  revealed_at_turn bigint,
  visibility    visibility_level NOT NULL DEFAULT 'dm_only'
);

CREATE INDEX ON npc_secrets (npc_id) WHERE revealed_at_turn IS NULL;

-- ============================================================================
-- 7. PERSONAJES JUGADORES
-- ============================================================================

-- Asimetría fundamental: en un PNJ el sistema es dueño de todo.
-- En un PJ, el JUGADOR escribió esos campos y el sistema NO los reescribe.
-- El sistema observa y reporta; el jugador decide y escribe.
CREATE TABLE characters (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  user_id       uuid NOT NULL REFERENCES users(id),

  -- Propiedad del jugador. El sistema solo LEE.
  name          text NOT NULL,
  species       text,
  class_levels  jsonb NOT NULL DEFAULT '[]'::jsonb,
  background    text,
  ideal_text    text,
  bond_text     text,
  flaw_text     text,
  backstory     text,

  -- Propiedad del sistema (mecánico, validado contra SRD).
  hp_current    integer,
  hp_max        integer,
  conditions    text[] NOT NULL DEFAULT '{}',
  inventory     jsonb NOT NULL DEFAULT '[]'::jsonb,
  currency      jsonb NOT NULL DEFAULT '{}'::jsonb,
  xp            integer NOT NULL DEFAULT 0,
  inspiration   boolean NOT NULL DEFAULT false,
  exhaustion    smallint NOT NULL DEFAULT 0 CHECK (exhaustion BETWEEN 0 AND 6),

  -- Mecánicas opcionales (solo si el perfil las activa).
  hunger        smallint,
  thirst        smallint,

  location_id   uuid REFERENCES locations(id),
  is_active     boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON characters (campaign_id, user_id);

-- El PJ vinculado a entidades del mundo. Misma propagación que los PNJ.
CREATE TABLE pc_bond_targets (
  pc_id         uuid NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  target_type   entity_type NOT NULL,
  target_id     uuid NOT NULL,
  PRIMARY KEY (pc_id, target_type, target_id)
);

CREATE INDEX ON pc_bond_targets (target_type, target_id);

-- APPEND-ONLY, y NUNCA reescribe la hoja. Registra cuándo las acciones
-- del jugador honran o contradicen lo que declaró.
-- Registrar es gratis; no registrar es irreversible. Si a mitad de una
-- campaña episódica el grupo se engancha y suben el slider, el historial
-- ya está y la evolución es visible retroactivamente.
CREATE TABLE pc_ibf_tension (
  id            bigserial PRIMARY KEY,
  pc_id         uuid NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  element       text NOT NULL CHECK (element IN ('ideal', 'bond', 'flaw')),
  alignment     smallint NOT NULL CHECK (alignment IN (-1, 1)),
  evidence      text NOT NULL,
  turn_id       bigint NOT NULL
);

CREATE INDEX ON pc_ibf_tension (pc_id, turn_id);

-- ============================================================================
-- 8. ITEMS Y RELACIONES
-- ============================================================================

CREATE TABLE items (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name          text NOT NULL,
  description   text,
  holder_type   entity_type,
  holder_id     uuid,
  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at_turn bigint NOT NULL DEFAULT 0
);

-- El grafo ES una tabla. Una campaña tiene cientos de entidades, no millones:
-- multi-hop exacto = CTE recursivo. No hace falta Neo4j ni Kuzu.
-- Aquí SÍ hay vigencia directa: una relación nace y muere en turnos concretos.
CREATE TABLE entity_relations (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  from_type     entity_type NOT NULL,
  from_id       uuid NOT NULL,
  rel_type      text NOT NULL,      -- member_of | owes | rules | kin | rival...
  to_type       entity_type NOT NULL,
  to_id         uuid NOT NULL,
  strength      smallint,
  valid_from_turn bigint NOT NULL DEFAULT 0,
  valid_to_turn   bigint,           -- NULL = vigente
  visibility    visibility_level NOT NULL DEFAULT 'party'
);

CREATE INDEX ON entity_relations (campaign_id, from_type, from_id) WHERE valid_to_turn IS NULL;
CREATE INDEX ON entity_relations (campaign_id, to_type, to_id)     WHERE valid_to_turn IS NULL;

-- ============================================================================
-- 9. LISTA BLANCA DE CAMPOS MUTABLES  +  LEDGER DE DELTAS
-- ============================================================================

-- El apalancamiento real NO está en el clasificador, está aquí.
-- Si un delta puede ser cualquier cosa sobre cualquier campo, ningún
-- clasificador es lo bastante bueno. Si solo puede tomar ~18 formas, el
-- modelo puede equivocarse sobre SI algo pasó, pero no puede inventar
-- QUÉ TIPO de cosa pasó. La alucinación queda acotada estructuralmente.
CREATE TABLE mutable_fields (
  entity_type   entity_type NOT NULL,
  field_name    text NOT NULL,
  value_kind    text NOT NULL CHECK (value_kind IN ('enum','numeric','uuid','bool','append')),
  min_value     numeric,
  max_value     numeric,
  max_delta_per_turn numeric,
  allowed_values text[],
  PRIMARY KEY (entity_type, field_name)
);

INSERT INTO mutable_fields (entity_type, field_name, value_kind, min_value, max_value, max_delta_per_turn, allowed_values) VALUES
  ('npc',      'status',            'enum',    NULL, NULL, NULL, ARRAY['alive','dead','missing','captured']),
  ('npc',      'location_id',       'uuid',    NULL, NULL, NULL, NULL),
  ('npc',      'affinity',          'numeric', -100, 100, 50,   NULL),
  ('npc',      'trust',             'numeric', -100, 100, 50,   NULL),
  ('npc',      'respect',           'numeric', -100, 100, 50,   NULL),
  ('npc',      'knowledge',         'append',  NULL, NULL, NULL, NULL),
  ('npc',      'secret_revealed',   'append',  NULL, NULL, NULL, NULL),
  ('location', 'state',             'enum',    NULL, NULL, NULL, ARRAY['intact','damaged','destroyed','occupied','abandoned']),
  ('location', 'detail',            'enum',    NULL, NULL, NULL, ARRAY['sketch','observed','full']),
  ('location', 'controlling_faction_id','uuid', NULL, NULL, NULL, NULL),
  ('faction',  'stance_party',      'numeric', -100, 100, 50,   NULL),
  ('faction',  'knows_about_party', 'bool',    NULL, NULL, NULL, NULL),
  ('faction',  'clock_progress',    'numeric', 0,    9999, NULL, NULL),
  ('quest',    'status',            'enum',    NULL, NULL, NULL, ARRAY['unknown','active','completed','failed','abandoned']),
  ('quest',    'next_step_known',   'bool',    NULL, NULL, NULL, NULL),
  ('character','hp_current',        'numeric', -99,  999,  NULL, NULL),
  ('character','conditions',        'append',  NULL, NULL, NULL, NULL),
  ('character','inventory',         'append',  NULL, NULL, NULL, NULL),
  ('world',    'game_day',          'numeric', 0,    999999, NULL, NULL);

-- El ledger. Fuente del recap: los hechos se DERIVAN del diff, no se generan.
-- Un recap malo envenena la campaña permanentemente; derivar de deltas
-- elimina el compounding porque los deltas no acumulan error.
CREATE TABLE state_deltas (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  session_id    uuid REFERENCES sessions(id),
  turn_id       bigint NOT NULL,

  entity_type   entity_type NOT NULL,
  entity_id     uuid,                    -- NULL solo para entity_type='world'
  field_name    text NOT NULL,
  old_value     jsonb,
  new_value     jsonb NOT NULL,

  source        delta_source NOT NULL,
  -- El campo que hace TODO el trabajo antialucinación: span LITERAL del turno.
  -- Se valida en código antes de escribir. Un modelo que debe citar el texto
  -- que justifica el cambio no puede inventar el cambio.
  evidence      text,
  visibility    visibility_level NOT NULL DEFAULT 'party',
  created_at    timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT extracted_requires_evidence
    CHECK (source <> 'extracted' OR evidence IS NOT NULL)
);

CREATE INDEX ON state_deltas (campaign_id, turn_id);
CREATE INDEX ON state_deltas (campaign_id, entity_type, entity_id, turn_id DESC);
CREATE INDEX ON state_deltas (session_id);

-- Los rechazados se GUARDAN. Es la instrumentación que separa
-- "sé que funciona" de "asumo que funciona": si la tasa de rechazo sube,
-- el prompt derivó. El no-op silencioso es el fallo que muerde.
CREATE TABLE rejected_deltas (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id       bigint NOT NULL,
  payload       jsonb NOT NULL,
  reason        text NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- ============================================================================
-- 9b. TABLA DE MAGNITUDES
-- El extractor clasifica el TIPO de evento (enum cerrado). Nunca elige números.
-- Los números salen de aquí, modulados por el eje de personalidad del PNJ.
-- Un mismo evento produce deltas distintos, e incluso de signo opuesto,
-- según a quién le ocurra.
-- ============================================================================

CREATE TYPE event_kind AS ENUM (
  'bribe_offered', 'promise_kept', 'promise_broken', 'courtesy',
  'bond_target_protected', 'bond_target_harmed', 'life_saved',
  'betrayal_proven', 'threat_made', 'competence_shown',
  'ideal_honored', 'ideal_violated', 'public_status_given', 'secret_entrusted'
);

CREATE TABLE event_magnitudes (
  event         event_kind NOT NULL,
  -- Qué eje de personalidad decide la reacción.
  modulator     text NOT NULL CHECK (modulator IN ('principle','warmth','candor','boldness','none')),
  -- Banda del modulador: high > 50, mid -50..50, low < -50.
  band          text NOT NULL CHECK (band IN ('high','mid','low','any')),
  d_affinity    numeric(5,1) NOT NULL DEFAULT 0,
  d_trust       numeric(5,1) NOT NULL DEFAULT 0,
  d_respect     numeric(5,1) NOT NULL DEFAULT 0,
  -- Qué ocurre narrativamente. El Actor lo lee; no lo improvisa.
  outcome       text NOT NULL,
  PRIMARY KEY (event, band)
);

INSERT INTO event_magnitudes (event, modulator, band, d_affinity, d_trust, d_respect, outcome) VALUES
  -- SOBORNO. El caso que mejor muestra la inversión de signo.
  ('bribe_offered','principle','high',  -15, -20, -25, 'La oferta ES la ofensa. Se ofende aunque el grupo sea aliado: le acaban de decir quién creen que es. Rechaza sin negociar y lo recuerda.'),
  ('bribe_offered','principle','mid',    -4,  -6,  -2, 'Incómodo. Rechaza pero no lo convierte en un asunto personal. Cambia de tema.'),
  ('bribe_offered','principle','low',    +2,   0,  +5, 'NO se ofende. Si rechaza es por insuficiente, no por indigno. Contraoferta o insinúa el precio correcto.'),

  ('promise_kept','principle','high',    +8, +15, +12, 'Lo registra como prueba de carácter, no como favor.'),
  ('promise_kept','principle','mid',     +6,  +8,  +5, 'Agradece y lo tiene en cuenta.'),
  ('promise_kept','principle','low',     +1,  +2,  +8, 'Registra la capacidad de cumplir, no la virtud de haber cumplido.'),

  ('promise_broken','principle','high',  -6, -18, -10, 'La palabra rota pesa más que el daño causado. Lo dice a la cara.'),
  ('promise_broken','principle','mid',   -5,  -8,  -4, 'Molesto. Da margen si hay explicación.'),
  ('promise_broken','principle','low',   -2,  -3,  -6, 'Lo esperaba. Baja el respeto por ineptos, no por indignos.'),

  ('courtesy','warmth','high',           +3,  +1,   0, 'Responde con calidez.'),
  ('courtesy','warmth','mid',            +1,   0,   0, 'Lo nota, no lo comenta.'),
  ('courtesy','warmth','low',             0,   0,   0, 'Indiferente. La cortesía no le mueve nada.'),

  ('bond_target_protected','none','any',+25, +15, +12, 'Tocaron lo que protegería por encima de todo, en la buena dirección.'),
  ('bond_target_harmed','none','any',   -45, -30,  -5, 'Tocaron su vínculo. Es lo más grave que le pueden hacer sin matarlo.'),
  ('life_saved','none','any',           +30, +25, +15, 'Deuda de sangre. No se olvida.'),
  ('betrayal_proven','none','any',      -40, -70, -20, 'Traición demostrada. En PNJ de principios, además FIJA el techo de confianza.'),

  ('threat_made','boldness','high',      -8,  -5, +10, 'No se amilana. Sube el respeto por atreverse, baja el aprecio.'),
  ('threat_made','boldness','mid',      -10,  -8,   0, 'Cede en el momento, lo guarda.'),
  ('threat_made','boldness','low',      -12, -10, +15, 'Cede y teme. El miedo se lee como respeto y contamina la relación.'),

  ('competence_shown','none','any',       +2,  +3, +12, 'Reevalúa lo que el grupo puede hacer.'),
  ('ideal_honored','none','any',          +5,  +5, +12, 'Actuaron según lo que él considera correcto.'),
  ('ideal_violated','none','any',         -8,  -6, -15, 'Actuaron contra lo que él considera correcto.'),
  ('public_status_given','none','any',    +6,  +2,  +4, 'Le dieron en público el trato que cree merecer. Explota el defecto de estatus.'),
  ('secret_entrusted','none','any',       +5, +20,  +3, 'Confiarle algo que expone a quien lo cuenta es en sí un acto de confianza.');

-- ---------------------------------------------------------------------------
-- resolve_event: dado un PNJ y un tipo de evento, devuelve los tres deltas
-- ya modulados por SU personalidad, más lo que debe ocurrir narrativamente.
-- El modelo clasifica el evento; los números salen de aquí.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION resolve_event(p_npc_id uuid, p_event event_kind)
RETURNS TABLE (d_affinity numeric, d_trust numeric, d_respect numeric,
               band text, outcome text)
LANGUAGE plpgsql STABLE AS $$
DECLARE v_mod text; v_val numeric; v_band text;
BEGIN
  SELECT DISTINCT modulator INTO v_mod FROM event_magnitudes WHERE event = p_event;

  IF v_mod = 'none' THEN
    v_band := 'any';
  ELSE
    EXECUTE format('SELECT %I FROM npcs WHERE id = $1', v_mod)
      INTO v_val USING p_npc_id;
    v_band := CASE WHEN v_val >  50 THEN 'high'
                   WHEN v_val < -50 THEN 'low'
                   ELSE 'mid' END;
  END IF;

  RETURN QUERY
    SELECT m.d_affinity, m.d_trust, m.d_respect, m.band, m.outcome
      FROM event_magnitudes m
     WHERE m.event = p_event AND m.band = v_band;
END;
$$;


-- ============================================================================
-- 10. RECAPS DE SESIÓN
-- ============================================================================

-- Dos campos SEPARADOS: facts es autoritativo y derivado del ledger;
-- narrative_summary es prosa ADVISORIA. Si se contradicen, ganan los hechos.
-- El recap es un caché RECOMPUTABLE: el turn_log crudo queda íntegro,
-- así que un recap malo se arregla. Un resumen que reemplazó a su fuente, no.
CREATE TABLE session_recaps (
  session_id    uuid PRIMARY KEY REFERENCES sessions(id) ON DELETE CASCADE,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  facts         jsonb NOT NULL DEFAULT '[]'::jsonb,   -- derivado de state_deltas
  narrative_summary text,                             -- prosa, advisorio
  open_threads  jsonb NOT NULL DEFAULT '[]'::jsonb,
  generated_at  timestamptz NOT NULL DEFAULT now(),
  regenerated_count integer NOT NULL DEFAULT 0
);

-- ============================================================================
-- 11. INGESTA DE LORE (pgvector)
-- ============================================================================

-- Ingesta inicial opcional: el usuario sube su propio lore en .md.
-- Los wiki-links [[Casa Vorren]] son aristas EXPLÍCITAS que no requieren
-- inferencia: el grafo viene medio construido con la topología que él quiso.
CREATE TABLE lore_documents (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  filename      text NOT NULL,
  raw_content   text NOT NULL,
  ingested_at   timestamptz NOT NULL DEFAULT now()
);

-- Prosa de referencia: atmósfera, historia. Responde "¿cómo se siente
-- estar aquí?". Distinto de las entidades canónicas, que responden
-- "¿quién gobierna?" y son consultables exactamente.
CREATE TABLE lore_chunks (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  document_id   uuid REFERENCES lore_documents(id) ON DELETE CASCADE,
  heading_path  text,
  content       text NOT NULL,
  -- bge-m3 local, versión FIJA. Si un proveedor actualizara el modelo
  -- entre las campañas de G2 y G1, el espacio vectorial cambiaría a mitad
  -- de experimento. Un archivo en disco no cambia nunca.
  embedding     vector(1024),
  embedding_model text NOT NULL DEFAULT 'bge-m3'
);

CREATE INDEX ON lore_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON lore_chunks (campaign_id);

-- Narrativa pasada indexada. ÚNICO lugar donde la recuperación aproximada
-- es correcta: "¿ha pasado algo parecido antes?" no tiene respuesta exacta.
-- El estado de entidades NO va aquí: eso es un SELECT.
CREATE TABLE narrative_chunks (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  turn_id       bigint NOT NULL,
  session_id    uuid REFERENCES sessions(id),
  content       text NOT NULL,
  embedding     vector(1024),
  visibility    visibility_level NOT NULL DEFAULT 'party'
);

CREATE INDEX ON narrative_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON narrative_chunks (campaign_id, turn_id);

-- Corpus estático de reglas: SRD, mecánicas opcionales, homebrew.
-- No cambia, así que no tiene problema temporal. Sin campaign_id cuando
-- es SRD compartido.
CREATE TABLE rules_chunks (
  id            bigserial PRIMARY KEY,
  tenant_id     uuid REFERENCES tenants(id) ON DELETE CASCADE,
  campaign_id   uuid REFERENCES campaigns(id) ON DELETE CASCADE,
  source        text NOT NULL,       -- 'srd' | 'homebrew' | 'optional'
  heading_path  text,
  content       text NOT NULL,
  embedding     vector(1024)
);

CREATE INDEX ON rules_chunks USING hnsw (embedding vector_cosine_ops);

-- ============================================================================
-- 12. FUNCIONES
-- ============================================================================

-- Bandas conductuales. El modelo NUNCA ve el número: recibe CONDUCTA.
-- Siete bandas por eje. Un float de dos decimales no produce comportamiento
-- distinguible; una banda con guía conductual sí.
CREATE OR REPLACE FUNCTION disposition_band(raw numeric)
RETURNS text LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE
    WHEN raw <= -60 THEN 'hostile'
    WHEN raw <= -25 THEN 'wary'
    WHEN raw <=  -8 THEN 'cold'
    WHEN raw <   8  THEN 'neutral'
    WHEN raw <   25 THEN 'cordial'
    WHEN raw <   60 THEN 'loyal'
    ELSE                 'devoted'
  END;
$$;

-- ---------------------------------------------------------------------------
-- apply_delta: LA única puerta de escritura narrativa.
-- Es el caso de libro para procedimiento almacenado: validar contra lista
-- blanca, actualizar entidad y registrar en el ledger deben ser ATÓMICOS.
-- Hecho desde el orquestador en tres llamadas, un fallo deja estado corrupto.
-- Y como el orquestador es remoto, además ahorra round-trips.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION apply_delta(
  p_campaign_id  uuid,
  p_entity_type  entity_type,
  p_entity_id    uuid,
  p_field        text,
  p_value        jsonb,
  p_turn_id      bigint,
  p_source       delta_source,
  p_evidence     text DEFAULT NULL,
  p_visibility   visibility_level DEFAULT 'party',
  p_session_id   uuid DEFAULT NULL
) RETURNS bigint
LANGUAGE plpgsql AS $$
DECLARE
  v_tenant   uuid;
  v_spec     mutable_fields;
  v_old      jsonb;
  v_num      numeric;
  v_delta_id bigint;
  v_table    text;
BEGIN
  SELECT tenant_id INTO v_tenant FROM campaigns WHERE id = p_campaign_id;
  IF v_tenant IS NULL THEN
    RAISE EXCEPTION 'campaign % not found', p_campaign_id;
  END IF;

  -- 1. Lista blanca. Un campo fuera de ella no existe para el sistema.
  SELECT * INTO v_spec FROM mutable_fields
   WHERE entity_type = p_entity_type AND field_name = p_field;
  IF v_spec IS NULL THEN
    RAISE EXCEPTION 'field %.% is not delta-able', p_entity_type, p_field;
  END IF;

  -- 2. Evidencia obligatoria para lo extraído.
  IF p_source = 'extracted' AND (p_evidence IS NULL OR length(trim(p_evidence)) = 0) THEN
    RAISE EXCEPTION 'extracted delta requires evidence span';
  END IF;

  -- 3. Validación de dominio.
  IF v_spec.value_kind = 'enum' THEN
    IF NOT (p_value #>> '{}' = ANY (v_spec.allowed_values)) THEN
      RAISE EXCEPTION 'value % not allowed for %.%', p_value, p_entity_type, p_field;
    END IF;
  ELSIF v_spec.value_kind = 'numeric' THEN
    v_num := (p_value #>> '{}')::numeric;
    IF v_spec.min_value IS NOT NULL AND v_num < v_spec.min_value THEN
      RAISE EXCEPTION 'value % below minimum % for %.%', v_num, v_spec.min_value, p_entity_type, p_field;
    END IF;
    IF v_spec.max_value IS NOT NULL AND v_num > v_spec.max_value THEN
      RAISE EXCEPTION 'value % above maximum % for %.%', v_num, v_spec.max_value, p_entity_type, p_field;
    END IF;
  END IF;

  -- 4. Aplicar sobre la entidad. Los campos 'append' no se actualizan aquí:
  --    van a sus tablas append-only (npc_knowledge, etc.).
  IF v_spec.value_kind <> 'append' THEN
    IF p_entity_type = 'npc' AND p_field IN ('affinity','trust','respect') THEN
      -- Disposición vive en su propia tabla, con topes por personalidad.
      INSERT INTO npc_disposition (npc_id, tenant_id, pc_id, updated_at_turn)
        VALUES (p_entity_id, v_tenant, NULL, p_turn_id)
        ON CONFLICT DO NOTHING;

      EXECUTE format(
        'SELECT to_jsonb(%I) FROM npc_disposition WHERE npc_id = $1 AND pc_id IS NULL',
        p_field
      ) INTO v_old USING p_entity_id;

      -- Los topes por personalidad se APLICAN aquí, no solo se almacenan.
      -- Walder Frey es estructuralmente incapaz de confiar: su techo de +20
      -- no es una etapa que se supere, es un límite de carácter.
      IF p_field = 'trust' THEN
        SELECT LEAST(GREATEST(v_num, trust_floor), trust_ceiling)
          INTO v_num
          FROM npc_disposition
         WHERE npc_id = p_entity_id AND pc_id IS NULL;
      END IF;

      EXECUTE format(
        'UPDATE npc_disposition SET %I = LEAST(GREATEST($1, -100), 100), updated_at_turn = $2
          WHERE npc_id = $3 AND pc_id IS NULL', p_field
      ) USING v_num, p_turn_id, p_entity_id;

    ELSIF p_entity_type = 'world' THEN
      SELECT to_jsonb(game_day) INTO v_old FROM campaigns WHERE id = p_campaign_id;
      UPDATE campaigns SET game_day = v_num::integer WHERE id = p_campaign_id;

    ELSE
      v_table := CASE p_entity_type
        WHEN 'npc' THEN 'npcs' WHEN 'location' THEN 'locations'
        WHEN 'faction' THEN 'factions' WHEN 'quest' THEN 'quests'
        WHEN 'character' THEN 'characters' WHEN 'item' THEN 'items' END;

      EXECUTE format('SELECT to_jsonb(%I) FROM %I WHERE id = $1', p_field, v_table)
        INTO v_old USING p_entity_id;

      IF v_spec.value_kind = 'uuid' THEN
        EXECUTE format('UPDATE %I SET %I = ($1 #>> ''{}'')::uuid WHERE id = $2', v_table, p_field)
          USING p_value, p_entity_id;
      ELSIF v_spec.value_kind = 'bool' THEN
        EXECUTE format('UPDATE %I SET %I = ($1 #>> ''{}'')::boolean WHERE id = $2', v_table, p_field)
          USING p_value, p_entity_id;
      ELSIF v_spec.value_kind = 'numeric' THEN
        EXECUTE format('UPDATE %I SET %I = $1 WHERE id = $2', v_table, p_field)
          USING v_num, p_entity_id;
      ELSE
        EXECUTE format('UPDATE %I SET %I = ($1 #>> ''{}'')::%s WHERE id = $2',
                       v_table, p_field,
                       CASE WHEN p_entity_type = 'npc' THEN 'npc_status'
                            WHEN p_entity_type = 'location' AND p_field = 'state' THEN 'location_state'
                            WHEN p_entity_type = 'location' AND p_field = 'detail' THEN 'detail_level'
                            WHEN p_entity_type = 'quest' THEN 'quest_status'
                            ELSE 'text' END)
          USING p_value, p_entity_id;
      END IF;
    END IF;
  END IF;

  -- 5. Ledger. En la MISMA transacción.
  INSERT INTO state_deltas (
    tenant_id, campaign_id, session_id, turn_id, entity_type, entity_id,
    field_name, old_value, new_value, source, evidence, visibility
  ) VALUES (
    v_tenant, p_campaign_id, p_session_id, p_turn_id, p_entity_type, p_entity_id,
    p_field, v_old, p_value, p_source, p_evidence, p_visibility
  ) RETURNING id INTO v_delta_id;

  RETURN v_delta_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- advance_clocks: las repercusiones como GARANTÍA, no como memoria del modelo.
-- Avanza contadores con el TIEMPO DE JUEGO (no con turnos), evalúa umbrales
-- y devuelve los eventos disparados. El modelo solo narra un hecho que ya
-- es verdad en la base.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION advance_clocks(
  p_campaign_id uuid,
  p_game_days   numeric,
  p_turn_id     bigint
) RETURNS TABLE (clock_id uuid, faction_id uuid, agenda text, event jsonb)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE faction_clocks c
     SET progress = c.progress + (p_game_days * c.rate_per_game_day)
   WHERE c.campaign_id = p_campaign_id
     AND NOT c.paused
     AND c.fired_at_turn IS NULL;

  UPDATE faction_clocks c
     SET fired_at_turn = p_turn_id
   WHERE c.campaign_id = p_campaign_id
     AND c.fired_at_turn IS NULL
     AND NOT c.paused
     AND c.progress >= c.threshold;

  RETURN QUERY
    SELECT c.id, c.faction_id, c.agenda, c.on_fire_event
      FROM faction_clocks c
     WHERE c.campaign_id = p_campaign_id
       AND c.fired_at_turn = p_turn_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- decay_dispositions: decaimiento PROPORCIONAL al cerrar sesión.
-- Se MATERIALIZA al escribir, no se calcula al leer: así mover el slider
-- no reescribe retroactivamente la historia. El pasado queda congelado.
-- Proporcional resuelve trivial-vs-grave sin clasificar sesiones:
-- un +3 de cortesía se disuelve; un -40 de traición sigue pesando.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION decay_dispositions(p_campaign_id uuid, p_turn_id bigint)
RETURNS integer LANGUAGE plpgsql AS $$
DECLARE v_pct numeric; v_count integer;
BEGIN
  SELECT disposition_decay_pct INTO v_pct FROM campaigns WHERE id = p_campaign_id;

  WITH updated AS (
    UPDATE npc_disposition d
       SET affinity = d.affinity * (1 - (v_pct/100) * n.decay_multiplier),
           trust    = d.trust    * (1 - (v_pct/100) * n.decay_multiplier),
           respect  = d.respect  * (1 - (v_pct/100) * n.decay_multiplier),
           updated_at_turn = p_turn_id
      FROM npcs n
     WHERE d.npc_id = n.id AND n.campaign_id = p_campaign_id
    RETURNING 1
  ) SELECT count(*) INTO v_count FROM updated;

  RETURN v_count;
END;
$$;

-- ---------------------------------------------------------------------------
-- get_visible_state: filtrado por visibilidad en UNA consulta.
-- El jugador ve lo que su grupo descubrió; el DM ve todo.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_visible_state(
  p_campaign_id uuid,
  p_viewer_id   uuid,
  p_entity_type entity_type DEFAULT NULL
) RETURNS TABLE (entity_type entity_type, entity_id uuid, name text, payload jsonb)
LANGUAGE plpgsql AS $$
DECLARE v_is_dm boolean;
BEGIN
  SELECT COALESCE(is_dm, false) INTO v_is_dm
    FROM campaign_members
   WHERE campaign_id = p_campaign_id AND user_id = p_viewer_id;

  RETURN QUERY
    SELECT 'npc'::entity_type, n.id, n.name,
           jsonb_build_object(
             'status', n.status, 'location_id', n.location_id,
             'affinity_band', disposition_band(COALESCE(d.affinity, 0)),
             'trust_band',    disposition_band(COALESCE(d.trust, 0)),
             'respect_band',  disposition_band(COALESCE(d.respect, 0))
           )
      FROM npcs n
      LEFT JOIN npc_disposition d ON d.npc_id = n.id AND d.pc_id IS NULL
     WHERE n.campaign_id = p_campaign_id
       AND (p_entity_type IS NULL OR p_entity_type = 'npc')
       AND (v_is_dm OR n.visibility <> 'dm_only')
  UNION ALL
    SELECT 'location'::entity_type, l.id, l.name,
           jsonb_build_object('kind', l.kind, 'state', l.state, 'detail', l.detail,
                              'description', COALESCE(l.description_canonical, l.sketch_text))
      FROM locations l
     WHERE l.campaign_id = p_campaign_id
       AND (p_entity_type IS NULL OR p_entity_type = 'location')
       AND (v_is_dm OR l.visibility <> 'dm_only')
  UNION ALL
    SELECT 'quest'::entity_type, q.id, q.title,
           jsonb_build_object('status', q.status, 'next_step_known', q.next_step_known)
      FROM quests q
     WHERE q.campaign_id = p_campaign_id
       AND (p_entity_type IS NULL OR p_entity_type = 'quest')
       AND (v_is_dm OR q.visibility <> 'dm_only');
END;
$$;

-- ---------------------------------------------------------------------------
-- location_context: la cadena de ancestros con herencia de cultura.
-- Hace que "coherente con la cultura local" sea un SELECT y no una
-- instrucción que el modelo puede olvidar.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION location_context(p_location_id uuid)
RETURNS jsonb LANGUAGE sql STABLE AS $$
  WITH RECURSIVE chain AS (
    SELECT id, parent_id, name, kind, culture_overrides, 0 AS depth
      FROM locations WHERE id = p_location_id
    UNION ALL
    SELECT l.id, l.parent_id, l.name, l.kind, l.culture_overrides, c.depth + 1
      FROM locations l JOIN chain c ON l.id = c.parent_id
  )
  SELECT jsonb_build_object(
    'path', (SELECT jsonb_agg(jsonb_build_object('name', name, 'kind', kind) ORDER BY depth DESC) FROM chain),
    -- El nivel más específico gana: se acumula desde la raíz hacia la hoja.
    'culture', (SELECT COALESCE(jsonb_object_agg(k, v), '{}'::jsonb)
                  FROM (SELECT DISTINCT ON (k) k, v
                          FROM chain, jsonb_each(culture_overrides) AS e(k, v)
                         ORDER BY k, depth ASC) s)
  );
$$;

-- ---------------------------------------------------------------------------
-- stagnation_check: capas 1-3, todas SQL, todas gratis.
-- El grupo que monta un puesto en el mercado NO está estancado: está
-- generando estado. Solo si las tres capas apuntan a estancamiento se paga
-- una llamada al modelo. La pregunta repetida como gag muere en la capa 2.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION stagnation_check(p_campaign_id uuid, p_window integer DEFAULT 15)
RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT jsonb_build_object(
    'has_known_next_step', EXISTS (
      SELECT 1 FROM quests
       WHERE campaign_id = p_campaign_id AND status = 'active' AND next_step_known),
    'new_state_generated', (
      SELECT count(*) FROM state_deltas
       WHERE campaign_id = p_campaign_id
         AND turn_id > (SELECT current_turn - p_window FROM campaigns WHERE id = p_campaign_id)),
    'entities_created', (
      SELECT count(*) FROM npcs
       WHERE campaign_id = p_campaign_id
         AND created_at_turn > (SELECT current_turn - p_window FROM campaigns WHERE id = p_campaign_id))
  );
$$;

-- ============================================================================
-- 12b. PROPAGACIÓN — cierra el fallo de `knows_about_party`
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


-- ============================================================================
-- 13. ROW LEVEL SECURITY
-- ============================================================================
-- Declarativo. Ningún endpoint puede "olvidarlo", que es exactamente el
-- riesgo de implementar visibilidad en lógica de aplicación.
-- El orquestador fija app.tenant_id por transacción.

CREATE OR REPLACE FUNCTION current_tenant() RETURNS uuid
LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.tenant_id', true), '')::uuid;
$$;

DO $$
DECLARE t text;
BEGIN
  FOR t IN SELECT unnest(ARRAY[
    'users','campaigns','sessions','turn_log','turn_jobs','model_calls',
    'locations','factions','faction_clocks','quests','session_seeds',
    'npcs','npc_ibf','npc_bond_targets','npc_disposition','npc_knowledge',
    'npc_secrets','characters','pc_bond_targets','pc_ibf_tension','items',
    'entity_relations','state_deltas','rejected_deltas','session_recaps',
    'lore_documents','lore_chunks','narrative_chunks'
  ]) LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format(
      'CREATE POLICY tenant_isolation ON %I USING (tenant_id = current_tenant())', t);
  END LOOP;
END $$;

-- rules_chunks: tenant_id NULLable (SRD compartido entre tenants).
ALTER TABLE rules_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON rules_chunks
  USING (tenant_id IS NULL OR tenant_id = current_tenant());

-- campaign_members no tiene tenant_id propio (es tabla puente), así que la
-- política va por subconsulta. Sin esto la tabla queda LEGIBLE entre tenants,
-- y get_visible_state la usa para decidir quién es DM.
ALTER TABLE campaign_members ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON campaign_members USING (
  EXISTS (SELECT 1 FROM campaigns c
           WHERE c.id = campaign_members.campaign_id
             AND c.tenant_id = current_tenant()));

-- mutable_fields es catálogo de referencia compartido: sin RLS a propósito.
-- tenants no puede llevar RLS (no tiene tenant_id); se protege por GRANT.