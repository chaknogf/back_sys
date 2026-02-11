--
-- PostgreSQL database dump
--

\restrict bAu8JTvlRRbXDRqhNfZhrc8ENmMHaTEs0t8vBGnukniP6mebxOpFuegdbi1xQTM

-- Dumped from database version 18.1 (Homebrew)
-- Dumped by pg_dump version 18.1 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


--
-- Name: actualizar_nombre_completo(); Type: FUNCTION; Schema: public; Owner: admin
--

CREATE FUNCTION public.actualizar_nombre_completo() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.nombre_completo := regexp_replace(
    TRIM(
      COALESCE(NEW.nombre->>'primer_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'segundo_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'otro_nombre', '') || ' ' ||
      COALESCE(NEW.nombre->>'primer_apellido', '') || ' ' ||
      COALESCE(NEW.nombre->>'segundo_apellido', '') || ' ' ||
      COALESCE(NEW.nombre->>'apellido_casada', '')
    ),
    '\s+', ' ', 'g'  -- reemplaza múltiples espacios por uno
  );
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_nombre_completo() OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: constancia_medica_control; Type: TABLE; Schema: public; Owner: macbookairm2
--

CREATE TABLE public.constancia_medica_control (
    anio smallint NOT NULL,
    ultimo_correlativo integer DEFAULT 0 NOT NULL,
    actualizado_en timestamp without time zone DEFAULT now()
);


ALTER TABLE public.constancia_medica_control OWNER TO macbookairm2;

--
-- Name: constancia_nacimiento; Type: TABLE; Schema: public; Owner: macbookairm2
--

