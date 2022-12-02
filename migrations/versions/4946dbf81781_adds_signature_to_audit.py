"""adds signature to audit

Revision ID: 4946dbf81781
Revises: 31d9e58d5759
Create Date: 2022-03-22 20:47:11.658503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4946dbf81781'
down_revision = '31d9e58d5759'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        SELECT audit.audit_table('signatures');
        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        DROP TRIGGER IF EXISTS audit_trigger_row on signatures;
        DROP TRIGGER IF EXISTS audit_trigger_stm on signatures;
        """)
