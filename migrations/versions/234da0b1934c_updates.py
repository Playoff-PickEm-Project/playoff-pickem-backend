"""updates

Revision ID: 234da0b1934c
Revises: 205175c4bee3
Create Date: 2024-12-28 22:44:14.814925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234da0b1934c'
down_revision = '205175c4bee3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('league', schema=None) as batch_op:
        batch_op.drop_constraint('league_commissioner_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'player', ['commissioner_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('league', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('league_commissioner_id_fkey', 'user', ['commissioner_id'], ['id'])

    # ### end Alembic commands ###
