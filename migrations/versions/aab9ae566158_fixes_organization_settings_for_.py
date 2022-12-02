"""fixes organization settings for currencies

Revision ID: aab9ae566158
Revises: 471f3be36c91
Create Date: 2022-01-03 18:29:16.557469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aab9ae566158'
down_revision = '471f3be36c91'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
    """
    UPDATE organizations
    SET data = jsonb_set(data, '{currency}', '"CAD"', TRUE)
    WHERE data->>'currency' IS NULL;


    UPDATE organizations o 
    SET data = jsonb_set(data, '{currency}', to_jsonb(c) , TRUE)
    FROM currencies c
    WHERE o."data" ->>'currency' = c.alphabetic_code;
    """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
    """
    UPDATE organizations o 
    SET data = jsonb_set(data, '{currency}', to_jsonb(c.alphabetic_code), TRUE)
    FROM currencies c
    WHERE o."data"->'currency'->>'alphabetic_code' = c.alphabetic_code;
    """
    )
