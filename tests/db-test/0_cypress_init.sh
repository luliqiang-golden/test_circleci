#!/bin/bash

# Create db user for api
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" <<-EOSQL
	CREATE USER $POSTGRES_API_USER WITH PASSWORD '$POSTGRES_PASSWORD';

	CREATE USER migration_runner WITH
		LOGIN
		NOSUPERUSER
		NOCREATEDB
		NOCREATEROLE
		INHERIT
		NOREPLICATION
		CONNECTION LIMIT -1
		PASSWORD '$POSTGRES_PASSWORD';

	GRANT postgres TO migration_runner;
	alter user migration_runner with superuser;

EOSQL

