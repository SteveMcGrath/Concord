from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
submissions = Table('submissions', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('user_id', INTEGER),
    Column('accepted', BOOLEAN),
    Column('status', VARCHAR(length=16)),
    Column('abstract', TEXT),
    Column('title', VARCHAR(length=255)),
    Column('outline', TEXT),
    Column('tool', BOOLEAN),
    Column('exploit', BOOLEAN),
    Column('panel', BOOLEAN),
    Column('demo', BOOLEAN),
    Column('time', INTEGER),
    Column('training', BOOLEAN),
    Column('new_talk', BOOLEAN),
    Column('needs', TEXT),
    Column('track', VARCHAR(length=32)),
    Column('seats', INTEGER),
    Column('tod', DATETIME),
    Column('review_rating', INTEGER),
    Column('review_notes', TEXT),
)

user_subs = Table('user_subs', pre_meta,
    Column('user_id', INTEGER),
    Column('submission_id', INTEGER),
)

discountcodes = Table('discountcodes', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('uses', Integer, default=ColumnDefault(0)),
    Column('code', Text),
    Column('t_type', Text, default=ColumnDefault('attendee')),
    Column('price', Integer),
)

purchases = Table('purchases', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ref_hash', Text),
    Column('email', Text),
    Column('opt_in', Boolean, default=ColumnDefault(True)),
    Column('price', Integer),
    Column('ticket_type', Text),
    Column('discountcode', Text),
    Column('payment_type', Text),
    Column('payment_token', Text),
    Column('completed', Boolean, default=ColumnDefault(False)),
    Column('redeemed', Boolean, default=ColumnDefault(False)),
)

ticket_purchases = Table('ticket_purchases', post_meta,
    Column('purchase_id', Integer),
    Column('tickets_id', Integer),
)

tickets = Table('tickets', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('ticket_type', TEXT),
    Column('ticket_hash', TEXT),
    Column('redeem_hash', TEXT),
    Column('email', TEXT),
    Column('opt_in', BOOLEAN),
    Column('price', INTEGER),
    Column('user_id', INTEGER),
    Column('redeemed', BOOLEAN),
    Column('training_id', INTEGER),
)

tickets = Table('tickets', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ticket_type', Text, default=ColumnDefault('attendee')),
    Column('purchase_id', Integer),
    Column('ticket_hash', Text),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['submissions'].drop()
    pre_meta.tables['user_subs'].drop()
    post_meta.tables['discountcodes'].create()
    post_meta.tables['purchases'].create()
    post_meta.tables['ticket_purchases'].create()
    pre_meta.tables['tickets'].columns['email'].drop()
    pre_meta.tables['tickets'].columns['opt_in'].drop()
    pre_meta.tables['tickets'].columns['price'].drop()
    pre_meta.tables['tickets'].columns['redeem_hash'].drop()
    pre_meta.tables['tickets'].columns['redeemed'].drop()
    pre_meta.tables['tickets'].columns['training_id'].drop()
    post_meta.tables['tickets'].columns['purchase_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['submissions'].create()
    pre_meta.tables['user_subs'].create()
    post_meta.tables['discountcodes'].drop()
    post_meta.tables['purchases'].drop()
    post_meta.tables['ticket_purchases'].drop()
    pre_meta.tables['tickets'].columns['email'].create()
    pre_meta.tables['tickets'].columns['opt_in'].create()
    pre_meta.tables['tickets'].columns['price'].create()
    pre_meta.tables['tickets'].columns['redeem_hash'].create()
    pre_meta.tables['tickets'].columns['redeemed'].create()
    pre_meta.tables['tickets'].columns['training_id'].create()
    post_meta.tables['tickets'].columns['purchase_id'].drop()
