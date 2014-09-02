#!/usr/bin/env python
import imp
import sys
import os.path
from migrate.versioning import api
from app import db
from app.models import *
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

def create_db(*opts):
    '''
    Creates a clean Database based off the models.
    '''
    db.create_all()
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, 
                            api.version(SQLALCHEMY_MIGRATE_REPO))
    try:
        import prepopulate
    except:
        print '[!] No prepopulate.py, will start with a blank DB.'
    else:
        prepopulate.run()


def migrate_db(*opts):
    '''
    Migrates the Database to what the current codebase expects.
    '''
    migration = ''.join([SQLALCHEMY_MIGRATE_REPO, 
                        '/versions/%03d_migration.py' % (\
                            api.db_version(SQLALCHEMY_DATABASE_URI, 
                                           SQLALCHEMY_MIGRATE_REPO) + 1)])

    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI, 
                                 SQLALCHEMY_MIGRATE_REPO)

    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, 
                                              SQLALCHEMY_MIGRATE_REPO, 
                                              tmp_module.meta, 
                                              db.metadata)
    open(migration, "wt").write(script)
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    print 'New migration saved as ' + migration
    print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, 
                                                            SQLALCHEMY_MIGRATE_REPO))


def upgrade_db(*opts):
    '''
    Upgrades the Database to current.
    '''
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, 
                                                            SQLALCHEMY_MIGRATE_REPO))


def downgrade_db(*opts):
    '''
    Downgrades the Database 1 rev.
    '''
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, 
                                                            SQLALCHEMY_MIGRATE_REPO))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'create':
            create_db(*sys.argv[1:])
        if sys.argv[1] == 'gen_migration':
            migrate_db(*sys.argv[1:])
        if sys.argv[1] == 'upgrade':
            upgrade_db(*sys.argv[1:])
        if sys.argv[1] == 'downgrade':
            downgrade_db(*sys.argv[1:])
    else:
        print '\n'.join(['Available options',
            'create',
            'gen_migration',
            'upgrade',
            'downgrade',
        ])