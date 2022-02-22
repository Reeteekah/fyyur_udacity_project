"""empty message

Revision ID: 95c8c3e81796
Revises: f099e29512f0
Create Date: 2022-02-21 16:44:41.567054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95c8c3e81796'
down_revision = 'f099e29512f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.alter_column('venue', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('artist', 'seeking_venue')
    # ### end Alembic commands ###