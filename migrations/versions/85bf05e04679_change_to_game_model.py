"""change to game model

Revision ID: 85bf05e04679
Revises: 0b6dac8dbfe1
Create Date: 2025-01-05 01:02:02.549129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85bf05e04679'
down_revision = '0b6dac8dbfe1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('winner_loser_prop', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_team', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('underdog_team', sa.String(length=100), nullable=True))
        batch_op.drop_column('option_two')
        batch_op.drop_column('option_one')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('winner_loser_prop', schema=None) as batch_op:
        batch_op.add_column(sa.Column('option_one', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('option_two', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.drop_column('underdog_team')
        batch_op.drop_column('favorite_team')

    # ### end Alembic commands ###
