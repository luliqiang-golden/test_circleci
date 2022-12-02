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
	UPDATE inventories SET attributes = jsonb_set(coalesce(attributes, '{}'), ARRAY['quarantined'], to_jsonb(NEW.data->'quarantined') )
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


--
-- Name: FUNCTION jsonb_merge_data(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.jsonb_merge_data() TO dev_server;


--
-- Name: FUNCTION update_stats(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_stats() TO dev_server;


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


--
-- Name: SEQUENCE equipment_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE public.equipment_id_seq TO dev_server;


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
-- PostgreSQL database dump complete
--
