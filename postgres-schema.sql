--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.6
-- Dumped by pg_dump version 9.6.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: sensor_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA sensor_data;


ALTER SCHEMA sensor_data OWNER TO postgres;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: jsonb_merge_data(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.jsonb_merge_data() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
NEW.data = coalesce(OLD.data || NEW.data);
RETURN NEW;
END
$$;


ALTER FUNCTION public.jsonb_merge_data() OWNER TO postgres;

--
-- Name: update_stats(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_stats() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
IF NEW.data ?& array['to_qty', 'to_qty_unit', 'to_inventory_id'] THEN
	UPDATE inventories SET stats = jsonb_set(coalesce(stats, '{}'), ARRAY[NEW.data->>'to_qty_unit'], to_jsonb(coalesce(jsonb_extract_path_text(coalesce(stats, '{}'), NEW.data->>'to_qty_unit')::numeric, 0) + jsonb_extract_path_text(NEW.data, 'to_qty')::numeric))
	WHERE id = (NEW.data->>'to_inventory_id')::bigint;
END IF;
IF NEW.data ?& array['from_qty', 'from_qty_unit', 'from_inventory_id'] THEN
	UPDATE inventories SET stats = jsonb_set(coalesce(stats, '{}'), ARRAY[NEW.data->>'from_qty_unit'], to_jsonb(coalesce(jsonb_extract_path_text(coalesce(stats, '{}'), NEW.data->>'from_qty_unit')::numeric, 0) - jsonb_extract_path_text(NEW.data, 'from_qty')::numeric))
	WHERE id = (NEW.data->>'from_inventory_id')::bigint;
END IF;
IF NEW.data ?& array['to_stage', 'inventory_id'] THEN
	UPDATE inventories SET attributes = jsonb_set(coalesce(attributes, '{}'), ARRAY['stage'], to_jsonb(NEW.data->>'to_stage') )
	WHERE id = (NEW.data->>'inventory_id')::bigint;
END IF;
IF NEW.data ?& array['to_room', 'inventory_id'] THEN
	UPDATE inventories SET attributes = jsonb_set(coalesce(attributes, '{}'), ARRAY['room'], to_jsonb(NEW.data->>'to_room') )
	WHERE id = (NEW.data->>'inventory_id')::bigint;
END IF;
IF NEW.data ?& array['quarantined', 'inventory_id'] THEN
	UPDATE inventories SET attributes = jsonb_set(coalesce(attributes, '{}'), ARRAY['quarantined'], to_jsonb(NEW.data->>'quarantined') )
	WHERE id = (NEW.data->>'inventory_id')::bigint;
END IF;
RETURN NEW;
END
$$;


ALTER FUNCTION public.update_stats() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    data jsonb NOT NULL
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activities_id_seq OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.id;


--
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    external_id character varying,
    stats jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_id_seq OWNER TO postgres;

--
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- Name: inventories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventories (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    variety character varying NOT NULL,
    data jsonb,
    stats jsonb DEFAULT '{}'::jsonb,
    attributes jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE public.inventories OWNER TO postgres;

--
-- Name: inventories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventories_id_seq OWNER TO postgres;

--
-- Name: inventories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventories_id_seq OWNED BY public.inventories.id;


--
-- Name: organizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organizations (
    name character varying NOT NULL,
    id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb
);


ALTER TABLE public.organizations OWNER TO postgres;

--
-- Name: organizations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organizations_id_seq OWNER TO postgres;

--
-- Name: organizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organizations_id_seq OWNED BY public.organizations.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    name character varying NOT NULL,
    permissions jsonb NOT NULL,
    data jsonb,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    name character varying NOT NULL,
    data jsonb,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rooms_id_seq OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rules (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    description character varying,
    activity character varying NOT NULL,
    conditions jsonb NOT NULL,
    data jsonb
);


ALTER TABLE public.rules OWNER TO postgres;

--
-- Name: rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rules_id_seq OWNER TO postgres;

--
-- Name: rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rules_id_seq OWNED BY public.rules.id;


--
-- Name: taxonomies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxonomies (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    data jsonb
);


ALTER TABLE public.taxonomies OWNER TO postgres;

--
-- Name: taxonomies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taxonomies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxonomies_id_seq OWNER TO postgres;

--
-- Name: taxonomies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.taxonomies_id_seq OWNED BY public.taxonomies.id;


--
-- Name: taxonomy_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxonomy_options (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    data jsonb,
    taxonomy_id integer NOT NULL
);


ALTER TABLE public.taxonomy_options OWNER TO postgres;

--
-- Name: taxonomy_options_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taxonomy_options_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxonomy_options_id_seq OWNER TO postgres;

--
-- Name: taxonomy_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.taxonomy_options_id_seq OWNED BY public.taxonomy_options.id;


--
-- Name: uploads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.uploads (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    name character varying NOT NULL,
    content_type character varying NOT NULL,
    upload_exists boolean DEFAULT false NOT NULL,
    data jsonb,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.uploads OWNER TO postgres;

--
-- Name: uploads_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.uploads_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uploads_id_seq OWNER TO postgres;

--
-- Name: uploads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.uploads_id_seq OWNED BY public.uploads.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying NOT NULL,
    organization_id integer NOT NULL,
    auth0_id character varying,
    role_id integer,
    enabled boolean NOT NULL,
    created_by integer,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: sensors; Type: TABLE; Schema: sensor_data; Owner: postgres
--

CREATE TABLE sensor_data.sensors (
    id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    database_id integer NOT NULL,
    external_id character varying NOT NULL,
    organization_id integer NOT NULL
);


ALTER TABLE sensor_data.sensors OWNER TO postgres;

--
-- Name: sensors_id_seq; Type: SEQUENCE; Schema: sensor_data; Owner: postgres
--

CREATE SEQUENCE sensor_data.sensors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sensor_data.sensors_id_seq OWNER TO postgres;

--
-- Name: sensors_id_seq; Type: SEQUENCE OWNED BY; Schema: sensor_data; Owner: postgres
--

ALTER SEQUENCE sensor_data.sensors_id_seq OWNED BY sensor_data.sensors.id;


--
-- Name: activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- Name: inventories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories ALTER COLUMN id SET DEFAULT nextval('public.inventories_id_seq'::regclass);


--
-- Name: organizations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations ALTER COLUMN id SET DEFAULT nextval('public.organizations_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: rules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules ALTER COLUMN id SET DEFAULT nextval('public.rules_id_seq'::regclass);


--
-- Name: taxonomies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies ALTER COLUMN id SET DEFAULT nextval('public.taxonomies_id_seq'::regclass);


--
-- Name: taxonomy_options id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options ALTER COLUMN id SET DEFAULT nextval('public.taxonomy_options_id_seq'::regclass);


--
-- Name: uploads id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads ALTER COLUMN id SET DEFAULT nextval('public.uploads_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: sensors id; Type: DEFAULT; Schema: sensor_data; Owner: postgres
--

ALTER TABLE ONLY sensor_data.sensors ALTER COLUMN id SET DEFAULT nextval('sensor_data.sensors_id_seq'::regclass);


--
-- Data for Name: activities; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.activities VALUES (2, 1, 1, '2018-06-25 14:42:59.379427+00', 'receive_inventory', '{"brand": "asdfasf", "strain": "Hybrid", "to_qty": 5000, "variety": "testy2", "substance": "fresh", "upload_id": 2, "description": "lkjlkj", "to_qty_unit": "seeds", "intended_use": "lkjlkj", "date_received": "2018-06-25", "to_inventory_id": 2, "proof_of_purchase": "receipt-2018.png", "received_at_address": "kjhkjh", "received_from_person": "asdfasdf"}');
INSERT INTO public.activities VALUES (3, 1, 3, '2018-06-25 14:43:45.651795+00', 'create_batch', '{"strain": "Hybrid", "variety": "testy2", "inventory_id": 3}');
INSERT INTO public.activities VALUES (4, 1, 3, '2018-06-25 14:48:38.055148+00', 'propagate_seeds', '{"to_qty": 100, "from_qty": 100, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 3, "from_inventory_id": 2}');
INSERT INTO public.activities VALUES (5, 1, 7, '2018-06-28 19:26:12.504195+00', 'germinate_seeds', '{"to_qty": 1, "from_qty": 1, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "3", "from_inventory_id": "3"}');
INSERT INTO public.activities VALUES (6, 1, 1, '2018-06-29 14:34:33.520768+00', 'receive_inventory', '{"brand": "asfasdf", "strain": "Hybrid", "to_qty": 5000, "variety": "Animal Cookies", "substance": "fresh", "upload_id": 3, "description": "asdfasdf", "to_qty_unit": "seeds", "intended_use": "asdfasdf", "date_received": "2018-06-29", "to_inventory_id": 4, "proof_of_purchase": "receipt-2018.png", "received_at_address": "kjhkjhlkjh", "received_from_person": "asdfasdf"}');
INSERT INTO public.activities VALUES (7, 1, 1, '2018-06-29 14:35:08.175731+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 5}');
INSERT INTO public.activities VALUES (8, 1, 1, '2018-06-29 14:35:44.651588+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 6}');
INSERT INTO public.activities VALUES (9, 1, 1, '2018-06-29 14:36:08.356896+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 7}');
INSERT INTO public.activities VALUES (10, 1, 1, '2018-06-29 14:36:08.582017+00', 'propagate_seeds', '{"to_qty": 200, "from_qty": 200, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 7, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (11, 1, 1, '2018-06-29 14:36:24.910045+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 8, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (12, 1, 1, '2018-06-29 14:37:57.199732+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 9, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (13, 1, 1, '2018-06-29 14:41:11.354999+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 10, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (14, 1, 1, '2018-06-29 14:42:02.530672+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 11, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (15, 1, 1, '2018-06-29 14:42:45.177767+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 12, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (16, 1, 1, '2018-06-29 14:43:17.316243+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 13, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (17, 1, 7, '2018-06-29 14:47:14.236892+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 14}');
INSERT INTO public.activities VALUES (18, 1, 1, '2018-06-29 14:48:35.087696+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 15, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (19, 1, 1, '2018-06-29 14:48:59.948665+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 16, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (20, 1, 1, '2018-06-29 14:49:01.224277+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 17, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (21, 1, 7, '2018-06-29 14:51:05.116463+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 18}');
INSERT INTO public.activities VALUES (22, 1, 7, '2018-06-29 14:52:11.417656+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 19}');
INSERT INTO public.activities VALUES (23, 1, 7, '2018-06-29 14:52:38.23916+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 20}');
INSERT INTO public.activities VALUES (24, 1, 1, '2018-06-29 14:53:56.175007+00', 'update_rule', '{"rule_id": "5", "rule_data": {"id": "5", "name": "Propagate Cuttings", "activity": "propagate_cuttings", "timestamp": "2018-06-21T10:27:59.964378-04:00", "conditions": [{"field": "to_qty_unit", "regex": "plants", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "[1-9]\\d*", "condition_type": "data_validation"}, {"match_fields": [{"match": "variety", "comparison": "="}], "condition_type": "inventory_compare", "first_inventory_id_field": "to_inventory_id", "second_inventory_id_field": "from_inventory_id"}, {"qty_unit": "to_qty_unit", "qty_value": "source_count", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (25, 1, 7, '2018-06-29 14:54:11.287227+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 21}');
INSERT INTO public.activities VALUES (26, 1, 1, '2018-06-29 14:54:29.89714+00', 'update_rule', '{"rule_id": "5", "rule_data": {"id": "5", "name": "Propagate Cuttings", "activity": "propagate_cuttings", "timestamp": "2018-06-21T10:27:59.964378-04:00", "conditions": [{"field": "to_qty_unit", "regex": "plants", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "[1-9]\\d*", "condition_type": "data_validation"}, {"match_fields": [{"match": "variety", "comparison": "="}], "condition_type": "inventory_compare", "first_inventory_id_field": "to_inventory_id", "second_inventory_id_field": "from_inventory_id"}, {"qty_unit": "to_qty_unit", "qty_value": "source_count", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (27, 1, 1, '2018-06-29 14:56:17.115169+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 22}');
INSERT INTO public.activities VALUES (28, 1, 7, '2018-06-29 14:58:44.105539+00', 'germinate_seeds', '{"to_qty": 1, "from_qty": 1, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "9", "from_inventory_id": "9"}');
INSERT INTO public.activities VALUES (29, 1, 7, '2018-06-29 14:59:57.262547+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 23}');
INSERT INTO public.activities VALUES (36, 1, 1, '2018-06-29 15:05:12.24959+00', 'lab_result_received', '{"lab_result": "fail", "inventory_id": "23", "lab_sample_sent_activity_id": "33"}');
INSERT INTO public.activities VALUES (30, 1, 7, '2018-06-29 14:59:57.365531+00', 'propagate_cuttings', '{"to_qty": 10, "to_qty_unit": "plants", "source_count": 1, "to_inventory_id": 23, "from_inventory_id": "9"}');
INSERT INTO public.activities VALUES (32, 1, 1, '2018-06-29 15:01:21.921394+00', 'complete_drying', '{"to_qty": 1800, "from_qty": 10000, "to_qty_unit": "g-dry", "from_qty_unit": "g-wet", "to_inventory_id": "23", "from_inventory_id": "23"}');
INSERT INTO public.activities VALUES (34, 1, 1, '2018-06-29 15:01:36.144423+00', 'lab_result_received', '{"lab_result": "pass", "inventory_id": "23", "lab_sample_sent_activity_id": "33"}');
INSERT INTO public.activities VALUES (40, 1, 7, '2018-06-29 15:11:10.93355+00', 'propagate_seeds', '{"to_qty": 100, "from_qty": 100, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 26, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (31, 1, 1, '2018-06-29 15:00:56.909961+00', 'harvest_plants', '{"to_qty": 10000, "from_qty": 10, "to_qty_unit": "g-wet", "from_qty_unit": "plants", "to_inventory_id": "23", "from_inventory_id": "23"}');
INSERT INTO public.activities VALUES (33, 1, 1, '2018-06-29 15:01:29.954208+00', 'lab_sample_sent', '{"from_qty": 80, "from_qty_unit": "g-dry", "from_inventory_id": "23"}');
INSERT INTO public.activities VALUES (35, 1, 1, '2018-06-29 15:04:00.642987+00', 'lab_result_received', '{"lab_result": "pass", "inventory_id": "23", "lab_sample_sent_activity_id": "33"}');
INSERT INTO public.activities VALUES (38, 1, 7, '2018-06-29 15:10:05.21415+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 25}');
INSERT INTO public.activities VALUES (41, 1, 7, '2018-06-29 17:52:34.411824+00', 'harvest_plants', '{"to_qty": 1000, "from_qty": 1, "to_qty_unit": "g-wet", "from_qty_unit": "plants", "to_inventory_id": "3", "from_inventory_id": "3"}');
INSERT INTO public.activities VALUES (42, 1, 7, '2018-06-29 17:59:59.540059+00', 'complete_oil_extraction', '{"to_qty": 1000, "from_qty": 1000, "to_qty_unit": "ml", "from_qty_unit": "g-wet", "to_inventory_id": "3", "from_inventory_id": "3"}');
INSERT INTO public.activities VALUES (37, 1, 7, '2018-06-29 15:06:18.739183+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 24}');
INSERT INTO public.activities VALUES (39, 1, 7, '2018-06-29 15:11:10.820688+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 26}');
INSERT INTO public.activities VALUES (43, 1, 7, '2018-07-03 14:19:59.536049+00', 'destroy_material', '{"from_qty": 1, "destroyed_qty": 100, "from_qty_unit": "seeds", "witness_name_1": "dsf", "witness_name_2": "asd", "from_inventory_id": "2", "destroyed_qty_unit": "g", "destroyed_at_location": "daddaf", "witness_qualification_1": "asd", "witness_qualification_2": "arwe"}');
INSERT INTO public.activities VALUES (44, 1, 1, '2018-07-03 14:51:43.263492+00', 'germinate_seeds', '{"to_qty": 1, "from_qty": 1, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "3", "from_inventory_id": "3"}');
INSERT INTO public.activities VALUES (45, 1, 1, '2018-07-03 14:52:01.97319+00', 'harvest_plants', '{"to_qty": 2000, "from_qty": 1, "to_qty_unit": "g-wet", "from_qty_unit": "plants", "to_inventory_id": "3", "from_inventory_id": "3"}');
INSERT INTO public.activities VALUES (46, 1, 1, '2018-07-03 14:52:28.238424+00', 'complete_oil_extraction', '{"to_qty": 50, "from_qty": 2000, "to_qty_unit": "ml", "from_qty_unit": "g-wet", "to_inventory_id": "3", "from_inventory_id": "3"}');
INSERT INTO public.activities VALUES (47, 1, 7, '2018-07-03 15:08:21.17522+00', 'germinate_seeds', '{"to_qty": 1, "from_qty": 1, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "7", "from_inventory_id": "7"}');
INSERT INTO public.activities VALUES (48, 1, 1, '2018-07-03 15:44:27.403467+00', 'germinate_seeds', '{"to_qty": 1, "from_qty": 1, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "15", "from_inventory_id": "15"}');
INSERT INTO public.activities VALUES (49, 1, 1, '2018-07-03 15:54:59.101461+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 27}');
INSERT INTO public.activities VALUES (50, 1, 1, '2018-07-03 15:54:59.300931+00', 'propagate_cuttings', '{"to_qty": 100, "to_qty_unit": "plants", "source_count": 1, "to_inventory_id": 27, "from_inventory_id": "9"}');
INSERT INTO public.activities VALUES (51, 1, 1, '2018-07-03 15:55:26.420493+00', 'harvest_plants', '{"to_qty": 8000, "from_qty": 100, "to_qty_unit": "g-wet", "from_qty_unit": "plants", "to_inventory_id": "27", "from_inventory_id": "27"}');
INSERT INTO public.activities VALUES (52, 1, 7, '2018-07-03 16:03:49.030199+00', 'create_mother', '{"strain": "Hybrid", "to_qty": 1, "variety": "Animal Cookies", "from_qty": 1, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 28, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (53, 1, 1, '2018-07-03 17:37:12.648616+00', 'germinate_seeds', '{"to_qty": 50, "from_qty": 50, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "7", "from_inventory_id": "7"}');
INSERT INTO public.activities VALUES (54, 1, 1, '2018-07-03 17:38:57.223635+00', 'destroy_material', '{"from_qty": 5, "destroyed_qty": 500, "from_qty_unit": "plants", "witness_name_1": "Dan", "witness_name_2": "Daniel", "from_inventory_id": "7", "destroyed_qty_unit": "g", "destroyed_at_location": "grow-room-1", "witness_qualification_1": "PIC", "witness_qualification_2": "PIC"}');
INSERT INTO public.activities VALUES (55, 1, 1, '2018-07-03 17:40:05.218047+00', 'harvest_plants', '{"to_qty": 4600, "from_qty": 46, "to_qty_unit": "g-wet", "from_qty_unit": "plants", "to_inventory_id": "7", "from_inventory_id": "7"}');
INSERT INTO public.activities VALUES (56, 1, 1, '2018-07-03 17:40:21.839079+00', 'destroy_material', '{"from_qty": 149, "destroyed_qty": 1, "from_qty_unit": "seeds", "witness_name_1": "1", "witness_name_2": "1", "from_inventory_id": "7", "destroyed_qty_unit": "g", "destroyed_at_location": "1", "witness_qualification_1": "1", "witness_qualification_2": "1"}');
INSERT INTO public.activities VALUES (57, 1, 1, '2018-07-03 17:41:23.048071+00', 'destroy_material', '{"from_qty": 3000, "destroyed_qty": 3000, "from_qty_unit": "g-wet", "witness_name_1": "D", "witness_name_2": "D", "from_inventory_id": "7", "destroyed_qty_unit": "g", "destroyed_at_location": "room2", "witness_qualification_1": "D", "witness_qualification_2": "D"}');
INSERT INTO public.activities VALUES (58, 1, 1, '2018-07-03 17:42:14.778942+00', 'complete_drying', '{"to_qty": 300, "from_qty": 1600, "to_qty_unit": "g-dry", "from_qty_unit": "g-wet", "to_inventory_id": "7", "from_inventory_id": "7"}');
INSERT INTO public.activities VALUES (59, 1, 1, '2018-07-03 17:42:45.86502+00', 'lab_sample_sent', '{"from_qty": 140, "from_qty_unit": "g-dry", "from_inventory_id": "7"}');
INSERT INTO public.activities VALUES (60, 1, 1, '2018-07-03 17:43:01.054579+00', 'lab_result_received', '{"lab_result": "pass", "inventory_id": "7", "lab_sample_sent_activity_id": "59"}');
INSERT INTO public.activities VALUES (61, 1, 1, '2018-07-03 17:43:24.233003+00', 'lab_result_received', '{"lab_result": "fail", "inventory_id": "7", "lab_sample_sent_activity_id": "59"}');
INSERT INTO public.activities VALUES (62, 1, 1, '2018-07-03 17:50:49.067597+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 29}');
INSERT INTO public.activities VALUES (63, 1, 1, '2018-07-03 17:50:49.192935+00', 'propagate_seeds', '{"to_qty": 500, "from_qty": 500, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 29, "from_inventory_id": "4"}');
INSERT INTO public.activities VALUES (64, 1, 1, '2018-07-03 17:51:57.674878+00', 'germinate_seeds', '{"to_qty": 200, "from_qty": 200, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "29", "from_inventory_id": "29"}');
INSERT INTO public.activities VALUES (65, 1, 3, '2018-07-03 19:40:03.844447+00', 'propagate_seeds', '{"to_qty": 100, "from_qty": 100, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": 3, "from_inventory_id": 2}');
INSERT INTO public.activities VALUES (66, 1, 7, '2018-07-03 20:45:20.729083+00', 'propagate_seeds', '{"to_qty": 100, "from_qty": 100, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": "3", "from_inventory_id": "2"}');
INSERT INTO public.activities VALUES (67, 1, 7, '2018-07-03 20:49:31.254026+00', 'propagate_seeds', '{"to_qty": 99, "from_qty": 99, "to_qty_unit": "seeds", "from_qty_unit": "seeds", "to_inventory_id": "3", "from_inventory_id": "2"}');
INSERT INTO public.activities VALUES (68, 1, 3, '2018-07-05 15:21:26.903122+00', 'create_equipment', '{"equipment_id": 1, "equipment_data": {"name": "Humidity - 407752", "type": "sensor", "sensor_id": "407752", "created_by": 3, "application": "Humidity", "organization_id": "1", "firmware_version": "10.22.10.5"}}');
INSERT INTO public.activities VALUES (69, 1, 1, '2018-07-05 18:43:19.699116+00', 'germinate_seeds', '{"to_qty": 1, "from_qty": 1, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "28", "from_inventory_id": "28"}');
INSERT INTO public.activities VALUES (70, 1, 1, '2018-07-05 19:57:42.057968+00', 'update_rule', '{"rule_id": "8", "rule_data": {"id": "8", "name": "Destroy material", "activity": "destroy_material", "timestamp": "2018-06-21T14:27:59.964378+00:00", "conditions": [{"field": "destroyed_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"field": "destroyed_qty_unit", "regex": "g", "condition_type": "data_validation"}, {"field": "destroyed_at_location", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_name_1", "regex": "[\\w\\-,@.\\s]+", "condition_type": "data_validation"}, {"field": "witness_qualification_1", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_name_2", "regex": "[\\w\\-@,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_qualification_2", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}, {"field": "from_qty", "conditions": [{"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}], "condition_type": "conditional_has_field"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (71, 1, 1, '2018-07-05 19:58:02.553876+00', 'destroy_material', '{"from_qty": 10, "destroyed_qty": 10, "from_qty_unit": "g-dry", "witness_name_1": "andrew.wilson@wilcompute.com", "witness_name_2": "aneesa.guerra.khan@wilcompute.com", "from_inventory_id": "23", "destroyed_qty_unit": "g", "destroyed_at_location": "Drying room", "witness_qualification_1": 1, "witness_qualification_2": 1}');
INSERT INTO public.activities VALUES (73, 1, 1, '2018-07-06 13:01:48.433365+00', 'destroy_material', '{"from_qty": 10, "destroyed_qty": 10, "from_qty_unit": "g-wet", "witness_name_1": "daniel.favand@wilcompute.com", "witness_name_2": "aneesa.guerra.khan@wilcompute.com", "from_inventory_id": "27", "destroyed_qty_unit": "g", "destroyed_at_location": "Drying room", "witness_qualification_1": 1, "witness_qualification_2": 1}');
INSERT INTO public.activities VALUES (75, 1, 3, '2018-07-09 14:10:30.303182+00', 'create_rule', '{"rule_id": 15, "rule_data": {"name": "custom-rule", "activity": "receive_inventory", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}], "created_by": 3, "description": "Rules about intake", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (72, 1, 6, '2018-07-05 19:58:24.974691+00', 'lab_sample_sent', '{"from_qty": 20, "from_qty_unit": "g-dry", "from_inventory_id": "23"}');
INSERT INTO public.activities VALUES (74, 1, 1, '2018-07-06 13:02:38.464499+00', 'destroy_material', '{"from_qty": 10, "destroyed_qty": 10, "from_qty_unit": "g-wet", "witness_name_1": "daniel.kain@wilcompute.com", "witness_name_2": "hareen.peiris@wilcompute.com", "from_inventory_id": "27", "destroyed_qty_unit": "g", "destroyed_at_location": "Drying room", "witness_qualification_1": "admin", "witness_qualification_2": "admin"}');
INSERT INTO public.activities VALUES (76, 1, 3, '2018-07-10 13:28:35.291898+00', 'create_rule', '{"rule_id": 16, "rule_data": {"name": "Queue for destruction", "activity": "queue_for_destruction", "conditions": [{"field": "from_qty", "conditions": [{"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}], "condition_type": "conditional_has_field"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}, {"field": "type_of_waste", "match": "name", "taxonomy_name": "waste_types", "condition_type": "taxonomy_validation"}, {"field": "reason_for_destruction", "match": "name", "taxonomy_name": "destruction_reasons", "condition_type": "taxonomy_validation"}, {"field": "destroyed_qty", "regex": "\\d+\\.?\\d*", "condition_type": "data_validation"}, {"field": "destroyed_qty_unit", "regex": "g", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "collected_from", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (77, 1, 1, '2018-07-10 15:44:10.910141+00', 'update_rule', '{"rule_id": "8", "rule_data": {"id": "8", "name": "Destroy material", "activity": "destroy_material", "timestamp": "2018-06-21T10:27:59.964378-04:00", "conditions": [{"field": "witness_1", "regex": "[\\w\\-,@.\\s]+", "condition_type": "data_validation"}, {"field": "witness_1_role", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_2", "regex": "[\\w\\-@,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_2_role", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (78, 1, 3, '2018-07-10 15:56:58.390971+00', 'create_rule', '{"rule_id": 17, "rule_data": {"name": "Queue for destruction", "activity": "complete_destruction", "conditions": [{"match_fields": [{"field": "destroyed_qty_unit", "match": "destroyed_qty_unit"}, {"match": "name", "regex": "queue_for_destruction"}], "condition_type": "activity_match", "activity_id_field": "queue_destruction_activity_id"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (79, 1, 7, '2018-07-11 17:59:38.078739+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 100, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 1000, "from_qty_unit": "seeds", "type_of_waste": "stems", "collected_from": {"id": "1", "name": "Main Room", "zone": "zone-1", "timestamp": "2018-06-25T19:02:31.276110+00:00", "created_by": 1, "description": "Small room in the back corner", "organization_id": 1}, "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (80, 1, 7, '2018-07-11 18:06:57.656774+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 10, "checked_by": "shila.regmi.atreya@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 1000, "from_qty_unit": "seeds", "type_of_waste": "leaves", "collected_from": "Drying room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (81, 1, 7, '2018-07-11 18:11:16.10253+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 10, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 100000, "from_qty_unit": "plants", "type_of_waste": "leaves", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (82, 1, 7, '2018-07-11 18:14:01.077413+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 100, "checked_by": "shila.regmi.atreya@wilcompute.com", "weighed_by": "daniel.kain@wilcompute.com", "destroyed_qty": 2000, "from_qty_unit": "g-wet", "type_of_waste": "leaves", "collected_from": "Main Room", "from_inventory_id": "27", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (83, 1, 7, '2018-07-11 18:21:38.104102+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 200, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": 100, "from_qty_unit": "g-dry", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "23", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (84, 1, 7, '2018-07-11 21:10:41.076441+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 22, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 2000, "from_qty_unit": "plants", "type_of_waste": "leaves", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (85, 1, 7, '2018-07-11 21:17:05.547098+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 0, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 444, "from_qty_unit": "plants", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (86, 1, 3, '2018-07-11 21:29:30.474576+00', 'update_rule', '{"rule_id": "16", "rule_data": {"id": "16", "name": "Queue for destruction", "activity": "queue_for_destruction", "timestamp": "2018-07-10T13:28:35.291898+00:00", "conditions": [{"field": "from_qty", "conditions": [{"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}], "condition_type": "conditional_has_field"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}, {"field": "type_of_waste", "match": "name", "taxonomy_name": "waste_types", "condition_type": "taxonomy_validation"}, {"field": "reason_for_destruction", "match": "name", "taxonomy_name": "destruction_reasons", "condition_type": "taxonomy_validation"}, {"field": "destroyed_qty", "regex": "\\d+\\.?\\d*", "condition_type": "data_validation"}, {"field": "destroyed_qty_unit", "regex": "g", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "collected_from", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (87, 1, 3, '2018-07-11 21:30:45.191448+00', 'queue_for_destruction', '{"variety": "Mango Kush", "checked_by": "Chad", "weighed_by": "Andrew", "destroyed_qty": "1", "type_of_waste": "stems", "collected_from": "Room 101", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (90, 1, 1, '2018-07-11 23:15:08.5527+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 6, "checked_by": "andrew.wilson@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 100, "from_qty_unit": "seeds", "type_of_waste": "leaves", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (88, 1, 7, '2018-07-11 21:33:55.523821+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.favand@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "destroyed_qty": 4545, "type_of_waste": "stems", "collected_from": "Drying room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (92, 1, 7, '2018-07-12 15:04:53.474293+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 44, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 55757, "from_qty_unit": "seeds", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (93, 1, 7, '2018-07-12 17:57:37.332821+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 1, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 6000, "from_qty_unit": "plants", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (89, 1, 7, '2018-07-11 21:46:26.945115+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 7777, "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (91, 1, 7, '2018-07-12 14:45:22.122992+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "andrew.wilson@wilcompute.com", "weighed_by": "hareen.peiris@wilcompute.com", "destroyed_qty": 22, "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (94, 1, 3, '2018-07-13 13:39:02.110686+00', 'destroy_material', '{"witness_1": "Dario", "witness_2": "Shila", "witness_1_role": "PIC", "witness_2_role": "QA", "destruction_timestamp": "2018-07-10T15:24:50.927Z", "method_of_destruction": "Kitty litter", "completed_queue_destruction_activities": [{"destroyed_qty": 6000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "93"}]}');
INSERT INTO public.activities VALUES (95, 1, 3, '2018-07-13 13:39:02.110686+00', 'complete_destruction', '{"witness_1": "Dario", "witness_2": "Shila", "destroyed_qty": 6000, "witness_1_role": "PIC", "witness_2_role": "QA", "destroyed_qty_unit": "g", "destruction_timestamp": "2018-07-10T15:24:50.927Z", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "94", "queue_destruction_activity_id": "93"}');
INSERT INTO public.activities VALUES (96, 1, 3, '2018-07-13 13:45:46.1595+00', 'destroy_material', '{"witness_1": "Dario", "witness_2": "Shila", "witness_1_role": "PIC", "witness_2_role": "QA", "destruction_timestamp": "2018-07-10T15:24:50.927Z", "method_of_destruction": "Kitty litter", "completed_queue_destruction_activities": [{"destroyed_qty": 2000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "82"}]}');
INSERT INTO public.activities VALUES (97, 1, 3, '2018-07-13 13:45:46.1595+00', 'complete_destruction', '{"witness_1": "Dario", "witness_2": "Shila", "destroyed_qty": 2000, "witness_1_role": "PIC", "witness_2_role": "QA", "destroyed_qty_unit": "g", "destruction_timestamp": "2018-07-10T15:24:50.927Z", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "96", "queue_destruction_activity_id": "82"}');
INSERT INTO public.activities VALUES (98, 1, 7, '2018-07-13 13:50:30.192413+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 100, "checked_by": "andrew.wilson@wilcompute.com", "weighed_by": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": 5008, "from_qty_unit": "g-dry", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "23", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (99, 1, 7, '2018-07-16 04:17:18.698179+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Test!", "completed_queue_destruction_activities": [{"destroyed_qty": 1000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "79"}]}');
INSERT INTO public.activities VALUES (100, 1, 7, '2018-07-16 04:17:18.698179+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 1000, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Test!", "destroy_material_activity_id": "99", "queue_destruction_activity_id": "79"}');
INSERT INTO public.activities VALUES (101, 1, 7, '2018-07-16 13:31:48.274303+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "leaves", "completed_queue_destruction_activities": [{"destroyed_qty": 1000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "80"}]}');
INSERT INTO public.activities VALUES (102, 1, 7, '2018-07-16 13:31:48.274303+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 1000, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "leaves", "destroy_material_activity_id": "101", "queue_destruction_activity_id": "80"}');
INSERT INTO public.activities VALUES (103, 1, 7, '2018-07-16 13:32:51.480278+00', 'destroy_material', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Test!", "completed_queue_destruction_activities": [{"destroyed_qty": 5008, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "98"}]}');
INSERT INTO public.activities VALUES (104, 1, 7, '2018-07-16 13:32:51.480278+00', 'complete_destruction', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 5008, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Test!", "destroy_material_activity_id": "103", "queue_destruction_activity_id": "98"}');
INSERT INTO public.activities VALUES (105, 1, 7, '2018-07-16 14:14:55.616484+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 444, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "85"}]}');
INSERT INTO public.activities VALUES (106, 1, 7, '2018-07-16 14:14:55.616484+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": 444, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "105", "queue_destruction_activity_id": "85"}');
INSERT INTO public.activities VALUES (107, 1, 7, '2018-07-16 14:17:34.102769+00', 'destroy_material', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "leaves", "completed_queue_destruction_activities": [{"destroyed_qty": "1", "destroyed_qty_unit": "g", "queue_destruction_activity_id": "87"}]}');
INSERT INTO public.activities VALUES (108, 1, 7, '2018-07-16 14:17:34.102769+00', 'complete_destruction', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": "1", "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "leaves", "destroy_material_activity_id": "107", "queue_destruction_activity_id": "87"}');
INSERT INTO public.activities VALUES (109, 1, 5, '2018-07-16 14:24:28.282495+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 2, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "tests+s2s-dev@wilcompute.com", "destroyed_qty": 15, "from_qty_unit": "plants", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (110, 1, 7, '2018-07-16 14:31:19.139635+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 100, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "90"}]}');
INSERT INTO public.activities VALUES (229, 1, 3, '2018-08-01 21:58:28.300613+00', 'update_stage', '{"to_stage": "received-approved", "inventory_id": "33"}');
INSERT INTO public.activities VALUES (231, 1, 3, '2018-08-01 22:00:10.606255+00', 'update_stage', '{"to_stage": "drying", "inventory_id": "31"}');
INSERT INTO public.activities VALUES (111, 1, 7, '2018-07-16 14:31:19.139635+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 100, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "110", "queue_destruction_activity_id": "90"}');
INSERT INTO public.activities VALUES (112, 1, 7, '2018-07-16 14:36:36.878039+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "daniel.favand@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 4545, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "88"}]}');
INSERT INTO public.activities VALUES (113, 1, 7, '2018-07-16 14:36:36.878039+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "daniel.favand@wilcompute.com", "destroyed_qty": 4545, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "112", "queue_destruction_activity_id": "88"}');
INSERT INTO public.activities VALUES (114, 1, 7, '2018-07-16 14:48:10.199931+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Kitty litter", "completed_queue_destruction_activities": [{"destroyed_qty": 22, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "91"}, {"destroyed_qty": 55757, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "92"}]}');
INSERT INTO public.activities VALUES (115, 1, 7, '2018-07-16 14:48:10.199931+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 22, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "114", "queue_destruction_activity_id": "91"}');
INSERT INTO public.activities VALUES (116, 1, 7, '2018-07-16 14:48:10.199931+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 55757, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "114", "queue_destruction_activity_id": "92"}');
INSERT INTO public.activities VALUES (119, 1, 7, '2018-07-16 14:57:02.582384+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 100000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "81"}]}');
INSERT INTO public.activities VALUES (120, 1, 7, '2018-07-16 14:57:02.582384+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 100000, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "119", "queue_destruction_activity_id": "81"}');
INSERT INTO public.activities VALUES (121, 1, 7, '2018-07-16 16:00:35.006275+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Kitty litter", "completed_queue_destruction_activities": [{"destroyed_qty": 2000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "84"}]}');
INSERT INTO public.activities VALUES (122, 1, 7, '2018-07-16 16:00:35.006275+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 2000, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "121", "queue_destruction_activity_id": "84"}');
INSERT INTO public.activities VALUES (123, 1, 7, '2018-07-16 20:07:40.370724+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 3, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 5666, "from_qty_unit": "seeds", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "26", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (127, 1, 7, '2018-07-16 20:10:42.676303+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 66, "checked_by": "andrew.wilson@wilcompute.com", "weighed_by": "daniel.kain@wilcompute.com", "destroyed_qty": 7676, "from_qty_unit": "g-wet", "type_of_waste": "stems", "collected_from": "Drying room", "from_inventory_id": "27", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (128, 1, 7, '2018-07-16 20:58:00.801402+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 5666, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "123"}]}');
INSERT INTO public.activities VALUES (129, 1, 7, '2018-07-16 20:58:00.801402+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 5666, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "128", "queue_destruction_activity_id": "123"}');
INSERT INTO public.activities VALUES (130, 1, 1, '2018-07-17 12:37:48.650378+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 7676, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "127"}]}');
INSERT INTO public.activities VALUES (131, 1, 1, '2018-07-17 12:37:48.650378+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 7676, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "130", "queue_destruction_activity_id": "127"}');
INSERT INTO public.activities VALUES (133, 1, 7, '2018-07-17 14:24:11.932401+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 55, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 6000, "from_qty_unit": "g-wet", "type_of_waste": "leaves", "collected_from": "Drying room", "from_inventory_id": "27", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (135, 1, 7, '2018-07-17 16:09:32.635845+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 5, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "132"}, {"destroyed_qty": 3000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "134"}, {"destroyed_qty": 6000, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "133"}]}');
INSERT INTO public.activities VALUES (230, 1, 3, '2018-08-01 22:00:06.872099+00', 'update_stage', '{"to_stage": "flowering", "inventory_id": "31"}');
INSERT INTO public.activities VALUES (233, 1, 3, '2018-08-01 22:03:22.762194+00', 'update_stage', '{"to_stage": "received-approved", "inventory_id": "30"}');
INSERT INTO public.activities VALUES (117, 1, 7, '2018-07-16 14:55:03.673655+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 15, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "109"}]}');
INSERT INTO public.activities VALUES (118, 1, 7, '2018-07-16 14:55:03.673655+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 15, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "117", "queue_destruction_activity_id": "109"}');
INSERT INTO public.activities VALUES (124, 1, 7, '2018-07-16 20:08:15.916597+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 7777, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "89"}, {"destroyed_qty": 100, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "83"}]}');
INSERT INTO public.activities VALUES (125, 1, 7, '2018-07-16 20:08:15.916597+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": 7777, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "124", "queue_destruction_activity_id": "89"}');
INSERT INTO public.activities VALUES (126, 1, 7, '2018-07-16 20:08:15.916597+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": 100, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "124", "queue_destruction_activity_id": "83"}');
INSERT INTO public.activities VALUES (132, 1, 1, '2018-07-17 12:38:34.266622+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 1, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 5, "from_qty_unit": "seeds", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (134, 1, 7, '2018-07-17 14:24:51.701437+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 66, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "daniel.kain@wilcompute.com", "destroyed_qty": 3000, "from_qty_unit": "g-dry", "type_of_waste": "leaves", "collected_from": "Drying room", "from_inventory_id": "23", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (140, 1, 7, '2018-07-17 16:51:34.026921+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 1, "checked_by": "andrew.wilson@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 400, "from_qty_unit": "plants", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (142, 1, 7, '2018-07-17 21:57:25.726117+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "andrew.wilson@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 777, "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (136, 1, 7, '2018-07-17 16:09:32.635845+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 5, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "135", "queue_destruction_activity_id": "132"}');
INSERT INTO public.activities VALUES (137, 1, 7, '2018-07-17 16:09:32.635845+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 3000, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "135", "queue_destruction_activity_id": "134"}');
INSERT INTO public.activities VALUES (138, 1, 7, '2018-07-17 16:09:32.635845+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 6000, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "135", "queue_destruction_activity_id": "133"}');
INSERT INTO public.activities VALUES (141, 1, 7, '2018-07-17 21:57:08.266829+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 8, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 88, "from_qty_unit": "seeds", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "29", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (143, 1, 7, '2018-07-17 22:12:24.576424+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Test!", "completed_queue_destruction_activities": [{"destroyed_qty": 400, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "140"}]}');
INSERT INTO public.activities VALUES (144, 1, 7, '2018-07-17 22:12:24.576424+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 400, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Test!", "destroy_material_activity_id": "143", "queue_destruction_activity_id": "140"}');
INSERT INTO public.activities VALUES (145, 1, 7, '2018-07-18 15:31:20.584277+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 88, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 87, "from_qty_unit": "g-wet", "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "27", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (146, 1, 7, '2018-07-18 15:32:22.086201+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.favand@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "destroyed_qty": 55, "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (147, 1, 7, '2018-07-18 15:38:37.451773+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 555, "type_of_waste": "stems", "collected_from": "Main Room", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (148, 1, 7, '2018-07-18 15:41:10.775406+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 88, "checked_by": "daniel.favand@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 567567, "from_qty_unit": "g-wet", "type_of_waste": "leaves", "collected_from": "Main Room", "from_inventory_id": "27", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (149, 1, 7, '2018-07-18 18:03:29.193998+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 88, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "141"}]}');
INSERT INTO public.activities VALUES (150, 1, 7, '2018-07-18 18:03:29.193998+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 88, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "149", "queue_destruction_activity_id": "141"}');
INSERT INTO public.activities VALUES (151, 1, 3, '2018-07-18 20:58:51.371442+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Drying room", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (152, 1, 1, '2018-07-19 13:36:55.104351+00', 'destroy_material', '{"witness_1": "andrew.wilson@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 55, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "146"}]}');
INSERT INTO public.activities VALUES (153, 1, 1, '2018-07-19 13:36:55.104351+00', 'complete_destruction', '{"witness_1": "andrew.wilson@wilcompute.com", "witness_2": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 55, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "152", "queue_destruction_activity_id": "146"}');
INSERT INTO public.activities VALUES (154, 1, 1, '2018-07-19 13:37:30.237769+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 777, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "142"}]}');
INSERT INTO public.activities VALUES (155, 1, 1, '2018-07-19 13:37:30.237769+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 777, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "154", "queue_destruction_activity_id": "142"}');
INSERT INTO public.activities VALUES (156, 1, 3, '2018-07-20 14:49:01.349641+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "shila.regmi.atreya@wilcompute.com", "weighed_by": "daniel.kain@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Propagation Room", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (157, 1, 1, '2018-07-23 15:46:55.485763+00', 'create_equipment', '{"equipment_id": 2, "equipment_data": {"name": "Test Printer", "type": "printer", "location": "", "ipAddress": "192.168.2.17", "created_by": 1, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (158, 1, 1, '2018-07-23 15:54:49.935913+00', 'create_equipment', '{"equipment_id": 3, "equipment_data": {"name": "fake printer", "type": "printer", "location": "", "ipAddress": "123.123.123.123", "created_by": 1, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (159, 1, 1, '2018-07-23 15:58:23.318994+00', 'create_equipment', '{"equipment_id": 4, "equipment_data": {"name": "the Real Fake printer", "type": "printer", "location": "", "ipAddress": "111.111.111.111", "created_by": 1, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (160, 1, 1, '2018-07-23 15:58:49.52929+00', 'update_equipment', '{"equipment_id": "3", "equipment_data": {"name": "fake printer", "type": "printer", "location": "", "ipAddress": "123.123.123.124", "created_by": 1, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (161, 1, 7, '2018-07-23 19:54:56.87695+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": "1", "destroyed_qty_unit": "g", "queue_destruction_activity_id": "156"}]}');
INSERT INTO public.activities VALUES (162, 1, 7, '2018-07-23 19:54:56.87695+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": "1", "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "161", "queue_destruction_activity_id": "156"}');
INSERT INTO public.activities VALUES (167, 1, 3, '2018-07-24 15:34:38.773526+00', 'create_rule', '{"rule_id": 18, "rule_data": {"name": "Stage Update", "activity": "update_stage", "conditions": [{"field": "to_stage", "condition_type": "stage_validation", "inventory_id_field": "inventory_id"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (163, 1, 7, '2018-07-23 20:19:56.515756+00', 'destroy_material', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": "1", "destroyed_qty_unit": "g", "queue_destruction_activity_id": "151"}, {"destroyed_qty": 567567, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "148"}, {"destroyed_qty": 555, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "147"}]}');
INSERT INTO public.activities VALUES (164, 1, 7, '2018-07-23 20:19:56.515756+00', 'complete_destruction', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": "1", "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "163", "queue_destruction_activity_id": "151"}');
INSERT INTO public.activities VALUES (165, 1, 7, '2018-07-23 20:19:56.515756+00', 'complete_destruction', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 567567, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "163", "queue_destruction_activity_id": "148"}');
INSERT INTO public.activities VALUES (166, 1, 7, '2018-07-23 20:19:56.515756+00', 'complete_destruction', '{"witness_1": "aneesa.guerra.khan@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 555, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "163", "queue_destruction_activity_id": "147"}');
INSERT INTO public.activities VALUES (168, 1, 3, '2018-07-24 15:37:14.40348+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (169, 1, 3, '2018-07-24 15:44:00.416701+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (170, 1, 3, '2018-07-24 15:48:47.014132+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (171, 1, 3, '2018-07-24 15:50:57.28856+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (172, 1, 3, '2018-07-24 15:58:30.971615+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (173, 1, 3, '2018-07-24 16:01:10.915211+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (174, 1, 7, '2018-07-24 16:04:16.251998+00', 'receive_inventory', '{"brand": "Any", "strain": "Hybrid", "to_qty": 100, "variety": "Agent Orange", "substance": "fresh", "upload_id": 4, "description": "sell", "to_qty_unit": "plants", "intended_use": "grow", "date_received": "2018-07-24", "to_inventory_id": 30, "proof_of_purchase": "Adobe Acrobat PDF Files111.pdf", "received_at_address": "scarborough", "received_from_person": "test"}');
INSERT INTO public.activities VALUES (175, 1, 3, '2018-07-24 16:04:53.905473+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (176, 1, 7, '2018-07-24 16:05:11.162452+00', 'queue_for_destruction', '{"variety": "Agent Orange", "from_qty": 1, "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 1000, "from_qty_unit": "plants", "type_of_waste": "stems", "collected_from": "Quarantine Room", "from_inventory_id": "30", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (177, 1, 3, '2018-07-24 16:06:04.058348+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (178, 1, 3, '2018-07-24 16:25:57.459329+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (179, 1, 3, '2018-07-24 16:28:42.272918+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "daniel.kain@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (180, 1, 5, '2018-07-24 17:43:09.94612+00', 'update_equipment', '{"equipment_id": "4", "equipment_data": {"name": "the Real Fake printer tested", "type": "printer", "location": "", "ipAddress": "111.111.111.111", "created_by": 5, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (181, 1, 1, '2018-07-25 15:52:05.285167+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 31}');
INSERT INTO public.activities VALUES (182, 1, 1, '2018-07-25 15:52:05.478662+00', 'propagate_cuttings', '{"to_qty": 60, "to_qty_unit": "plants", "source_count": 1, "to_inventory_id": 31, "from_inventory_id": "28"}');
INSERT INTO public.activities VALUES (183, 1, 1, '2018-07-25 15:52:05.759589+00', 'propagate_cuttings', '{"to_qty": 60, "to_qty_unit": "plants", "source_count": 1, "to_inventory_id": 31, "from_inventory_id": "15"}');
INSERT INTO public.activities VALUES (184, 1, 3, '2018-07-25 16:47:45.764893+00', 'update_stage', '{"to_stage": "propagation", "inventory_id": 31}');
INSERT INTO public.activities VALUES (187, 1, 1, '2018-07-25 18:19:07.811957+00', 'propagate_cuttings', '{"to_qty": 100, "to_qty_unit": "plants", "source_count": 1, "to_inventory_id": "31", "from_inventory_id": "28"}');
INSERT INTO public.activities VALUES (188, 1, 1, '2018-07-25 19:00:49.724142+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 10, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "destroyed_qty": 10, "from_qty_unit": "plants", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "31", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (189, 1, 3, '2018-07-25 19:02:33.569021+00', 'update_stage', '{"to_stage": "vegetation", "inventory_id": 31}');
INSERT INTO public.activities VALUES (190, 1, 1, '2018-07-25 19:03:38.344855+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 10, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "destroyed_qty": 10, "from_qty_unit": "plants", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "31", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (191, 1, 3, '2018-07-26 15:29:00.826454+00', 'create_rule', '{"rule_id": 19, "rule_data": {"name": "Release Receive Inventory", "activity": "release_received_inventory", "conditions": [{"field": "to_stage", "condition_field": "quarantined", "inventory_id_field": "inventory_id"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (192, 1, 1, '2018-07-26 15:37:17.526425+00', 'destroy_material', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Kitty litter", "completed_queue_destruction_activities": [{"destroyed_qty": 87, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "145"}]}');
INSERT INTO public.activities VALUES (193, 1, 1, '2018-07-26 15:37:17.526425+00', 'complete_destruction', '{"witness_1": "daniel.favand@wilcompute.com", "witness_2": "daniel.kain@wilcompute.com", "destroyed_qty": 87, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "192", "queue_destruction_activity_id": "145"}');
INSERT INTO public.activities VALUES (232, 1, 3, '2018-08-01 22:03:19.8073+00', 'update_stage', '{"to_stage": "received-unapproved", "inventory_id": "30"}');
INSERT INTO public.activities VALUES (194, 1, 3, '2018-07-26 15:55:09.627534+00', 'update_rule', '{"rule_id": "19", "rule_data": {"name": "Release Receive Inventory", "activity": "release_received_inventory", "conditions": [{"field": "to_stage", "condition_type": "stage_validation", "inventory_id_field": "inventory_id"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (197, 1, 1, '2018-07-26 17:39:20.185324+00', 'update_stage', '{"to_stage": "propagation", "inventory_id": "26"}');
INSERT INTO public.activities VALUES (201, 1, 1, '2018-07-26 19:46:23.84988+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[A-Za-z0-9_]", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stage", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (213, 1, 7, '2018-07-27 21:17:12.040566+00', 'receive_inventory', '{"po": "6455", "to_qty": 18, "variety": "Candyland", "to_stage": "received-unapproved", "upload_id": 22, "checked_by": "tests+s2s-dev@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "quarantined": "true", "to_qty_unit": "g-dry", "vendor_name": "cartels", "intended_use": "propagation", "inventory_id": 37, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 37, "number_of_pieces": 10, "vendor_lot_number": "asdasd", "damage_to_shipment": "wefwe", "delivery_matches_po": true, "net_weight_received": 66}');
INSERT INTO public.activities VALUES (195, 1, 3, '2018-07-26 17:36:27.058707+00', 'update_rule', '{"rule_id": "19", "rule_data": {"name": "Release Receive Inventory", "activity": "release_received_inventory", "conditions": [{"field": "to_stage", "condition_type": "stage_validation", "inventory_id_field": "inventory_id"}, {"field": "quarantined", "regex": "~*''false''", "condition_type": "data_validation"}], "created_by": 3, "description": "", "organization_id": "1"}}');
INSERT INTO public.activities VALUES (196, 1, 1, '2018-07-26 17:38:53.023892+00', 'update_stage', '{"to_stage": "seedling", "inventory_id": "26"}');
INSERT INTO public.activities VALUES (198, 1, 1, '2018-07-26 17:39:31.46555+00', 'germinate_seeds', '{"to_qty": 97, "from_qty": 97, "to_qty_unit": "plants", "from_qty_unit": "seeds", "to_inventory_id": "26", "from_inventory_id": "26"}');
INSERT INTO public.activities VALUES (199, 1, 1, '2018-07-26 18:45:09.849482+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "received_at_address", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}, {"field": "date_received", "regex": "(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "brand", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "description", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "strain", "match": "name", "taxonomy_name": "strains", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (200, 1, 1, '2018-07-26 19:45:37.522653+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "date_received", "regex": "(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[A-Za-z0-9_]", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stage", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (202, 1, 1, '2018-07-27 13:47:11.532719+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[A-Za-z0-9_]", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stage", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (203, 1, 1, '2018-07-27 13:48:37.367664+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[A-Za-z0-9]", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stage", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (234, 1, 3, '2018-08-01 22:11:38.968774+00', 'update_stage', '{"to_stage": "seedling", "inventory_id": "40"}');
INSERT INTO public.activities VALUES (235, 1, 3, '2018-08-01 22:11:42.570914+00', 'update_stage', '{"to_stage": "propagation", "inventory_id": "40"}');
INSERT INTO public.activities VALUES (204, 1, 1, '2018-07-27 13:49:38.55986+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[A-Za-z0-9]+", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stage", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (205, 1, 1, '2018-07-27 13:51:58.555464+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stage", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (206, 1, 1, '2018-07-27 13:54:40.488696+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "damage_to_shipment", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stages", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (207, 1, 7, '2018-07-27 13:54:47.201475+00', 'receive_inventory', '{"po": "34343", "to_qty": 17, "variety": "Lamb''s Bread", "to_stage": "received-unapproved", "upload_id": 16, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "quarantined": "true", "to_qty_unit": "plants", "vendor_name": "sfsdf", "intended_use": "hhasdasd", "inventory_id": 32, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 32, "number_of_pieces": 18, "vendor_lot_number": "sdsf5656", "damage_to_shipment": "no", "delivery_matches_po": "true", "net_weight_received": 22}');
INSERT INTO public.activities VALUES (209, 1, 7, '2018-07-27 14:52:23.655446+00', 'receive_inventory', '{"po": "234234", "to_qty": 100, "variety": "Hindu Kush", "to_stage": "received-unapproved", "upload_id": 18, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "daniel.kain@wilcompute.com", "quarantined": "true", "to_qty_unit": "plants", "vendor_name": "cdel", "intended_use": "donnn", "inventory_id": 34, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 34, "number_of_pieces": 7, "vendor_lot_number": "46456gfh", "damage_to_shipment": "no", "delivery_matches_po": "true", "net_weight_received": 23423}');
INSERT INTO public.activities VALUES (210, 1, 7, '2018-07-27 17:54:20.634411+00', 'receive_inventory', '{"po": "555", "to_qty": 10, "variety": "Strawberry Cough", "to_stage": "received-unapproved", "upload_id": 19, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "quarantined": "true", "to_qty_unit": "g-wet", "vendor_name": "dsgsd34345", "intended_use": "asdasd", "inventory_id": 35, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 35, "number_of_pieces": 55, "vendor_lot_number": "retert", "damage_to_shipment": "asdasd", "delivery_matches_po": "true", "net_weight_received": 555}');
INSERT INTO public.activities VALUES (208, 1, 7, '2018-07-27 14:47:57.056362+00', 'receive_inventory', '{"po": "4343", "to_qty": 10, "variety": "Tangie", "to_stage": "received-unapproved", "upload_id": 17, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "quarantined": "true", "to_qty_unit": "plants", "vendor_name": "dfgdf", "intended_use": "dont know", "inventory_id": 33, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 33, "number_of_pieces": 22, "vendor_lot_number": "sse4545", "damage_to_shipment": "asdasd", "delivery_matches_po": "false", "net_weight_received": 55}');
INSERT INTO public.activities VALUES (211, 1, 1, '2018-07-27 21:04:27.502367+00', 'update_rule', '{"rule_id": "1", "rule_data": {"id": "1", "name": "Intake", "activity": "receive_inventory", "timestamp": "2018-06-21T14:23:25.257445+00:00", "conditions": [{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stages", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}], "created_by": 1, "description": null, "organization_id": "1"}}');
INSERT INTO public.activities VALUES (212, 1, 7, '2018-07-27 21:04:41.171409+00', 'receive_inventory', '{"po": "sdsdf", "to_qty": 18, "variety": "Lamb''s Bread", "to_stage": "received-unapproved", "upload_id": 21, "checked_by": "daniel.favand@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "quarantined": "true", "to_qty_unit": "seeds", "vendor_name": "asdasd", "intended_use": "asdasd", "inventory_id": 36, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 36, "number_of_pieces": 19, "vendor_lot_number": "asdasd", "damage_to_shipment": "", "delivery_matches_po": false, "net_weight_received": 6666}');
INSERT INTO public.activities VALUES (214, 1, 7, '2018-07-30 13:55:09.324057+00', 'receive_inventory', '{"po": "qweqwe", "to_qty": 17, "variety": "Lamb''s Bread", "to_stage": "received-unapproved", "upload_id": 23, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "quarantined": "true", "to_qty_unit": "seeds", "vendor_name": "qweqwe", "intended_use": "rtyrt", "inventory_id": 38, "documentation": "Adobe Acrobat PDF Files111.pdf", "to_inventory_id": 38, "number_of_pieces": 166, "vendor_lot_number": "asdasd", "damage_to_shipment": "", "delivery_matches_po": true, "net_weight_received": 555}');
INSERT INTO public.activities VALUES (215, 1, 1, '2018-07-30 14:11:02.531814+00', 'receive_inventory', '{"po": "ABC-123", "to_qty": 1000, "variety": "Candyland", "to_stage": "received-unapproved", "upload_id": 24, "checked_by": "shila.regmi.atreya@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "quarantined": "true", "to_qty_unit": "plants", "vendor_name": "YES Co", "intended_use": "Propagation", "inventory_id": 39, "documentation": "receipt-2018.png", "to_inventory_id": 39, "number_of_pieces": 23, "vendor_lot_number": "XYZ098", "damage_to_shipment": "", "delivery_matches_po": true, "net_weight_received": 100}');
INSERT INTO public.activities VALUES (216, 1, 7, '2018-07-30 14:24:57.698275+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "william.buttenham@wilcompute.com", "weighed_by": "aneesa.guerra.khan@wilcompute.com", "destroyed_qty": 1, "type_of_waste": "stems", "collected_from": "Grow Bay 2", "from_inventory_id": "26", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (217, 1, 7, '2018-07-30 15:22:04.592532+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 1, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "216"}]}');
INSERT INTO public.activities VALUES (218, 1, 7, '2018-07-30 15:22:04.592532+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "shila.regmi.atreya@wilcompute.com", "destroyed_qty": 1, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "217", "queue_destruction_activity_id": "216"}');
INSERT INTO public.activities VALUES (219, 1, 7, '2018-07-30 18:23:48.808954+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 1, "checked_by": "hareen.peiris@wilcompute.com", "weighed_by": "daniel.favand@wilcompute.com", "destroyed_qty": 5656, "from_qty_unit": "plants", "type_of_waste": "stems", "collected_from": "Grow Bay 2", "from_inventory_id": "26", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (220, 1, 3, '2018-07-31 16:41:20.283044+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "tests+s2s-dev@wilcompute.com", "weighed_by": "daniel.kain@wilcompute.com", "destroyed_qty": "1", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "28", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (221, 1, 7, '2018-07-31 18:43:55.558549+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 40}');
INSERT INTO public.activities VALUES (222, 1, 7, '2018-07-31 18:44:51.619451+00', 'create_batch', '{"strain": "Hybrid", "variety": "Animal Cookies", "inventory_id": 41}');
INSERT INTO public.activities VALUES (223, 1, 7, '2018-07-31 18:44:51.855895+00', 'propagate_cuttings', '{"to_qty": 11, "to_qty_unit": "plants", "source_count": 1, "to_inventory_id": 41, "from_inventory_id": "15"}');
INSERT INTO public.activities VALUES (224, 1, 1, '2018-08-01 13:24:09.8414+00', 'update_stage', '{"to_stage": "vegetation", "inventory_id": "26"}');
INSERT INTO public.activities VALUES (225, 1, 1, '2018-08-01 13:42:56.638668+00', 'update_stage', '{"to_stage": "propagation", "inventory_id": "23"}');
INSERT INTO public.activities VALUES (226, 1, 3, '2018-08-01 20:00:05.258253+00', 'destroy_material', '{"witness_1": "william.buttenham@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Kitty litter", "completed_queue_destruction_activities": [{"destroyed_qty": 10, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "188"}]}');
INSERT INTO public.activities VALUES (227, 1, 3, '2018-08-01 20:00:05.258253+00', 'complete_destruction', '{"witness_1": "william.buttenham@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 10, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Kitty litter", "destroy_material_activity_id": "226", "queue_destruction_activity_id": "188"}');
INSERT INTO public.activities VALUES (228, 1, 3, '2018-08-01 21:56:08.455954+00', 'update_stage', '{"to_stage": "test stage", "inventory_id": "28"}');
INSERT INTO public.activities VALUES (236, 1, 3, '2018-08-01 22:11:44.483055+00', 'update_stage', '{"to_stage": "vegetation", "inventory_id": "40"}');
INSERT INTO public.activities VALUES (238, 1, 3, '2018-08-01 22:11:47.610991+00', 'update_stage', '{"to_stage": "drying", "inventory_id": "40"}');
INSERT INTO public.activities VALUES (237, 1, 3, '2018-08-01 22:11:45.800334+00', 'update_stage', '{"to_stage": "flowering", "inventory_id": "40"}');
INSERT INTO public.activities VALUES (239, 1, 1, '2018-08-02 12:51:56.426037+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "from_qty": 1, "checked_by": "aneesa.guerra.khan@wilcompute.com", "weighed_by": "andrew.wilson@wilcompute.com", "destroyed_qty": 50, "from_qty_unit": "plants", "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "31", "destroyed_qty_unit": "g", "reason_for_destruction": "Harvest trimmings"}');
INSERT INTO public.activities VALUES (240, 1, 1, '2018-08-02 12:57:56.876652+00', 'update_stage', '{"to_stage": "propagation", "inventory_id": "41"}');
INSERT INTO public.activities VALUES (241, 1, 1, '2018-08-02 12:58:44.690784+00', 'queue_for_destruction', '{"variety": "Animal Cookies", "checked_by": "william.buttenham@wilcompute.com", "weighed_by": "hareen.peiris@wilcompute.com", "destroyed_qty": 123, "type_of_waste": "leaves", "collected_from": "Grow Bay 1", "from_inventory_id": "41", "destroyed_qty_unit": "g", "reason_for_destruction": "Daily sweep"}');
INSERT INTO public.activities VALUES (242, 1, 3, '2018-08-02 14:12:53.752843+00', 'destroy_material', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "witness_1_role": "admin", "witness_2_role": "admin", "method_of_destruction": "Shredding", "completed_queue_destruction_activities": [{"destroyed_qty": 10, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "190"}, {"destroyed_qty": 50, "destroyed_qty_unit": "g", "queue_destruction_activity_id": "239"}]}');
INSERT INTO public.activities VALUES (243, 1, 3, '2018-08-02 14:12:53.752843+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 10, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "242", "queue_destruction_activity_id": "190"}');
INSERT INTO public.activities VALUES (244, 1, 3, '2018-08-02 14:12:53.752843+00', 'complete_destruction', '{"witness_1": "daniel.kain@wilcompute.com", "witness_2": "hareen.peiris@wilcompute.com", "destroyed_qty": 50, "witness_1_role": "admin", "witness_2_role": "admin", "destroyed_qty_unit": "g", "method_of_destruction": "Shredding", "destroy_material_activity_id": "242", "queue_destruction_activity_id": "239"}');


--
-- Name: activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.activities_id_seq', 244, true);


--
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.equipment VALUES (1, 1, 3, 'Humidity - 407752', 'sensor', '{"sensor_id": "407752", "application": "Humidity", "firmware_version": "10.22.10.5"}', '2018-07-05 15:21:26.903122+00', NULL, '{}');
INSERT INTO public.equipment VALUES (2, 1, 1, 'Test Printer', 'printer', '{"location": "", "ipAddress": "192.168.2.17"}', '2018-07-23 15:46:55.485763+00', NULL, '{}');
INSERT INTO public.equipment VALUES (3, 1, 1, 'fake printer', 'printer', '{"location": "", "ipAddress": "123.123.123.124"}', '2018-07-23 15:54:49.935913+00', NULL, '{}');
INSERT INTO public.equipment VALUES (4, 1, 5, 'the Real Fake printer tested', 'printer', '{"location": "", "ipAddress": "111.111.111.111"}', '2018-07-23 15:58:23.318994+00', NULL, '{}');


--
-- Name: equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_id_seq', 4, true);


--
-- Data for Name: inventories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.inventories VALUES (5, 1, 1, '2018-06-29 14:35:08.175731+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (6, 1, 1, '2018-06-29 14:35:44.651588+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (7, 1, 1, '2018-06-29 14:36:08.356896+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"g-dry": 160, "g-wet": 0, "seeds": 0, "plants": 0}', '{}');
INSERT INTO public.inventories VALUES (8, 1, 1, '2018-06-29 14:36:24.910045+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (4, 1, 1, '2018-06-29 14:34:33.520768+00', 'Hybrid Animal Cookies seeds', 'received inventory', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 4190}', '{}');
INSERT INTO public.inventories VALUES (10, 1, 1, '2018-06-29 14:41:11.354999+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (11, 1, 1, '2018-06-29 14:42:02.530672+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (3, 1, 3, '2018-06-25 14:43:45.651795+00', '2018-26-testy2', 'batch', 'testy2', '{"strain": "Hybrid"}', '{"ml": 1050, "g-wet": 0, "seeds": 397, "plants": 0}', '{}');
INSERT INTO public.inventories VALUES (2, 1, 1, '2018-06-25 14:42:59.379427+00', 'Hybrid testy2 seeds', 'received inventory', 'testy2', '{"strain": "Hybrid"}', '{"seeds": 4600}', '{}');
INSERT INTO public.inventories VALUES (12, 1, 1, '2018-06-29 14:42:45.177767+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (13, 1, 1, '2018-06-29 14:43:17.316243+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (14, 1, 7, '2018-06-29 14:47:14.236892+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (16, 1, 1, '2018-06-29 14:48:59.948665+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (17, 1, 1, '2018-06-29 14:49:01.224277+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 1}', '{}');
INSERT INTO public.inventories VALUES (18, 1, 7, '2018-06-29 14:51:05.116463+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (19, 1, 7, '2018-06-29 14:52:11.417656+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (21, 1, 7, '2018-06-29 14:54:11.287227+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (22, 1, 1, '2018-06-29 14:56:17.115169+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (9, 1, 1, '2018-06-29 14:37:57.199732+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 0, "plants": 1}', '{}');
INSERT INTO public.inventories VALUES (24, 1, 7, '2018-06-29 15:06:18.739183+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{}');
INSERT INTO public.inventories VALUES (15, 1, 1, '2018-06-29 14:48:35.087696+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 0, "plants": 1}', '{}');
INSERT INTO public.inventories VALUES (32, 1, 7, '2018-07-27 13:54:47.201475+00', 'Lamb''s Bread plants', 'received inventory', 'Lamb''s Bread', '{}', '{"plants": 17}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (34, 1, 7, '2018-07-27 14:52:23.655446+00', 'Hindu Kush plants', 'received inventory', 'Hindu Kush', '{}', '{"plants": 100}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (35, 1, 7, '2018-07-27 17:54:20.634411+00', 'Strawberry Cough g-wet', 'received inventory', 'Strawberry Cough', '{}', '{"g-wet": 10}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (36, 1, 7, '2018-07-27 21:04:41.171409+00', 'Lamb''s Bread seeds', 'received inventory', 'Lamb''s Bread', '{}', '{"seeds": 18}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (37, 1, 7, '2018-07-27 21:17:12.040566+00', 'Candyland g-dry', 'received inventory', 'Candyland', '{}', '{"g-dry": 18}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (38, 1, 7, '2018-07-30 13:55:09.324057+00', 'Lamb''s Bread seeds', 'received inventory', 'Lamb''s Bread', '{}', '{"seeds": 17}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (39, 1, 1, '2018-07-30 14:11:02.531814+00', 'Candyland plants', 'received inventory', 'Candyland', '{}', '{"plants": 1000}', '{"stage": "received-unapproved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (23, 1, 7, '2018-06-29 14:59:57.262547+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"g-dry": 1324, "g-wet": 0, "plants": 0}', '{"stage": "propagation"}');
INSERT INTO public.inventories VALUES (26, 1, 7, '2018-06-29 15:11:10.820688+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 0, "plants": 96}', '{"room": "Grow Bay 1", "stage": "vegetation"}');
INSERT INTO public.inventories VALUES (27, 1, 1, '2018-07-03 15:54:59.101461+00', '2018-27-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"g-wet": 7583, "plants": 0}', '{"room": "Vault 1"}');
INSERT INTO public.inventories VALUES (29, 1, 1, '2018-07-03 17:50:49.067597+00', '2018-27-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 131, "plants": 164}', '{"room": "Quarantine Room", "stage": "vegetation"}');
INSERT INTO public.inventories VALUES (20, 1, 7, '2018-06-29 14:52:38.23916+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{"room": "Grow Bay 2"}');
INSERT INTO public.inventories VALUES (25, 1, 7, '2018-06-29 15:10:05.21415+00', '2018-26-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{"room": "Propagation Room"}');
INSERT INTO public.inventories VALUES (28, 1, 7, '2018-07-03 16:03:49.030199+00', 'Hybrid Animal Cookies Mother', 'mother', 'Animal Cookies', '{"strain": "Hybrid"}', '{"seeds": 0, "plants": 1}', '{"room": "Mothers Room", "stage": "test stage"}');
INSERT INTO public.inventories VALUES (33, 1, 7, '2018-07-27 14:47:57.056362+00', 'Tangie plants', 'received inventory', 'Tangie', '{}', '{"plants": 10}', '{"stage": "received-approved", "quarantined": "true"}');
INSERT INTO public.inventories VALUES (30, 1, 7, '2018-07-24 16:04:16.251998+00', 'Hybrid Agent Orange plants', 'received inventory', 'Agent Orange', '{"strain": "Hybrid"}', '{"plants": 99}', '{"stage": "received-approved"}');
INSERT INTO public.inventories VALUES (40, 1, 7, '2018-07-31 18:43:55.558549+00', '2018-31-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{}', '{"stage": "drying"}');
INSERT INTO public.inventories VALUES (31, 1, 1, '2018-07-25 15:52:05.285167+00', '2018-30-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"plants": 199}', '{"stage": "drying"}');
INSERT INTO public.inventories VALUES (41, 1, 7, '2018-07-31 18:44:51.619451+00', '2018-31-Animal Cookies', 'batch', 'Animal Cookies', '{"strain": "Hybrid"}', '{"plants": 11}', '{"stage": "propagation"}');


--
-- Name: inventories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventories_id_seq', 41, true);


--
-- Data for Name: organizations; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.organizations VALUES ('GrowerIQ', 1, '2018-06-21 14:10:21.72089+00', NULL);


--
-- Name: organizations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.organizations_id_seq', 1, true);


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.roles VALUES (1, 1, 'admin', '[{"object": "users", "methods": ["GET", "POST", "PATCH"]}, {"object": "equipment", "methods": ["GET", "POST", "PATCH"]}, {"object": "uploads", "methods": ["POST"]}, {"object": "clients", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxonomies", "methods": ["GET", "POST", "DELETE", "PATCH"]}, {"object": "taxonomy_options", "methods": ["GET", "POST", "DELETE", "PATCH"]}, {"object": "inventories", "methods": ["GET", "POST", "PATCH"]}, {"object": "products", "methods": ["GET", "POST", "PATCH"]}, {"object": "roles", "methods": ["GET", "POST", "DELETE", "PATCH"]}, {"object": "rooms", "methods": ["GET", "POST", "DELETE", "PATCH"]}, {"object": "rules", "methods": ["GET", "POST", "DELETE", "PATCH"]}, {"object": "labels", "methods": ["GET"]}, {"object": "activities", "methods": ["GET"]}, {"action": "receive_inventory"}, {"action": "create_batch"}, {"action": "transfer_inventory"}, {"action": "create_mother"}, {"action": "propagate_cuttings"}, {"action": "propagate_seeds"}, {"action": "germinate_seeds"}, {"action": "destroy_material"}, {"action": "harvest_plants"}, {"action": "complete_drying"}, {"action": "complete_oil_extraction"}, {"action": "admin_adjustment"}, {"action": "lab_sample_sent"}, {"action": "lab_result_received"}, {"action": "queue_for_destruction"}, {"action": "complete_destruction"}, {"action": "update_stage"}]', NULL, 1, '2018-06-21 14:19:32.87351+00');


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 2, true);


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.rooms VALUES (3, 1, 1, 'Propagation Room', '{"zone": "greenhouse", "description": ""}', '2018-07-04 15:21:05.018797+00');
INSERT INTO public.rooms VALUES (4, 1, 1, 'Mothers Room', '{"zone": "greenhouse", "description": ""}', '2018-07-19 16:26:15.37134+00');
INSERT INTO public.rooms VALUES (5, 1, 1, 'Grow Bay 1', '{"zone": "greenhouse", "description": ""}', '2018-07-19 16:26:25.432935+00');
INSERT INTO public.rooms VALUES (6, 1, 1, 'Grow Bay 2', '{"zone": "greenhouse", "description": ""}', '2018-07-19 16:26:34.084868+00');
INSERT INTO public.rooms VALUES (1, 1, 1, 'Quarantine Room', '{"zone": "warehouse", "description": ""}', '2018-06-25 19:02:31.27611+00');
INSERT INTO public.rooms VALUES (7, 1, 1, 'Vault 1', '{"zone": "warehouse", "description": ""}', '2018-07-19 16:27:18.978483+00');


--
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rooms_id_seq', 7, true);


--
-- Data for Name: rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.rules VALUES (2, 1, 1, '2018-06-21 14:27:59.964378+00', 'Create batch', NULL, 'create_batch', '[{"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}, {"field": "strain", "match": "name", "taxonomy_name": "strains", "condition_type": "taxonomy_validation"}]', NULL);
INSERT INTO public.rules VALUES (3, 1, 1, '2018-06-21 14:27:59.964378+00', 'Transfer inventory', NULL, 'transfer_inventory', '[{"match_fields": [{"field": "variety", "match": "variety"}, {"field": "strain", "match": "strain"}], "condition_type": "inventory_match", "inventory_id_field": "from_inventory_id"}, {"match_fields": [{"field": "variety", "match": "variety"}, {"field": "strain", "match": "strain"}], "condition_type": "inventory_match", "inventory_id_field": "to_inventory_id"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}]', NULL);
INSERT INTO public.rules VALUES (4, 1, 1, '2018-06-21 14:27:59.964378+00', 'Create mother', NULL, 'create_mother', '[{"field": "from_qty_unit", "regex": "(seeds|plants)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(seeds|plants)", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "1", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "1", "condition_type": "data_validation"}, {"field": "strain", "match": "name", "taxonomy_name": "strains", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}, {"match_fields": [{"field": "variety", "match": "variety"}, {"field": "strain", "match": "strain"}], "condition_type": "inventory_match", "inventory_id_field": "from_inventory_id"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}]', NULL);
INSERT INTO public.rules VALUES (7, 1, 1, '2018-06-21 14:27:59.964378+00', 'Germinate seeds', NULL, 'germinate_seeds', '[{"field": "to_qty_unit", "regex": "plants", "condition_type": "data_validation"}, {"field": "from_qty_unit", "regex": "seeds", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "\\d+", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "\\d+", "condition_type": "data_validation"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}, {"match_fields": [{"match": "type", "regex": "(batch|mother)"}], "condition_type": "inventory_match", "inventory_id_field": "to_inventory_id"}]', NULL);
INSERT INTO public.rules VALUES (9, 1, 1, '2018-06-21 14:27:59.964378+00', 'Harvest plants', NULL, 'harvest_plants', '[{"field": "to_qty_unit", "regex": "g-wet", "condition_type": "data_validation"}, {"field": "from_qty_unit", "regex": "plants", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "\\d+", "condition_type": "data_validation"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}, {"match_fields": [{"match": "type", "regex": "batch"}], "condition_type": "inventory_match", "inventory_id_field": "to_inventory_id"}]', NULL);
INSERT INTO public.rules VALUES (10, 1, 1, '2018-06-21 14:27:59.964378+00', 'Complete drying', NULL, 'complete_drying', '[{"field": "to_qty_unit", "regex": "g-dry", "condition_type": "data_validation"}, {"field": "from_qty_unit", "regex": "g-wet", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"operator": "=", "qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}, {"match_fields": [{"match": "type", "regex": "batch"}], "condition_type": "inventory_match", "inventory_id_field": "to_inventory_id"}]', NULL);
INSERT INTO public.rules VALUES (8, 1, 1, '2018-06-21 14:27:59.964378+00', 'Destroy material', NULL, 'destroy_material', '[{"field": "witness_1", "regex": "[\\w\\-,@.\\s]+", "condition_type": "data_validation"}, {"field": "witness_1_role", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_2", "regex": "[\\w\\-@,.\\s]+", "condition_type": "data_validation"}, {"field": "witness_2_role", "regex": "[\\w\\-,.\\s]+", "condition_type": "data_validation"}]', NULL);
INSERT INTO public.rules VALUES (11, 1, 1, '2018-06-21 14:27:59.964378+00', 'Complete oil extraction', NULL, 'complete_oil_extraction', '[{"field": "to_qty_unit", "regex": "ml", "condition_type": "data_validation"}, {"field": "from_qty_unit", "regex": "g-wet", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"operator": "=", "qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}, {"match_fields": [{"match": "type", "regex": "batch"}], "condition_type": "inventory_match", "inventory_id_field": "to_inventory_id"}]', NULL);
INSERT INTO public.rules VALUES (12, 1, 1, '2018-06-21 14:27:59.964378+00', 'Admin adjustment', NULL, 'admin_adjustment', '[]', NULL);
INSERT INTO public.rules VALUES (13, 1, 1, '2018-06-21 14:27:59.964378+00', 'Lab sample sent', NULL, 'lab_sample_sent', '[{"field": "from_qty_unit", "regex": "(g-dry|ml)", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "([0-9]*[.])?[0-9]+", "condition_type": "data_validation"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}, {"match_fields": [{"match": "type", "regex": "batch"}], "condition_type": "inventory_match", "inventory_id_field": "from_inventory_id"}]', NULL);
INSERT INTO public.rules VALUES (14, 1, 1, '2018-06-21 14:27:59.964378+00', 'Lab results received', NULL, 'lab_result_received', '[{"match_fields": [{"field": "inventory_id", "match": "from_inventory_id"}, {"match": "name", "regex": "lab_sample_sent"}], "condition_type": "activity_match", "activity_id_field": "lab_sample_sent_activity_id"}]', NULL);
INSERT INTO public.rules VALUES (6, 1, 1, '2018-06-21 14:27:59.964378+00', 'Sow seeds', NULL, 'propagate_seeds', '[{"field": "to_qty_unit", "regex": "seeds", "condition_type": "data_validation"}, {"field": "from_qty_unit", "regex": "seeds", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "[1-9]\\d*", "condition_type": "data_validation"}, {"field": "from_qty", "regex": "[1-9]\\d*", "condition_type": "data_validation"}, {"match_fields": [{"match": "variety", "comparison": "="}], "condition_type": "inventory_compare", "first_inventory_id_field": "from_inventory_id", "second_inventory_id_field": "to_inventory_id"}, {"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}]', NULL);
INSERT INTO public.rules VALUES (5, 1, 1, '2018-06-21 14:27:59.964378+00', 'Propagate Cuttings', NULL, 'propagate_cuttings', '[{"field": "to_qty_unit", "regex": "plants", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "[1-9]\\d*", "condition_type": "data_validation"}, {"match_fields": [{"match": "variety", "comparison": "="}], "condition_type": "inventory_compare", "first_inventory_id_field": "to_inventory_id", "second_inventory_id_field": "from_inventory_id"}, {"qty_unit": "to_qty_unit", "qty_value": "source_count", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}]', NULL);
INSERT INTO public.rules VALUES (15, 1, 3, '2018-07-09 14:10:30.303182+00', 'custom-rule', 'Rules about intake', 'receive_inventory', '[{"field": "upload_id", "condition_type": "upload_validation"}]', '{}');
INSERT INTO public.rules VALUES (17, 1, 3, '2018-07-10 15:56:58.390971+00', 'Queue for destruction', '', 'complete_destruction', '[{"match_fields": [{"field": "destroyed_qty_unit", "match": "destroyed_qty_unit"}, {"match": "name", "regex": "queue_for_destruction"}], "condition_type": "activity_match", "activity_id_field": "queue_destruction_activity_id"}]', '{}');
INSERT INTO public.rules VALUES (16, 1, 3, '2018-07-10 13:28:35.291898+00', 'Queue for destruction', '', 'queue_for_destruction', '[{"field": "from_qty", "conditions": [{"qty_unit": "from_qty_unit", "qty_value": "from_qty", "inventory_id": "from_inventory_id", "condition_type": "inventory_count"}], "condition_type": "conditional_has_field"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}, {"field": "type_of_waste", "match": "name", "taxonomy_name": "waste_types", "condition_type": "taxonomy_validation"}, {"field": "reason_for_destruction", "match": "name", "taxonomy_name": "destruction_reasons", "condition_type": "taxonomy_validation"}, {"field": "destroyed_qty", "regex": "\\d+\\.?\\d*", "condition_type": "data_validation"}, {"field": "destroyed_qty_unit", "regex": "g", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "collected_from", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}]', '{}');
INSERT INTO public.rules VALUES (18, 1, 3, '2018-07-24 15:34:38.773526+00', 'Stage Update', '', 'update_stage', '[{"field": "to_stage", "condition_type": "stage_validation", "inventory_id_field": "inventory_id"}]', '{}');
INSERT INTO public.rules VALUES (19, 1, 3, '2018-07-26 15:29:00.826454+00', 'Release Receive Inventory', '', 'release_received_inventory', '[{"field": "to_stage", "condition_type": "stage_validation", "inventory_id_field": "inventory_id"}, {"field": "quarantined", "regex": "~*''false''", "condition_type": "data_validation"}]', '{}');
INSERT INTO public.rules VALUES (1, 1, 1, '2018-06-21 14:23:25.257445+00', 'Intake', NULL, 'receive_inventory', '[{"field": "upload_id", "condition_type": "upload_validation"}, {"field": "vendor_name", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "net_weight_received", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "number_of_pieces", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "weighed_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "checked_by", "regex": "(?!\\s*$).+", "condition_type": "data_validation"}, {"field": "to_qty", "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)", "condition_type": "data_validation"}, {"field": "to_qty_unit", "regex": "(g-dry|g-wet|ml|seeds|plants)", "condition_type": "data_validation"}, {"field": "vendor_lot_number", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "intended_use", "regex": "[\\w\\s]+", "condition_type": "data_validation"}, {"field": "quarantined", "regex": "true", "condition_type": "data_validation"}, {"field": "to_stage", "match": "name", "taxonomy_name": "stages", "condition_type": "taxonomy_validation"}, {"field": "variety", "match": "name", "taxonomy_name": "varieties", "condition_type": "taxonomy_validation"}]', NULL);


--
-- Name: rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rules_id_seq', 19, true);


--
-- Data for Name: taxonomies; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.taxonomies VALUES (2, 1, 3, '2018-06-21 17:39:14.19008+00', 'varieties', NULL);
INSERT INTO public.taxonomies VALUES (9, 1, 3, '2018-06-21 17:55:15.833117+00', 'strains', NULL);
INSERT INTO public.taxonomies VALUES (10, 1, 3, '2018-07-10 13:29:07.966438+00', 'destruction_reasons', '{}');
INSERT INTO public.taxonomies VALUES (11, 1, 3, '2018-07-10 13:29:15.015543+00', 'waste_types', '{}');
INSERT INTO public.taxonomies VALUES (12, 1, 3, '2018-07-10 14:47:43.614851+00', 'destruction_methods', '{}');
INSERT INTO public.taxonomies VALUES (13, 1, 3, '2018-07-18 19:27:43.724644+00', 'stages', '{}');
INSERT INTO public.taxonomies VALUES (14, 1, 3, '2018-07-23 15:02:03.619482+00', 'labels', '{}');


--
-- Name: taxonomies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.taxonomies_id_seq', 14, true);


--
-- Data for Name: taxonomy_options; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.taxonomy_options VALUES (2, 1, 3, '2018-06-21 17:56:10.015428+00', 'Sativa', NULL, 9);
INSERT INTO public.taxonomy_options VALUES (3, 1, 3, '2018-06-21 17:56:24.125284+00', 'Hybrid', NULL, 9);
INSERT INTO public.taxonomy_options VALUES (5, 1, 3, '2018-06-21 17:56:52.468757+00', 'Indica', NULL, 9);
INSERT INTO public.taxonomy_options VALUES (23, 1, 1, '2018-06-28 18:07:32.810458+00', 'Blue Dream', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (24, 1, 1, '2018-06-28 18:07:32.810458+00', 'OG Kush', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (25, 1, 1, '2018-06-28 18:07:32.810458+00', 'White Widow', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (26, 1, 1, '2018-06-28 18:07:32.810458+00', 'Pineapple Express', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (27, 1, 1, '2018-06-28 18:07:32.810458+00', 'AK-47', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (28, 1, 1, '2018-06-28 18:07:32.810458+00', 'Cherry Pie', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (29, 1, 1, '2018-06-28 18:07:32.810458+00', 'Cheese', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (30, 1, 1, '2018-06-28 18:07:32.810458+00', 'Platinum GSC', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (31, 1, 1, '2018-06-28 18:07:32.810458+00', 'Lemon Kush', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (32, 1, 1, '2018-06-28 18:07:32.810458+00', 'Golden Goat', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (33, 1, 1, '2018-06-28 18:07:32.810458+00', 'Agent Orange', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (34, 1, 1, '2018-06-28 18:07:32.810458+00', 'Mango Kush', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (35, 1, 1, '2018-06-28 18:07:32.810458+00', 'Dutch Treat', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (36, 1, 1, '2018-06-28 18:07:32.810458+00', 'Bruce Banner', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (37, 1, 1, '2018-06-28 18:07:32.810458+00', 'Fire OG', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (38, 1, 1, '2018-06-28 18:07:32.810458+00', 'NYC Diesel', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (40, 1, 1, '2018-06-28 18:07:32.810458+00', 'Cotton Candy Kush', '{"strain": "Hybrid"}', 2);
INSERT INTO public.taxonomy_options VALUES (41, 1, 1, '2018-06-28 18:07:32.810458+00', 'Bubba Kush', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (42, 1, 1, '2018-06-28 18:07:32.810458+00', 'Northern Lights', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (43, 1, 1, '2018-06-28 18:07:32.810458+00', 'Blue Cheese', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (44, 1, 1, '2018-06-28 18:07:32.810458+00', 'Purple Kush', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (45, 1, 1, '2018-06-28 18:07:32.810458+00', 'Blueberry', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (46, 1, 1, '2018-06-28 18:07:32.810458+00', 'Grape Ape', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (47, 1, 1, '2018-06-28 18:07:32.810458+00', 'God''s Gift', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (48, 1, 1, '2018-06-28 18:07:32.810458+00', 'Death Star', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (49, 1, 1, '2018-06-28 18:07:32.810458+00', 'LA Confidential', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (50, 1, 1, '2018-06-28 18:07:32.810458+00', 'Purple Urkle', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (51, 1, 1, '2018-06-28 18:07:32.810458+00', 'Afghan Kush', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (52, 1, 1, '2018-06-28 18:07:32.810458+00', 'Hindu Kush', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (53, 1, 1, '2018-06-28 18:07:32.810458+00', 'White Rhino', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (54, 1, 1, '2018-06-28 18:07:32.810458+00', 'G13', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (55, 1, 1, '2018-06-28 18:07:32.810458+00', 'Berry White', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (56, 1, 1, '2018-06-28 18:07:32.810458+00', 'Blueberry Kush', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (57, 1, 1, '2018-06-28 18:07:32.810458+00', 'Mr. Nice', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (58, 1, 1, '2018-06-28 18:07:32.810458+00', 'Romulan', '{"strain": "Indica"}', 2);
INSERT INTO public.taxonomy_options VALUES (59, 1, 1, '2018-06-28 18:07:32.810458+00', 'Sour Diesel', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (60, 1, 1, '2018-06-28 18:07:32.810458+00', 'Jack Herer', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (61, 1, 1, '2018-06-28 18:07:32.810458+00', 'Durban Poison', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (62, 1, 1, '2018-06-28 18:07:32.810458+00', 'Lemon Haze', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (63, 1, 1, '2018-06-28 18:07:32.810458+00', 'Strawberry Cough', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (64, 1, 1, '2018-06-28 18:07:32.810458+00', 'Super Lemon Haze', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (65, 1, 1, '2018-06-28 18:07:32.810458+00', 'Amnesia Haze', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (66, 1, 1, '2018-06-28 18:07:32.810458+00', 'Harlequin', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (67, 1, 1, '2018-06-28 18:07:32.810458+00', 'Purple Haze', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (68, 1, 1, '2018-06-28 18:07:32.810458+00', 'Cinex', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (69, 1, 1, '2018-06-28 18:07:32.810458+00', 'Candyland', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (70, 1, 1, '2018-06-28 18:07:32.810458+00', 'Tangie', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (71, 1, 1, '2018-06-28 18:07:32.810458+00', 'Lamb''s Bread', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (72, 1, 1, '2018-06-28 18:07:32.810458+00', 'Ghost Train Haze', '{"strain": "Sativa"}', 2);
INSERT INTO public.taxonomy_options VALUES (73, 1, 3, '2018-07-10 13:29:22.444704+00', 'Daily sweep', '{}', 10);
INSERT INTO public.taxonomy_options VALUES (74, 1, 3, '2018-07-10 13:29:38.542189+00', 'stems', '{}', 11);
INSERT INTO public.taxonomy_options VALUES (75, 1, 1, '2018-07-10 14:48:04.284808+00', 'Kitty litter', '{"description": "This is how we do it"}', 12);
INSERT INTO public.taxonomy_options VALUES (76, 1, 1, '2018-07-11 14:16:40.318373+00', 'Shredding', '{"description": ""}', 12);
INSERT INTO public.taxonomy_options VALUES (77, 1, 1, '2018-07-11 15:54:49.790149+00', 'Test!', '{"description": "New Test"}', 12);
INSERT INTO public.taxonomy_options VALUES (78, 1, 1, '2018-07-11 15:58:05.780633+00', 'leaves', '{"description": ""}', 12);
INSERT INTO public.taxonomy_options VALUES (79, 1, 1, '2018-07-11 15:58:28.49419+00', 'leaves', '{"description": ""}', 11);
INSERT INTO public.taxonomy_options VALUES (80, 1, 1, '2018-07-11 22:39:43.601104+00', 'Harvest trimmings', '{"description": ""}', 10);
INSERT INTO public.taxonomy_options VALUES (82, 1, 3, '2018-07-18 20:40:21.929128+00', 'testy3', '{"TMI": "nope", "strain": "Hybrid", "description": "For mother plant"}', 2);
INSERT INTO public.taxonomy_options VALUES (87, 1, 1, '2018-07-20 14:01:11.792462+00', 'received-unapproved', '{"description": "", "allowed_inventory_types": ["received inventory"], "allowed_previous_stages": [""]}', 13);
INSERT INTO public.taxonomy_options VALUES (81, 1, 1, '2018-07-18 20:13:25.824174+00', 'propagation', '{"description": "", "allowed_inventory_types": ["mother", "batch"], "allowed_previous_stages": ["", "seedling"]}', 13);
INSERT INTO public.taxonomy_options VALUES (84, 1, 1, '2018-07-19 02:11:42.160042+00', 'seedling', '{"description": "", "allowed_inventory_types": ["mother", "batch"], "allowed_previous_stages": [""]}', 13);
INSERT INTO public.taxonomy_options VALUES (85, 1, 1, '2018-07-19 15:17:02.372681+00', 'vegetation', '{"description": "", "allowed_inventory_types": ["mother", "batch"], "allowed_previous_stages": ["propagation"]}', 13);
INSERT INTO public.taxonomy_options VALUES (86, 1, 1, '2018-07-19 18:29:01.988827+00', 'drying', '{"description": "", "allowed_inventory_types": ["batch"], "allowed_previous_stages": ["flowering"]}', 13);
INSERT INTO public.taxonomy_options VALUES (88, 1, 1, '2018-07-20 19:25:04.059829+00', 'received-approved', '{"description": "", "allowed_inventory_types": ["received inventory"], "allowed_previous_stages": ["received-unapproved"]}', 13);
INSERT INTO public.taxonomy_options VALUES (39, 1, 1, '2018-06-28 18:07:32.810458+00', 'Animal Cookies', '{"strain": "Hybrid", "stage_info": "[drying:{days_in_stage:10},vegetation:{days_in_stage:14}]", "description": "check"}', 2);
INSERT INTO public.taxonomy_options VALUES (89, 1, 3, '2018-07-23 15:04:20.564161+00', 'Item Queued for Destruction', '{"type": "item_for_destruction", "format": "ZPL", "template": "\r\n^XA\r\n^FO576,0^GFA,06272,06272,00028,:Z64:\r\neJztWMGK4zgQLZsWNIbALNiwhwmEPgV/hQLJ3QEL5jD5F80t7FeYOQV/hfsPcphAHzb/slUlOZZlyQ5z290u04mk8svTqypZcgN82v/DXmd82YxPzfhaHXUlty7qS9sm6hOqivqy9hL1rU9/R31l20Z9StW/hbvdbjrma9toYBKllIz4UsQ1EZ+43+/XiC9DXCwwBfLFAjqLQ32/Ij4MSzQwiizia2dwpzteegYX9iXMJ4O+dA53I+towm76z2fd4xpcMdwdmGqqTsUBFWOVGzQOJ+G4M5phDas72TXxonNG0wZ3eeXOWFlVGD4/qm8pXhbHbT8iBeu7+TiiOP9l5nkO8KkDf+58HEna2HhupvoQwflLgnza5D3IZ+pzgiNJKQe0sW0fJyh9ET6zjsJ8vP4mOKuJyyWoDxJMH0T4gMs6zMfPlwnO5qyk5RfMHy3Aa5SPn4Pcdnw9Dqszpi+jqvb09bjVqYvy8fM6yCdxJUiDc9eRzVmK4Uy9/PW4BB+fwsf1a4BWrc9XWJyCKW7TJxCm+iwO7gHcg882J3z46KyH5qDP5qy0Ul0+MYPrSbYD9RiHoHyYsieQ9/CNr68P/p+P0Dp2Jh7G0fery5cQJeK+EI67Y7NF+eaPK56rYSauyfZpVJ290ZdDD4aEQ3KQ8IwZQYI/DOlke9EB2Etd8+9LZyB+sHDpvO2ymDsgPCzZH/b70YjAERm+efzrnh6/ZMJWk8nJyBKs3768CURPJA8cihkLPPDIEk4pj9BMYDGitbX4QHiaSo0Yh/78RI280LWAUzFbyGDt2N7tzPOBS7FzO/OwkcDEae+XcAND7ZIvFuigqIL8aXmuQOmQLy/AQaBZi8+VZ7/bWoriyWiS5Y6il4fUZUtcRc/T0fOTJEnTcdtLVjj5Ek8Fszf3zvxJtn+LfQmM5eYrnbwzZLp/0xWTt1qhk5t5MSsnL2+Z7t9Y1cEvDoGJMQFuIYDTJbc+hg3M2kp/hTW3fBThtjRXrDIfRXy12UDTxjKAZYcs0xdIGdfhjYVWV6FzqPCIlhdCX0F0hMMbslK3l1RnsMUgZW2mG4Oj7VmoRNVCFlCJg8yVwF2ep8G4Jm3KFDVtM2iyhnENBw8FdaJbJ3INH1+hWstVcnVwOM0McbohqB5w/IdXIo9Q4VQLava47IK3IrZ5082WKB2+AqXhzT+643tXERSbLPuBS0M4QFVAJNVxJ3E95eDq21ocGh7pXVwH3yhhGMT39+50R4krjKflG3A/MXFgcTaehg+OcicrKk0BlTkF4Q9b3FY/cEP+KqExLvrY3TQfJgV+CW3qhUOIRaLfelxp66UiPmL8A49oueHLsWsqBOOC+YMSE5HBJnPq85R8rHRy/Q5rfYJ1V6E+WO/Mf2JwPdDCuTANvkIQLrXroVASY4rPpYJUcjzx0WjWCJWWhrLBCZb0KpA56w8qsOknswu2mBT7YH2Zh0zEXSZ9Mdy9iztn/rUFc8eQcgb3aZ/2H7V/AExaSqc=:221D\r\n^CWY,E:ARI001.FNT^FT21,1611^AYN,53,22\r\n^FH\\^FDGrowerIQ^FS\r\n^BY4,7^FT179,1254^B7N,7,0,,,N\r\n^FH\\^FD{barcode_data}^FS\r\n^FO4,1536^GB806,0,8^FS\r\n^CWZ,E:ARI000.FNT^FT628,1614^AZN,39,15\r\n^FH\\^FDgroweriq.ca^FS\r\n^CWY,E:ARI001.FNT^FT13,269^AYN,53,22\r\n^FH\\^FDProduct For Destruction^FS\r\n^FO2,283^GB808,0,11^FS\r\n^CWY,E:ARI001.FNT^FT583,466^AYN,53,22\r\n^FH\\^FD{queue_activity[type_of_waste]}^FS\r\n^CWY,E:ARI001.FNT^FT322,460^AYN,53,22\r\n^FH\\^FD{queue_activity[destroyed_qty]} {queue_activity[destroyed_qty_unit]}^FS\r\n^CWY,E:ARI001.FNT^FT27,462^AYN,53,22\r\n^FH\\^FD{queue_activity[collected_from]}^FS\r\n^CWY,E:ARI001.FNT^FT320,573^AYN,53,22\r\n^FH\\^FD{queue_activity[collected_from]}^FS\r\n^CWY,E:ARI001.FNT^FT27,801^AYN,53,22\r\n^FH\\^FD{queue_activity[checked_by]}^FS\r\n^CWY,E:ARI001.FNT^FT27,698^AYN,53,22\r\n^FH\\^FD{queue_activity[weighed_by]}^FS\r\n^CWZ,E:ARI000.FNT^FT583,501^AZN,39,15\r\n^FH\\^FDType of Waste^FS\r\n^CWZ,E:ARI000.FNT^FT27,840^AZN,39,15\r\n^FH\\^FDChecked By^FS\r\n^CWY,E:ARI001.FNT^FT27,573^AYN,53,22\r\n^FH\\^FD{queue_activity[from_inventory_id]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,737^AZN,39,15\r\n^FH\\^FDWeighed By^FS\r\n^CWZ,E:ARI000.FNT^FT322,499^AZN,39,15\r\n^FH\\^FDNet Weight^FS\r\n^CWZ,E:ARI000.FNT^FT320,612^AZN,39,15\r\n^FH\\^FDVariety^FS\r\n^CWZ,E:ARI000.FNT^FT27,612^AZN,39,15\r\n^FH\\^FDInventory ID^FS\r\n^CWZ,E:ARI000.FNT^FT27,501^AZN,39,15\r\n^FH\\^FDCollected From^FS\r\n^CWY,E:ARI001.FNT^FT27,372^AYN,53,22\r\n^FH\\^FD{queue_activity[timestamp]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,411^AZN,39,15\r\n^FH\\^FDDate Collected^FS\r\n^XZ\r\n"}', 14);
INSERT INTO public.taxonomy_options VALUES (90, 1, 3, '2018-07-25 13:12:59.153366+00', 'Received Item Quarantine', '{"type": "received_item_quarantine", "format": "ZPL", "template": "^XA\r\n^FO576,0^GFA,06272,06272,00028,:Z64:\r\neJztWMGK4zgQLZsWNIbALNiwhwmEPgV/hQLJ3QEL5jD5F80t7FeYOQV/hfsPcphAHzb/slUlOZZlyQ5z290u04mk8svTqypZcgN82v/DXmd82YxPzfhaHXUlty7qS9sm6hOqivqy9hL1rU9/R31l20Z9StW/hbvdbjrma9toYBKllIz4UsQ1EZ+43+/XiC9DXCwwBfLFAjqLQ32/Ij4MSzQwiizia2dwpzteegYX9iXMJ4O+dA53I+towm76z2fd4xpcMdwdmGqqTsUBFWOVGzQOJ+G4M5phDas72TXxonNG0wZ3eeXOWFlVGD4/qm8pXhbHbT8iBeu7+TiiOP9l5nkO8KkDf+58HEna2HhupvoQwflLgnza5D3IZ+pzgiNJKQe0sW0fJyh9ET6zjsJ8vP4mOKuJyyWoDxJMH0T4gMs6zMfPlwnO5qyk5RfMHy3Aa5SPn4Pcdnw9Dqszpi+jqvb09bjVqYvy8fM6yCdxJUiDc9eRzVmK4Uy9/PW4BB+fwsf1a4BWrc9XWJyCKW7TJxCm+iwO7gHcg882J3z46KyH5qDP5qy0Ul0+MYPrSbYD9RiHoHyYsieQ9/CNr68P/p+P0Dp2Jh7G0fery5cQJeK+EI67Y7NF+eaPK56rYSauyfZpVJ290ZdDD4aEQ3KQ8IwZQYI/DOlke9EB2Etd8+9LZyB+sHDpvO2ymDsgPCzZH/b70YjAERm+efzrnh6/ZMJWk8nJyBKs3768CURPJA8cihkLPPDIEk4pj9BMYDGitbX4QHiaSo0Yh/78RI280LWAUzFbyGDt2N7tzPOBS7FzO/OwkcDEae+XcAND7ZIvFuigqIL8aXmuQOmQLy/AQaBZi8+VZ7/bWoriyWiS5Y6il4fUZUtcRc/T0fOTJEnTcdtLVjj5Ek8Fszf3zvxJtn+LfQmM5eYrnbwzZLp/0xWTt1qhk5t5MSsnL2+Z7t9Y1cEvDoGJMQFuIYDTJbc+hg3M2kp/hTW3fBThtjRXrDIfRXy12UDTxjKAZYcs0xdIGdfhjYVWV6FzqPCIlhdCX0F0hMMbslK3l1RnsMUgZW2mG4Oj7VmoRNVCFlCJg8yVwF2ep8G4Jm3KFDVtM2iyhnENBw8FdaJbJ3INH1+hWstVcnVwOM0McbohqB5w/IdXIo9Q4VQLava47IK3IrZ5082WKB2+AqXhzT+643tXERSbLPuBS0M4QFVAJNVxJ3E95eDq21ocGh7pXVwH3yhhGMT39+50R4krjKflG3A/MXFgcTaehg+OcicrKk0BlTkF4Q9b3FY/cEP+KqExLvrY3TQfJgV+CW3qhUOIRaLfelxp66UiPmL8A49oueHLsWsqBOOC+YMSE5HBJnPq85R8rHRy/Q5rfYJ1V6E+WO/Mf2JwPdDCuTANvkIQLrXroVASY4rPpYJUcjzx0WjWCJWWhrLBCZb0KpA56w8qsOknswu2mBT7YH2Zh0zEXSZ9Mdy9iztn/rUFc8eQcgb3aZ/2H7V/AExaSqc=:221D\r\n^CWY,E:ARI001.FNT^FT21,1611^AYN,53,22\r\n^FH\\^FDGrowerIQ^FS\r\n^BY4,7^FT179,1254^B7N,7,0,,,N\r\n^FH\\^FD{\"type\":\"item_for_destruction\", \"id\": 123456\"}^FS\r\n^FO4,1536^GB806,0,8^FS\r\n^CWZ,E:ARI000.FNT^FT628,1614^AZN,39,15\r\n^FH\\^FDgroweriq.ca^FS\r\n^CWY,E:ARI001.FNT^FT13,217^AYN,53,22\r\n^FH\\^FDQUARANTINED PRODUCT^FS\r\n^CWY,E:ARI001.FNT^FT13,270^AYN,53,22\r\n^FH\\^FDDo Not Pick^FS\r\n^FO2,283^GB808,0,11^FS\r\n^CWY,E:ARI001.FNT^FT472,460^AYN,53,22\r\n^FH\\^FD{activity[net_weight_received]}g^FS\r\n^CWY,E:ARI001.FNT^FT27,462^AYN,53,22\r\n^FH\\^FDPending QA^FS\r\n^CWY,E:ARI001.FNT^FT313,573^AYN,53,22\r\n^FH\\^FD{activity[variety]}^FS\r\n^CWY,E:ARI001.FNT^FT27,801^AYN,53,22\r\n^FH\\^FD{activity[checked_by]}^FS\r\n^CWY,E:ARI001.FNT^FT27,698^AYN,53,22\r\n^FH\\^FD{activity[weighed_by]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,840^AZN,39,15\r\n^FH\\^FDChecked By^FS\r\n^CWY,E:ARI001.FNT^FT27,573^AYN,53,22\r\n^FH\\^FD{activity[inventory_id]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,737^AZN,39,15\r\n^FH\\^FDWeighed By^FS\r\n^CWZ,E:ARI000.FNT^FT472,499^AZN,39,15\r\n^FH\\^FDWeight^FS\r\n^CWZ,E:ARI000.FNT^FT313,612^AZN,39,15\r\n^FH\\^FDVariety^FS\r\n^CWZ,E:ARI000.FNT^FT27,612^AZN,39,15\r\n^FH\\^FDInventory ID^FS\r\n^CWZ,E:ARI000.FNT^FT27,501^AZN,39,15\r\n^FH\\^FDReason^FS\r\n^CWY,E:ARI001.FNT^FT27,372^AYN,53,22\r\n^FH\\^FD{activity[timestamp]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,411^AZN,39,15\r\n^FH\\^FDDate^FS\r\n^XZ\r\n"}', 14);
INSERT INTO public.taxonomy_options VALUES (91, 1, 1, '2018-07-25 15:25:36.104732+00', 'flowering', '{"description": "", "allowed_inventory_types": ["batch"], "allowed_previous_stages": ["vegetation"]}', 13);
INSERT INTO public.taxonomy_options VALUES (92, 1, 1, '2018-07-27 19:43:52.552856+00', 'Approved Received Inventory', '{"type": "approved_received_inventory", "format": "ZPL", "template": "\r\n^XA\r\n^FO576,0^GFA,05120,05120,00032,:Z64:\r\neJztVzGO4zAMtIwYCFJtgHO5gJEyr1Dh9C6sbv0Xl3lGysCvuCdscS73LyeSUiwrFK1cdUUYwJFETEZDUrRSFG97W7Z9bPibDX+34b/LbvVH9peT7K+MFv2HaRT9n4Ms4DzdRL8xMn6axACoeRYDUE6TGIDKGLOFHwX/5zAMvwX/YQNfW34t+M8WfxP8Zp7nb8Fv4WIALb3p/x2vrPzhK+2H8EkJgPBLCdjEz2AwOrL+A+LHothfr2uPwrgTv4bvOApN0wR4nEV4W7mQ/mHQRyaKV2sOf9vjZL1zJK6Jn8lCWZ7KU3MmPIxLBt8b1D9zUQTKK+FxyPEb4q+4KmjAaP805vDVD+SfxRMn1U+SH+uv4/Ao+YT1P7oxh6+tei3w0/lL8fd0/tP6Xf9g9CvCqB9b/gI/9S+G3+Ohinj9lHM4/uWzfI+3DeBb5Mf+m+YvXPWn9FP/T+k30AATeMeJ+BS/gTy4XMSvAZfzw+RqIcFfzQk8nrkR339uuDaP76kJP+Gd5vJesPoL1znUVwLvSe8J/trhu8dwbf7M3x+hYPAd3h8Mh/ektwR/FeHj3/eiG17+A68xFTXXxH3Tha8946+oaFTyDUQ9rywZlwJM7fDwYK8RxD8ynraFJ+660vaxu+jEJlhTFLAaHr9wZHruJshRI6bvkU/HC9n0UcFtvMcj213aSG9rV/LxTwdecUcgbT3YakNPK5LRayukMxsXibWBWPtZFiqctzoPTr0n3EAdL4hGYvsl44+FPLxj84qDaZ6A3aVNfPLwAaG/QgTbyeDvA1tN8vAqpAwnuQUYBKAtXpa/CkBXBPxb/wUftijWcPJfk7/agL8J5WcfbLfIL4pwnGshpd9M/vFfSgAnr6pfNqBx/NwOMiw871E3yLJjkO6P+lX2t/239hcIyIpQ:5E09\r\n^CWY,E:ARI001.FNT^FT21,1611^AYN,53,22\r\n^FH\\^FDGrowerIQ^FS\r\n^BY4,7^FT179,1254^B7N,7,0,,,N\r\n^FH\\^FD{barcode_data}^FS\r\n^FO4,1536^GB806,0,8^FS\r\n^CWZ,E:ARI000.FNT^FT628,1614^AZN,39,15\r\n^FH\\^FDgroweriq.ca^FS\r\n^CWY,E:ARI001.FNT^FT13,269^AYN,53,22\r\n^FH\\^FDApproved Received Inventory^FS\r\n^FO2,283^GB808,0,11^FS\r\n^CWY,E:ARI001.FNT^FT583,466^AYN,53,22\r\n^FH\\^FD{activity[approved_received_inventory]}^FS\r\n^CWY,E:ARI001.FNT^FT322,460^AYN,53,22\r\n^FH\\^FD{activity[collected_from]}^FS\r\n^CWY,E:ARI001.FNT^FT320,573^AYN,53,22\r\n^FH\\^FD{activity[collected_from]}^FS\r\n^CWY,E:ARI001.FNT^FT27,801^AYN,53,22\r\n^FH\\^FD{activity[checked_by]}^FS\r\n^CWY,E:ARI001.FNT^FT27,698^AYN,53,22\r\n^CWZ,E:ARI000.FNT^FT583,501^AZN,39,15\r\n^FH\\^FDApproved Received Inventory^FS\r\n^CWZ,E:ARI000.FNT^FT27,840^AZN,39,15\r\n^FH\\^FDChecked By^FS\r\n^CWY,E:ARI001.FNT^FT27,573^AYN,53,22\r\n^FH\\^FD{activity[from_inventory_id]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,737^AZN,39,15\r\n^CWZ,E:ARI000.FNT^FT322,499^AZN,39,15\r\n^CWZ,E:ARI000.FNT^FT320,612^AZN,39,15\r\n^FH\\^FDVariety^FS\r\n^CWZ,E:ARI000.FNT^FT27,612^AZN,39,15\r\n^FH\\^FDInventory ID^FS\r\n^CWZ,E:ARI000.FNT^FT27,501^AZN,39,15\r\n^FH\\^FDCollected From^FS\r\n^CWY,E:ARI001.FNT^FT27,372^AYN,53,22\r\n^FH\\^FD{activity[timestamp]}^FS\r\n^CWZ,E:ARI000.FNT^FT27,411^AZN,39,15\r\n^FH\\^FDDate Collected^FS\r\n^XZ\r\n"}', 14);
INSERT INTO public.taxonomy_options VALUES (94, 1, 1, '2018-08-01 00:13:44.252277+00', 'test stage', '{"description": "", "allowed_inventory_types": ["mother"], "allowed_previous_stages": [""]}', 13);
INSERT INTO public.taxonomy_options VALUES (93, 1, 1, '2018-07-31 14:39:38.73777+00', 'added variety ', '{"strain": "Hybrid", "stage_info": {"flowering": {"days_in_stage": 10}, "vegetation": {"days_in_stage": 10}}, "description": "check"}', 2);


--
-- Name: taxonomy_options_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.taxonomy_options_id_seq', 94, true);


--
-- Data for Name: uploads; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.uploads VALUES (2, 1, 'receipt-2018.png', 'image/png', true, '{}', 1, '2018-06-25 14:42:58.321126+00');
INSERT INTO public.uploads VALUES (3, 1, 'receipt-2018.png', 'image/png', true, '{}', 1, '2018-06-29 14:34:32.846381+00');
INSERT INTO public.uploads VALUES (4, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-24 16:04:13.016948+00');
INSERT INTO public.uploads VALUES (5, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-26 17:33:27.078797+00');
INSERT INTO public.uploads VALUES (6, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-26 17:35:21.893089+00');
INSERT INTO public.uploads VALUES (7, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-26 18:11:36.31352+00');
INSERT INTO public.uploads VALUES (8, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-26 18:18:03.539389+00');
INSERT INTO public.uploads VALUES (9, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-26 19:07:02.909646+00');
INSERT INTO public.uploads VALUES (10, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 13:45:02.398375+00');
INSERT INTO public.uploads VALUES (11, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 13:47:51.487668+00');
INSERT INTO public.uploads VALUES (12, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 13:48:42.897318+00');
INSERT INTO public.uploads VALUES (13, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 13:49:42.873635+00');
INSERT INTO public.uploads VALUES (14, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 13:52:05.10733+00');
INSERT INTO public.uploads VALUES (15, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 13:54:06.44759+00');
INSERT INTO public.uploads VALUES (16, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-27 13:54:46.288916+00');
INSERT INTO public.uploads VALUES (17, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-27 14:47:55.849707+00');
INSERT INTO public.uploads VALUES (18, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-27 14:52:22.344784+00');
INSERT INTO public.uploads VALUES (19, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-27 17:54:19.661971+00');
INSERT INTO public.uploads VALUES (20, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', false, '{}', 7, '2018-07-27 21:03:13.252316+00');
INSERT INTO public.uploads VALUES (21, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-27 21:04:40.237767+00');
INSERT INTO public.uploads VALUES (22, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-27 21:17:10.88107+00');
INSERT INTO public.uploads VALUES (23, 1, 'Adobe Acrobat PDF Files111.pdf', 'application/pdf', true, '{}', 7, '2018-07-30 13:55:08.090342+00');
INSERT INTO public.uploads VALUES (24, 1, 'receipt-2018.png', 'image/png', true, '{}', 1, '2018-07-30 14:11:01.430413+00');


--
-- Name: uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.uploads_id_seq', 24, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users VALUES (1, 'daniel.favand@wilcompute.com', 1, 'auth0|5ab26f288bd5067ff5787c89', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (3, 'tests+s2s-dev@wilcompute.com', 1, 'auth0|5ac781b6fcdc016ee9ee751b', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (5, 'hareen.peiris@wilcompute.com', 1, 'auth0|5acb75dda33e56128a547fac', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (6, 'william.buttenham@wilcompute.com', 1, 'auth0|5acb958da33e56128a548837', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (7, 'shila.regmi.atreya@wilcompute.com', 1, 'auth0|5b04355c42f10e18ba74ed31', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (8, 'daniel.kain@wilcompute.com', 1, 'auth0|5b1a7cd2157859716f2d1f76', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (9, 'aneesa.guerra.khan@wilcompute.com', 1, 'auth0|5b1a7cea55f2302168ff85cd', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);
INSERT INTO public.users VALUES (2, 'andrew.wilson@wilcompute.com', 1, 'auth0|5a9efa307a392148fa27df14', 1, true, 1, '2018-06-21 14:20:25.97703+00', NULL);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 10, true);


--
-- Data for Name: sensors; Type: TABLE DATA; Schema: sensor_data; Owner: postgres
--



--
-- Name: sensors_id_seq; Type: SEQUENCE SET; Schema: sensor_data; Owner: postgres
--

SELECT pg_catalog.setval('sensor_data.sensors_id_seq', 2, true);


--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- Name: inventories inventories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: rules rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_pkey PRIMARY KEY (id);


--
-- Name: taxonomies taxonomies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT taxonomies_pkey PRIMARY KEY (id);


--
-- Name: taxonomy_options taxonomy_options_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_pkey PRIMARY KEY (id);


--
-- Name: equipment unique_external_id_per_type_per_org; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT unique_external_id_per_type_per_org UNIQUE (external_id, type, organization_id);


--
-- Name: taxonomy_options unique_option_per_taxonomy; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT unique_option_per_taxonomy UNIQUE (taxonomy_id, name);


--
-- Name: roles unique_org_role_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT unique_org_role_name UNIQUE (organization_id, name);


--
-- Name: organizations unique_organization_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT unique_organization_name UNIQUE (name);


--
-- Name: rooms unique_room_name_per_org; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT unique_room_name_per_org UNIQUE (organization_id, name);


--
-- Name: taxonomies unique_taxonomies_per_org; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT unique_taxonomies_per_org UNIQUE (organization_id, name);


--
-- Name: uploads uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT uploads_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: activities_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX activities_data ON public.activities USING gin (data);


--
-- Name: fki_taxonomies_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_taxonomies_org ON public.taxonomies USING btree (organization_id);


--
-- Name: fki_taxonomies_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_taxonomies_user ON public.taxonomies USING btree (created_by);


--
-- Name: fki_user_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_user_role ON public.users USING btree (role_id);


--
-- Name: fki_users_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_users_org ON public.users USING btree (organization_id);


--
-- Name: inventories_attributes; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX inventories_attributes ON public.inventories USING gin (attributes);


--
-- Name: inventories_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX inventories_data ON public.inventories USING gin (data);


--
-- Name: inventories_stats; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX inventories_stats ON public.inventories USING gin (stats);


--
-- Name: organizations_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organizations_data ON public.organizations USING gin (data);


--
-- Name: role_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX role_data ON public.roles USING gin (data);


--
-- Name: rules_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rules_data ON public.rules USING gin (data);


--
-- Name: taxonomy_options_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX taxonomy_options_data ON public.taxonomy_options USING gin (data);


--
-- Name: uploads_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX uploads_data ON public.uploads USING gin (data);


--
-- Name: users_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_data ON public.users USING gin (data);


--
-- Name: activities activities_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER activities_update_merge_data BEFORE UPDATE ON public.activities FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: equipment equipment_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER equipment_update_merge_data BEFORE UPDATE ON public.equipment FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: inventories inventories_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER inventories_update_merge_data BEFORE UPDATE ON public.inventories FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: organizations organizations_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER organizations_update_merge_data BEFORE UPDATE ON public.organizations FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: roles roles_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER roles_update_merge_data BEFORE UPDATE ON public.roles FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: rooms rooms_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER rooms_update_merge_data BEFORE UPDATE ON public.rooms FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: rules rules_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER rules_update_merge_data BEFORE UPDATE ON public.rules FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: taxonomies taxonomies_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER taxonomies_update_merge_data BEFORE UPDATE ON public.taxonomies FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: taxonomy_options taxonomy_options_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER taxonomy_options_update_merge_data BEFORE UPDATE ON public.taxonomy_options FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: activities update_stats_on_new_activity; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_stats_on_new_activity BEFORE INSERT ON public.activities FOR EACH ROW EXECUTE PROCEDURE public.update_stats();


--
-- Name: uploads uploads_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER uploads_update_merge_data BEFORE UPDATE ON public.uploads FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: users users_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER users_update_merge_data BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- Name: activities activity_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activity_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: activities activity_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activity_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: equipment equipment_org_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_org_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: equipment equipment_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_user_id FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: inventories inventories_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: inventories inventories_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: roles role_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT role_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: rooms rooms_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: rooms rooms_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: rules rules_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: rules rules_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: taxonomies taxonomies_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT taxonomies_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: taxonomies taxonomies_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT taxonomies_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: taxonomy_options taxonomy_options_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: taxonomy_options taxonomy_options_taxonomy; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_taxonomy FOREIGN KEY (taxonomy_id) REFERENCES public.taxonomies(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: taxonomy_options taxonomy_options_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: uploads upload_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT upload_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: uploads upload_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT upload_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: users users_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: users users_role; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: cloudsqlsuperuser
--

REVOKE ALL ON SCHEMA public FROM cloudsqladmin;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: SCHEMA sensor_data; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA sensor_data FROM postgres;
GRANT ALL ON SCHEMA sensor_data TO postgres WITH GRANT OPTION;
GRANT ALL ON SCHEMA sensor_data TO dev_server WITH GRANT OPTION;
GRANT USAGE ON SCHEMA sensor_data TO dev_sensor_service;


--
-- Name: FUNCTION jsonb_merge_data(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.jsonb_merge_data() TO dev_server;
GRANT ALL ON FUNCTION public.jsonb_merge_data() TO dev_sensor_service;


--
-- Name: FUNCTION update_stats(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_stats() TO dev_server;
GRANT ALL ON FUNCTION public.update_stats() TO dev_sensor_service;


--
-- Name: TABLE activities; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.activities TO dev_server;


--
-- Name: SEQUENCE activities_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.activities_id_seq TO dev_server;


--
-- Name: TABLE equipment; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,TRIGGER,UPDATE ON TABLE public.equipment TO dev_server;
GRANT SELECT,INSERT,DELETE,TRIGGER,UPDATE ON TABLE public.equipment TO dev_sensor_service;


--
-- Name: SEQUENCE equipment_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE public.equipment_id_seq TO dev_server;
GRANT SELECT,UPDATE ON SEQUENCE public.equipment_id_seq TO dev_sensor_service;


--
-- Name: TABLE inventories; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.inventories TO dev_server;


--
-- Name: SEQUENCE inventories_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.inventories_id_seq TO dev_server;


--
-- Name: TABLE organizations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.organizations TO dev_server;


--
-- Name: SEQUENCE organizations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.organizations_id_seq TO dev_server;


--
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.roles TO dev_server;


--
-- Name: SEQUENCE roles_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.roles_id_seq TO dev_server;


--
-- Name: TABLE rooms; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.rooms TO dev_server;


--
-- Name: SEQUENCE rooms_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.rooms_id_seq TO dev_server;


--
-- Name: TABLE rules; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.rules TO dev_server;


--
-- Name: SEQUENCE rules_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.rules_id_seq TO dev_server;


--
-- Name: TABLE taxonomies; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.taxonomies TO dev_server;


--
-- Name: SEQUENCE taxonomies_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.taxonomies_id_seq TO dev_server;


--
-- Name: TABLE taxonomy_options; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.taxonomy_options TO dev_server;


--
-- Name: SEQUENCE taxonomy_options_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.taxonomy_options_id_seq TO dev_server;


--
-- Name: TABLE uploads; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.uploads TO dev_server;


--
-- Name: SEQUENCE uploads_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.uploads_id_seq TO dev_server;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.users TO dev_server;


--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.users_id_seq TO dev_server;


--
-- Name: TABLE sensors; Type: ACL; Schema: sensor_data; Owner: postgres
--

GRANT ALL ON TABLE sensor_data.sensors TO dev_server WITH GRANT OPTION;
GRANT SELECT,INSERT,DELETE,TRIGGER,UPDATE ON TABLE sensor_data.sensors TO dev_sensor_service;


--
-- PostgreSQL database dump complete
--

