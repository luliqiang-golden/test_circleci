# Base image
FROM postgres:9.6

# Copy initdb script to create a db api user
COPY *.sh /docker-entrypoint-initdb.d/

# Copy sql schema and data files into container (these are imported when the container starts up)
COPY *.sql /docker-entrypoint-initdb.d/

# Default command
CMD ["postgres"]
