"""empty message

Revision ID: 3ce8fc45a018
Revises: 95c8c3e81796
Create Date: 2022-02-21 16:45:22.573669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ce8fc45a018'
down_revision = '95c8c3e81796'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'seeking_description')
    # ### end Alembic commands ###
