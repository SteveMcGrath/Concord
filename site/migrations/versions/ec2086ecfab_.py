"""empty message

Revision ID: ec2086ecfab
Revises: None
Create Date: 2015-03-02 10:55:27.191899

"""

# revision identifiers, used by Alembic.
revision = 'ec2086ecfab'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=32), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('discountcodes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uses', sa.Integer(), nullable=True),
    sa.Column('code', sa.Text(), nullable=True),
    sa.Column('t_type', sa.Text(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('limit', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('purchases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ref_hash', sa.Text(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('ticket_type', sa.Text(), nullable=True),
    sa.Column('purchase_type', sa.Text(), nullable=True),
    sa.Column('discountcode', sa.Text(), nullable=True),
    sa.Column('payment_type', sa.Text(), nullable=True),
    sa.Column('payment_token', sa.Text(), nullable=True),
    sa.Column('children', sa.Integer(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('train_purchases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ref_hash', sa.Text(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('payment_type', sa.Text(), nullable=True),
    sa.Column('payment_token', sa.Text(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('body_md', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('draft', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_type', sa.Text(), nullable=True),
    sa.Column('purchase_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('ticket_hash', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('redeemed', sa.Boolean(), nullable=True),
    sa.Column('marketing', sa.Boolean(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('company', sa.Text(), nullable=True),
    sa.Column('phone', sa.Text(), nullable=True),
    sa.Column('twitter', sa.Text(), nullable=True),
    sa.Column('linkedin', sa.Text(), nullable=True),
    sa.Column('facebook', sa.Text(), nullable=True),
    sa.Column('shirt', sa.Text(), nullable=True),
    sa.Column('fri_party', sa.Boolean(), nullable=True),
    sa.Column('sat_party', sa.Boolean(), nullable=True),
    sa.Column('thu_hfd', sa.Boolean(), nullable=True),
    sa.Column('fri_hfd', sa.Boolean(), nullable=True),
    sa.Column('sat_hfd', sa.Boolean(), nullable=True),
    sa.Column('helpus', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('seats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('tag', sa.Text(), nullable=True),
    sa.Column('sub', sa.Text(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.Column('purchase_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['purchase_id'], ['train_purchases.id'], ),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_purchases',
    sa.Column('purchase_id', sa.Integer(), nullable=True),
    sa.Column('tickets_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['purchase_id'], ['purchases.id'], ),
    sa.ForeignKeyConstraint(['tickets_id'], ['tickets.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ticket_purchases')
    op.drop_table('seats')
    op.drop_table('tickets')
    op.drop_table('posts')
    op.drop_table('train_purchases')
    op.drop_table('purchases')
    op.drop_table('ticket_types')
    op.drop_table('discountcodes')
    op.drop_table('users')
    ### end Alembic commands ###