from __future__ import with_statement

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys
from dotenv import load_dotenv

sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, "python_scripts"))
from settings import Settings


load_dotenv('.env')  # pylint: disable=C0413

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
#from baseline_1_12 import baselinedb
#target_metadata = baselinedb.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def build_database_url():
    """Builds the database url for alembic based on env configuration"""
    user = Settings.get_setting("ALEMBIC_USERNAME", 'postgres')
    password = Settings.get_setting("DB_PASSWORD")
    db_host = Settings.get_setting("DB_HOST", '127.0.0.1')
    db_name = Settings.get_setting("DB")
    sql_url = "postgresql://{0}:{1}@{2}/{3}".format(user, password, db_host, db_name)
    sql_url = sql_url.replace('%', '%%')

    return sql_url


# Set database url
config.set_main_option('sqlalchemy.url', build_database_url())


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
