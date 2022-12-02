"""new end types and serialize stats function

Revision ID: b98aebdbe206
Revises: d97679384caf
Create Date: 2021-05-10 11:58:27.660966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b98aebdbe206'
down_revision = 'd97679384caf'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
"""
DROP FUNCTION IF EXISTS f_serialize_stats(stats jsonb, OUT unit text, OUT qty numeric);
CREATE OR REPLACE FUNCTION f_serialize_stats(stats jsonb, OUT unit text, OUT qty numeric)
    RETURNS record
    LANGUAGE plpgsql
AS
$$
BEGIN

    WITH RECURSIVE _stats (key, value) AS (
        SELECT NULL  AS key,
               stats AS value

        UNION ALL

        SELECT JSONB_OBJECT_KEYS(value)          AS key,
               value -> JSONB_OBJECT_KEYS(value) AS value
        FROM _stats
        WHERE JSONB_TYPEOF(value) = 'object'
    )
    SELECT key,
           value::text::float
    FROM _stats
    WHERE JSONB_TYPEOF(value) = 'number'
      AND value::text::float > 0
    INTO unit, qty;

    IF NOT found THEN
        SELECT 'none', 0
        INTO unit, qty;
    END IF;
END;
$$;
"""
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
    	"""
        DROP FUNCTION IF EXISTS f_serialize_stats(stats jsonb, OUT unit text, OUT qty numeric);
	    """
    )
