#coding: utf-8

import logging
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import create_engine, desc
from models import KeeperArchive, KeeperArchiveOwnerQuota, KeeperBase
from urllib import quote_plus
from sqlalchemy.orm import sessionmaker
from seafevents.db import ping_connection
from sqlalchemy.event import contains as has_event_listener, listen as add_event_listener
from sqlalchemy.pool import Pool

from seahub.utils import normalize_cache_key
from seahub_settings import CACHES, DATABASES

from datetime import datetime

import pylibmc
# from seahub.notifications.models import get_cache_key_of_unseen_notifications
USER_NOTIFICATION_COUNT_CACHE_PREFIX = 'USER_NOTIFICATION_COUNT_'

MSG_TYPE_KEEPER_ARCHIVING_MSG = 'keeper_archiving_msg'

def create_db_session(host, port, username, passwd, dbname):
    db_url = "mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8".format(username, quote_plus(passwd), host, port, dbname)
    # Add pool recycle, or mysql connection will be closed by mysqld if idle
    # for too long.
    logging.info(db_url)
    kwargs = dict(pool_recycle=300, echo=False, echo_pool=False )

    engine = create_engine(db_url, **kwargs)

    # create tables, if not exist
    if dbname == DATABASES['keeper']['NAME']:
        KeeperBase.metadata.create_all(engine, tables=[KeeperArchive.__table__, KeeperArchiveOwnerQuota.__table__])

    if not has_event_listener(Pool, 'checkout', ping_connection):
        # We use has_event_listener to double check in case we call create_engine
        # multipe times in the same process.
        add_event_listener(Pool, 'checkout', ping_connection)

    return scoped_session(sessionmaker(bind=engine, autocommit=True, expire_on_commit=False))

class DBOper(object):
    def __init__(self):
        self.is_enabled = False
        self.kdb_session = None
        self.edb_session = None
        self.init_db()

    def init_db(self):

        try:
            kdb = DATABASES['keeper']
            self.kdb_session = create_db_session(
                kdb['HOST'], kdb['PORT'], kdb['USER'], kdb['PASSWORD'], kdb['NAME'],
            )

            edb = DATABASES['default']
            self.edb_session = create_db_session(
                edb['HOST'], edb['PORT'], edb['USER'], edb['PASSWORD'], edb['NAME'],
            )

            self.is_enabled = True
        except Exception as e:
            logging.info('Failed to init mysql db: {}, stop keeper archiving.'.format(e))
            if self.kdb_session:
                self.kdb_session.remove()
            if self.edb_session:
                self.edb_session.remove()

    def is_enabled(self):
        return self.is_enabled

    def close_db(self):
        if self.is_enabled:
            self.kdb_session.remove()
            self.edb_session.remove()


    def add_user_notification(self, to_user, detail):
        if to_user and detail:
            try:
                cmd = 'INSERT INTO notifications_usernotification ( to_user, msg_type, detail, timestamp, seen ) VALUES ( \'{}\', \'{}\', \'{}\', \'{}\', 0 )'.format(
                    to_user,
                    MSG_TYPE_KEEPER_ARCHIVING_MSG,
                    detail,
                    datetime.now(),
                )
                self.edb_session.execute(cmd)

                # add notification to gui
                cache = pylibmc.Client([CACHES['default']['LOCATION']])
                cache_key = normalize_cache_key(to_user, USER_NOTIFICATION_COUNT_CACHE_PREFIX)
                cache.delete(':1:' + cache_key)

            except Exception as e:
                logging.error(e)
                self.edb_session.rollback()
            finally:
                self.edb_session.remove()


    def add_archive(self, repo_id, owner, version, checksum, external_path, md):
        try:
            a = KeeperArchive(repo_id, owner, version, checksum, external_path, md)
            self.kdb_session.add(a)
            self.kdb_session.flush()
            return 0
        except Exception as e:
            self.kdb_session.rollback()
            logging.warning('Failed to add keeper archive record to db: {}.'.format(e))
            return -1
        finally:
            self.kdb_session.remove()


    def update_archive(self, repo_id, owner, version, checksum, external_path, md, ts):
        try:
            q = self.kdb_session.query(KeeperArchive).filter(KeeperArchive.repo_id == repo_id, KeeperArchive.version == version)
            a = q.first()
            if not a:
                self.add_archive(repo_id, owner, version, checksum, external_path, md)
            else:
                a.owner = owner
                a.checksum = checksum
                a.external_path = external_path
                a.md = md
                a.timestamp = ts
                a.commit()

        except Exception as e:
            self.kdb_session.rollback()
            logging.warning('Failed to update keeper archive record from db: {}.'.format(e))
        finally:
            self.kdb_session.remove()



    def get_archive_by_id(self, aid):
        try:
            q = self.kdb_session.query(KeeperArchive).filter(KeeperArchive.aid == aid)
            return q.first()
        except Exception as e:
            logging.warning('Failed to get keeper archive: {}.'.format(e))
            return None
        finally:
            self.kdb_session.remove()


    def get_max_archive_version(self, repo_id):
        try:
            q = self.kdb_session.query(KeeperArchive).filter(KeeperArchive.repo_id == repo_id).order_by(desc(KeeperArchive.version)).first()
            if not q:
                return -1
            else:
                return q.version
        except Exception as e:
            logging.warning('Failed to get max version of keeper archive for repo {}: {}.'.format(repo_id, e))
            return None
        finally:
            self.kdb_session.remove()



    def get_archives(self, repo_id=None, version=None):
        try:
            q = self.kdb_session.query(KeeperArchive)
            if repo_id:
                q = q.filter(KeeperArchive.repo_id == repo_id)
            if version:
                q = q.filter(KeeperArchive.version == version)
            return q.all()
        except Exception as e:
            logging.warning('Failed to get keeper archives for repo {}, version {} : {}.'.format(repo_id, version, e))
            return None
        finally:
            self.kdb_session.remove()

