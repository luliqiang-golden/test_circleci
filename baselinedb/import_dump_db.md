### Import Test database dump
To run the tests using sqlachemy is necessary to import de dumpdb.sql to seed-to-sale-test database.

- Import the file baselinedb/dump.sql
    
    ```sql
    docker container exec -i db psql -U <user> -W seed-to-sale-test <  dumpdb.sql
    ```
