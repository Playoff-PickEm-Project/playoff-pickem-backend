"""remove prop_limit server default

Revision ID: fix_prop_limit_2026
Revises: 7f71240d9d35
Create Date: 2026-01-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_prop_limit_2026'
down_revision = 'c7b04f07f906'
branch_labels = None
depends_on = None


def upgrade():
    # Remove server default from prop_limit column
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.alter_column('prop_limit',
               existing_type=sa.INTEGER(),
               server_default=None,
               nullable=False)


def downgrade():
    # Restore server default
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.alter_column('prop_limit',
               existing_type=sa.INTEGER(),
               server_default='2',
               nullable=False)
