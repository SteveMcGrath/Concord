from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
purchases = Table('purchases', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('ref_hash', Text),
    Column('email', Text),
    Column('opt_in', Boolean, default=ColumnDefault(True)),
    Column('price', Integer),
    Column('children', Integer, default=ColumnDefault(0)),
    Column('name', Text),
    Column('company', Text),
    Column('phone', Text),
    Column('twitter', Text),
    Column('linkedin', Text),
    Column('facebook', Text),
    Column('fri_party', Boolean),
    Column('sat_party', Boolean),
    Column('thu_hfd', Boolean),
    Column('fru_hfd', Boolean),
    Column('sat_hfd', Boolean),
    Column('helpus', Text),
    Column('ticket_type', Text),
    Column('discountcode', Text),
    Column('payment_type', Text),
    Column('payment_token', Text),
    Column('completed', Boolean, default=ColumnDefault(False)),
    Column('redeemed', Boolean, default=ColumnDefault(False)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['purchases'].columns['children'].create()
    post_meta.tables['purchases'].columns['company'].create()
    post_meta.tables['purchases'].columns['facebook'].create()
    post_meta.tables['purchases'].columns['fri_party'].create()
    post_meta.tables['purchases'].columns['fru_hfd'].create()
    post_meta.tables['purchases'].columns['helpus'].create()
    post_meta.tables['purchases'].columns['linkedin'].create()
    post_meta.tables['purchases'].columns['name'].create()
    post_meta.tables['purchases'].columns['phone'].create()
    post_meta.tables['purchases'].columns['sat_hfd'].create()
    post_meta.tables['purchases'].columns['sat_party'].create()
    post_meta.tables['purchases'].columns['thu_hfd'].create()
    post_meta.tables['purchases'].columns['twitter'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['purchases'].columns['children'].drop()
    post_meta.tables['purchases'].columns['company'].drop()
    post_meta.tables['purchases'].columns['facebook'].drop()
    post_meta.tables['purchases'].columns['fri_party'].drop()
    post_meta.tables['purchases'].columns['fru_hfd'].drop()
    post_meta.tables['purchases'].columns['helpus'].drop()
    post_meta.tables['purchases'].columns['linkedin'].drop()
    post_meta.tables['purchases'].columns['name'].drop()
    post_meta.tables['purchases'].columns['phone'].drop()
    post_meta.tables['purchases'].columns['sat_hfd'].drop()
    post_meta.tables['purchases'].columns['sat_party'].drop()
    post_meta.tables['purchases'].columns['thu_hfd'].drop()
    post_meta.tables['purchases'].columns['twitter'].drop()
