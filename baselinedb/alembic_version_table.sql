CREATE DATABASE [seed-to-sale-test];

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);

ALTER TABLE public.alembic_version OWNER TO migration_runner;

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);

ALTER USER migration_runner WITH SUPERUSER;