CREATE TABLE public.constancia_nacimiento (
    id integer NOT NULL,
    documento character varying(20) NOT NULL,
    paciente_id integer NOT NULL,
    medico_id integer NOT NULL,
    registrador_id integer NOT NULL,
    nombre_madre character varying(200) NOT NULL,
    vecindad_madre character varying(200),
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    menor_edad jsonb,
    hijos integer,
    vivos integer,
    muertos integer,
    observaciones text,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.constancia_nacimiento OWNER TO macbookairm2;

--
-- Name: constancia_nacimiento_control; Type: TABLE; Schema: public; Owner: macbookairm2
--

CREATE TABLE public.constancia_nacimiento_control (
    anio smallint NOT NULL,
    ultimo_correlativo integer DEFAULT 0 NOT NULL,
    actualizado_en timestamp without time zone DEFAULT now()
);


ALTER TABLE public.constancia_nacimiento_control OWNER TO macbookairm2;

--
-- Name: constancia_nacimiento_id_seq; Type: SEQUENCE; Schema: public; Owner: macbookairm2
--

CREATE SEQUENCE public.constancia_nacimiento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.constancia_nacimiento_id_seq OWNER TO macbookairm2;

--
-- Name: constancia_nacimiento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: macbookairm2
--

ALTER SEQUENCE public.constancia_nacimiento_id_seq OWNED BY public.constancia_nacimiento.id;


--
-- Name: consultas; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.consultas (
    id integer NOT NULL,
    expediente character varying(20),
    paciente_id integer NOT NULL,
    tipo_consulta integer NOT NULL,
    especialidad character varying(20) NOT NULL,
    servicio character varying(20) NOT NULL,
    documento character varying(20),
    fecha_consulta date NOT NULL,
    hora_consulta time without time zone NOT NULL,
    indicadores jsonb,
    ciclo jsonb,
    orden integer,
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now(),
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.consultas OWNER TO admin;

--
-- Name: consultas_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.consultas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.consultas_id_seq OWNER TO admin;

--
-- Name: consultas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.consultas_id_seq OWNED BY public.consultas.id;


--
-- Name: defuncion_control; Type: TABLE; Schema: public; Owner: macbookairm2
--

CREATE TABLE public.defuncion_control (
    anio smallint NOT NULL,
    ultimo_correlativo integer DEFAULT 0 NOT NULL,
    actualizado_en timestamp without time zone DEFAULT now()
);


ALTER TABLE public.defuncion_control OWNER TO macbookairm2;

--
-- Name: emergencia_control; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.emergencia_control (
    anio smallint NOT NULL,
    ultimo_correlativo integer DEFAULT 0 NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.emergencia_control OWNER TO admin;

--
-- Name: eventos_consulta; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.eventos_consulta (
    id integer NOT NULL,
    consulta_id integer NOT NULL,
    tipo_evento integer NOT NULL,
    datos jsonb,
    responsable jsonb,
    creado_en timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    actualizado_en timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    estado character varying(2) DEFAULT 'A'::character varying
);


ALTER TABLE public.eventos_consulta OWNER TO admin;

--
-- Name: eventos_consulta_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.eventos_consulta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eventos_consulta_id_seq OWNER TO admin;

--
-- Name: eventos_consulta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.eventos_consulta_id_seq OWNED BY public.eventos_consulta.id;


--
-- Name: expediente_control; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.expediente_control (
    anio smallint NOT NULL,
    ultimo_correlativo integer DEFAULT 0 NOT NULL,
    actualizado_en timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.expediente_control OWNER TO admin;

--
-- Name: medicos; Type: TABLE; Schema: public; Owner: macbookairm2
--

CREATE TABLE public.medicos (
    id integer NOT NULL,
    nombre character varying(200) NOT NULL,
    colegiado character varying(20),
    dpi bigint,
    sexo character(1),
    especialidad character varying(100),
    activo boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.medicos OWNER TO macbookairm2;

--
-- Name: medicos_id_seq; Type: SEQUENCE; Schema: public; Owner: macbookairm2
--

CREATE SEQUENCE public.medicos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medicos_id_seq OWNER TO macbookairm2;

--
-- Name: medicos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: macbookairm2
--

ALTER SEQUENCE public.medicos_id_seq OWNED BY public.medicos.id;


--
-- Name: municipios; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.municipios (
    codigo character varying(10) NOT NULL,
    vecindad character varying(100),
    municipio character varying(100) NOT NULL,
    departamento character varying(100) NOT NULL
);


ALTER TABLE public.municipios OWNER TO admin;

--
-- Name: pacientes; Type: TABLE; Schema: public; Owner: macbookairm2
--

CREATE TABLE public.pacientes (
    id integer NOT NULL,
    expediente character varying(20),
    cui bigint,
    nombre jsonb NOT NULL,
    sexo character(1),
    fecha_nacimiento date,
    contacto jsonb,
    referencias jsonb,
    datos_extra jsonb,
    estado character(1) DEFAULT 'V'::bpchar,
    metadatos jsonb,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    nombre_completo character varying(200),
    pasaporte character varying(50),
    CONSTRAINT pacientes_estado_check CHECK ((estado = ANY (ARRAY['V'::bpchar, 'F'::bpchar, 'I'::bpchar, 'A'::bpchar]))),
    CONSTRAINT pacientes_sexo_check CHECK ((sexo = ANY (ARRAY['M'::bpchar, 'F'::bpchar, 'NF'::bpchar])))
);


ALTER TABLE public.pacientes OWNER TO macbookairm2;

--
-- Name: pacientes_id_seq; Type: SEQUENCE; Schema: public; Owner: macbookairm2
--

CREATE SEQUENCE public.pacientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pacientes_id_seq OWNER TO macbookairm2;

--
-- Name: pacientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: macbookairm2
--

ALTER SEQUENCE public.pacientes_id_seq OWNED BY public.pacientes.id;


--
-- Name: paises_iso; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.paises_iso (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    codigo_iso3 character(3) NOT NULL
);


ALTER TABLE public.paises_iso OWNER TO admin;

--
-- Name: paises_iso_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.paises_iso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.paises_iso_id_seq OWNER TO admin;

--
-- Name: paises_iso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.paises_iso_id_seq OWNED BY public.paises_iso.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    estado character(1),
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now(),
    unidad integer,
    datos_extra jsonb
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vista_consultas; Type: VIEW; Schema: public; Owner: macbookairm2
--

CREATE VIEW public.vista_consultas AS
 SELECT p.id AS id_paciente,
    (p.datos_extra ->> 'personaid'::text) AS otro_id,
    p.cui,
    p.expediente,
    p.pasaporte,
    p.nombre,
    (p.nombre ->> 'primer_nombre'::text) AS primer_nombre,
    (p.nombre ->> 'segundo_nombre'::text) AS segundo_nombre,
    (p.nombre ->> 'otro_nombre'::text) AS otro_nombre,
    (p.nombre ->> 'primer_apellido'::text) AS primer_apellido,
    (p.nombre ->> 'segundo_apellido'::text) AS segundo_apellido,
    (p.nombre ->> 'apellido_casada'::text) AS apellido_casada,
    p.sexo,
    p.fecha_nacimiento,
    p.estado,
    c.id AS id_consulta,
    c.tipo_consulta,
    c.especialidad,
    c.servicio,
    c.documento,
    c.fecha_consulta,
    c.hora_consulta,
    c.ciclo,
    c.orden
   FROM (public.pacientes p
     JOIN public.consultas c ON ((p.id = c.paciente_id)));


ALTER VIEW public.vista_consultas OWNER TO macbookairm2;

--
-- Name: vista_totales; Type: VIEW; Schema: public; Owner: macbookairm2
--

CREATE VIEW public.vista_totales AS
 SELECT 'pacientes'::text AS entidad,
    count(*) AS total
   FROM public.pacientes
UNION ALL
 SELECT 'consultas'::text AS entidad,
    count(*) AS total
   FROM public.consultas
UNION ALL
 SELECT 'consultas_hoy'::text AS entidad,
    count(*) AS total
   FROM public.consultas
  WHERE (consultas.fecha_consulta = CURRENT_DATE)
UNION ALL
 SELECT 'coex_hoy'::text AS entidad,
    count(*) AS total
   FROM public.consultas
  WHERE ((consultas.tipo_consulta = 1) AND (consultas.fecha_consulta = CURRENT_DATE))
UNION ALL
 SELECT 'hospitalizaciones_hoy'::text AS entidad,
    count(*) AS total
   FROM public.consultas
  WHERE ((consultas.tipo_consulta = 2) AND (consultas.fecha_consulta = CURRENT_DATE))
UNION ALL
 SELECT 'emergencias_hoy'::text AS entidad,
    count(*) AS total
   FROM public.consultas
  WHERE ((consultas.tipo_consulta = 3) AND (consultas.fecha_consulta = CURRENT_DATE))
UNION ALL
 SELECT 'pacientes_activos'::text AS entidad,
    count(*) AS total
   FROM public.pacientes
  WHERE (pacientes.estado = 'ACTIVO'::bpchar);


ALTER VIEW public.vista_totales OWNER TO macbookairm2;

--
-- Name: constancia_nacimiento id; Type: DEFAULT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento ALTER COLUMN id SET DEFAULT nextval('public.constancia_nacimiento_id_seq'::regclass);


--
-- Name: consultas id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.consultas ALTER COLUMN id SET DEFAULT nextval('public.consultas_id_seq'::regclass);


--
-- Name: eventos_consulta id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.eventos_consulta ALTER COLUMN id SET DEFAULT nextval('public.eventos_consulta_id_seq'::regclass);


--
-- Name: medicos id; Type: DEFAULT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.medicos ALTER COLUMN id SET DEFAULT nextval('public.medicos_id_seq'::regclass);


--
-- Name: pacientes id; Type: DEFAULT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.pacientes ALTER COLUMN id SET DEFAULT nextval('public.pacientes_id_seq'::regclass);


--
-- Name: paises_iso id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.paises_iso ALTER COLUMN id SET DEFAULT nextval('public.paises_iso_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: constancia_medica_control constancia_medica_control_pkey; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_medica_control
    ADD CONSTRAINT constancia_medica_control_pkey PRIMARY KEY (anio);


--
-- Name: constancia_nacimiento_control constancia_nacimiento_control_pkey; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento_control
    ADD CONSTRAINT constancia_nacimiento_control_pkey PRIMARY KEY (anio);


--
-- Name: constancia_nacimiento constancia_nacimiento_documento_key; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento
    ADD CONSTRAINT constancia_nacimiento_documento_key UNIQUE (documento);


--
-- Name: constancia_nacimiento constancia_nacimiento_pkey; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento
    ADD CONSTRAINT constancia_nacimiento_pkey PRIMARY KEY (id);


--
-- Name: consultas consultas_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.consultas
    ADD CONSTRAINT consultas_pkey PRIMARY KEY (id);


--
-- Name: defuncion_control defuncion_control_pkey; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.defuncion_control
    ADD CONSTRAINT defuncion_control_pkey PRIMARY KEY (anio);


--
-- Name: emergencia_control emergencia_control_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.emergencia_control
    ADD CONSTRAINT emergencia_control_pkey PRIMARY KEY (anio);


--
-- Name: eventos_consulta eventos_consulta_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.eventos_consulta
    ADD CONSTRAINT eventos_consulta_pkey PRIMARY KEY (id);


--
-- Name: expediente_control expediente_control_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.expediente_control
    ADD CONSTRAINT expediente_control_pkey PRIMARY KEY (anio);


--
-- Name: medicos medicos_pkey; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.medicos
    ADD CONSTRAINT medicos_pkey PRIMARY KEY (id);


--
-- Name: municipios municipios_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_pkey PRIMARY KEY (codigo);


--
-- Name: pacientes pacientes_cui_key; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.pacientes
    ADD CONSTRAINT pacientes_cui_key UNIQUE (cui);


--
-- Name: pacientes pacientes_expediente_key; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.pacientes
    ADD CONSTRAINT pacientes_expediente_key UNIQUE (expediente);


--
-- Name: pacientes pacientes_pkey; Type: CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.pacientes
    ADD CONSTRAINT pacientes_pkey PRIMARY KEY (id);


--
-- Name: paises_iso paises_iso_codigo_iso3_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.paises_iso
    ADD CONSTRAINT paises_iso_codigo_iso3_key UNIQUE (codigo_iso3);


--
-- Name: paises_iso paises_iso_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.paises_iso
    ADD CONSTRAINT paises_iso_pkey PRIMARY KEY (id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- Name: municipios unique_codigo; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT unique_codigo UNIQUE (codigo);


--
-- Name: idx_codigo; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX idx_codigo ON public.municipios USING btree (codigo);


--
-- Name: idx_consultas_ciclo_gin; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_ciclo_gin ON public.consultas USING gin (ciclo);


--
-- Name: idx_consultas_especialidad_servicio; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_especialidad_servicio ON public.consultas USING btree (especialidad, servicio);


--
-- Name: idx_consultas_expediente; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_expediente ON public.consultas USING btree (expediente);


--
-- Name: idx_consultas_fecha_consulta; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_fecha_consulta ON public.consultas USING btree (fecha_consulta);


--
-- Name: idx_consultas_indicadores_gin; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_indicadores_gin ON public.consultas USING gin (indicadores);


--
-- Name: idx_consultas_paciente_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_paciente_id ON public.consultas USING btree (paciente_id);


--
-- Name: idx_consultas_tipo_fecha; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_consultas_tipo_fecha ON public.consultas USING btree (tipo_consulta, fecha_consulta);


--
-- Name: idx_contacto_telefono; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_contacto_telefono ON public.pacientes USING btree (((contacto ->> 'telefono'::text)));


--
-- Name: idx_creado_en; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_creado_en ON public.pacientes USING btree (creado_en);


--
-- Name: idx_datos_extra_gin; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_datos_extra_gin ON public.pacientes USING gin (datos_extra);


--
-- Name: idx_estado; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_estado ON public.pacientes USING btree (estado);


--
-- Name: idx_eventos_consulta_consulta_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_eventos_consulta_consulta_id ON public.eventos_consulta USING btree (consulta_id);


--
-- Name: idx_eventos_consulta_datos_gin; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_eventos_consulta_datos_gin ON public.eventos_consulta USING gin (datos);


--
-- Name: idx_eventos_consulta_estado; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_eventos_consulta_estado ON public.eventos_consulta USING btree (estado);


--
-- Name: idx_eventos_consulta_responsable_gin; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_eventos_consulta_responsable_gin ON public.eventos_consulta USING gin (responsable);


--
-- Name: idx_eventos_consulta_tipo_evento; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_eventos_consulta_tipo_evento ON public.eventos_consulta USING btree (tipo_evento);


--
-- Name: idx_fecha_nacimiento; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_fecha_nacimiento ON public.pacientes USING btree (fecha_nacimiento);


--
-- Name: idx_medicos_activo; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_medicos_activo ON public.medicos USING btree (activo);


--
-- Name: idx_medicos_colegiado; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_medicos_colegiado ON public.medicos USING btree (colegiado);


--
-- Name: idx_medicos_dpi; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_medicos_dpi ON public.medicos USING btree (dpi);


--
-- Name: idx_medicos_especialidad; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_medicos_especialidad ON public.medicos USING btree (especialidad);


--
-- Name: idx_medicos_nombre; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_medicos_nombre ON public.medicos USING btree (nombre);


--
-- Name: idx_nombre_apellido1; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_nombre_apellido1 ON public.pacientes USING btree (((nombre ->> 'apellido_primero'::text)));


--
-- Name: idx_nombre_completo_trgm; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_nombre_completo_trgm ON public.pacientes USING gin (nombre_completo public.gin_trgm_ops);


--
-- Name: idx_nombre_primer; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_nombre_primer ON public.pacientes USING btree (((nombre ->> 'primer'::text)));


--
-- Name: idx_paciente_nombre_json; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_paciente_nombre_json ON public.pacientes USING gin (nombre jsonb_path_ops);


--
-- Name: idx_pacientes_contacto; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_pacientes_contacto ON public.pacientes USING gin (contacto);


--
-- Name: idx_pacientes_datos_extra; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_pacientes_datos_extra ON public.pacientes USING gin (datos_extra);


--
-- Name: idx_pacientes_estado; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_pacientes_estado ON public.pacientes USING btree (estado);


--
-- Name: idx_pacientes_fecha_nacimiento; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_pacientes_fecha_nacimiento ON public.pacientes USING btree (fecha_nacimiento);


--
-- Name: idx_pacientes_nombre; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_pacientes_nombre ON public.pacientes USING gin (nombre);


--
-- Name: idx_pacientes_referencias; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_pacientes_referencias ON public.pacientes USING gin (referencias);


--
-- Name: idx_referencias_gin; Type: INDEX; Schema: public; Owner: macbookairm2
--

CREATE INDEX idx_referencias_gin ON public.pacientes USING gin (referencias);


--
-- Name: pacientes trg_set_nombre_completo; Type: TRIGGER; Schema: public; Owner: macbookairm2
--

CREATE TRIGGER trg_set_nombre_completo BEFORE INSERT OR UPDATE ON public.pacientes FOR EACH ROW EXECUTE FUNCTION public.actualizar_nombre_completo();


--
-- Name: constancia_nacimiento fk_constancia_medico; Type: FK CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento
    ADD CONSTRAINT fk_constancia_medico FOREIGN KEY (medico_id) REFERENCES public.medicos(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: constancia_nacimiento fk_constancia_paciente; Type: FK CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento
    ADD CONSTRAINT fk_constancia_paciente FOREIGN KEY (paciente_id) REFERENCES public.pacientes(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: constancia_nacimiento fk_constancia_registrador; Type: FK CONSTRAINT; Schema: public; Owner: macbookairm2
--

ALTER TABLE ONLY public.constancia_nacimiento
    ADD CONSTRAINT fk_constancia_registrador FOREIGN KEY (registrador_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict bAu8JTvlRRbXDRqhNfZhrc8ENmMHaTEs0t8vBGnukniP6mebxOpFuegdbi1xQTM

