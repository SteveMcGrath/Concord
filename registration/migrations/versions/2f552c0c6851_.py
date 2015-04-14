"""empty message

Revision ID: 2f552c0c6851
Revises: None
Create Date: 2015-03-04 18:02:30.732433

"""

# revision identifiers, used by Alembic.
revision = '2f552c0c6851'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_type', sa.Text(), nullable=True),
    sa.Column('ticket_hash', sa.Text(), nullable=True),
    sa.Column('redeemed', sa.Boolean(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tickets')
    ### end Alembic commands ###