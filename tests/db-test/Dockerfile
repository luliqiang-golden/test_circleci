# Base image
FROM postgres:9.6

# Copy initdb script to create a db api user

COPY 0_cypress_init.sh /docker-entrypoint-initdb.d/


# Copy sql schema into container (these are imported when the container starts up)
COPY 1_cypress_schema.sql /docker-entrypoint-initdb.d/

# Copy sql data files into container (these are imported when the container starts up)
COPY 2_cypress_data.sql /docker-entrypoint-initdb.d/

# Default command
CMD ["postgres"]
