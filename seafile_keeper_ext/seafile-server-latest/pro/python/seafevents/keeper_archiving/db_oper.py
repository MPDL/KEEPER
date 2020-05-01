import logging
import traceback

from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import create_engine, desc
from sqlalchemy.sql import text
from .models import KeeperArchive, KeeperArchiveOwnerQuota, KeeperBase, MAX_UNICODE_TEXT_LEN
from urllib.parse import quote_plus
from sqlalchemy.orm import sessionmaker
from seafevents.db import ping_connection
from sqlalchemy.event import contains as has_event_listener, listen as add_event_listener
from sqlalchemy.pool import Pool

from seahub_settings import CACHES, DATABASES
from django.utils.http import urlquote
from django.utils import timezone

from keeper.common import truncate_str

import pylibmc

# from seahub.notifications.models import get_cache_key_of_unseen_notifications
USER_NOTIFICATION_COUNT_CACHE_PREFIX = 'USER_NOTIFICATION_COUNT_'

MSG_TYPE_KEEPER_ARCHIVING_MSG = 'keeper_archiving_msg'

def normalize_cache_key(value, prefix=None, token=None, max_length=200):
    """Returns a cache key consisten of ``value`` and ``prefix`` and ``token``. Cache key
    must not include control characters or whitespace.
    """
    key = value if prefix is None else prefix + value
    key = key if token is None else key + '_' + token
    return urlquote(key)[:max_length]

def _prepare_md(md):
    if md is None:
        return None;
    return truncate_str(md, max_len=MAX_UNICODE_TEXT_LEN)

def create_db_session(host, port, username, passwd, dbname):
    db_url = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(username, quote_plus(passwd), host, port, dbname)
    # Add pool recycle, or mysql connection will be closed by mysqld if idle
    # for too long.
    kwargs = dict(pool_recycle=300, echo=False, echo_pool=False)

    engine = create_engine(db_url, **kwargs)

    # create tables, if not exist
    if dbname == DATABASES['keeper']['NAME']:
        KeeperBase.metadata.create_all(engine, tables=[KeeperArchive.__table__, KeeperArchiveOwnerQuota.__table__])

    if not has_event_listener(Pool, 'checkout', ping_connection):
        # We use has_event_listener to double check in case we call create_engine
        # multipe times in the same process.
        add_event_listener(Pool, 'checkout', ping_connection)

    return scoped_session(sessionmaker(bind=engine, autocommit=False, expire_on_commit=False))


class DBOper(object):
    '''
    Class for keeper db operations
    '''

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
        '''
        Add seafile user notification entry,  refresh notices counter
        '''
        if to_user and detail:
            try:
                sql = text("INSERT INTO notifications_usernotification ( to_user, msg_type, detail, timestamp, seen ) "
                           "VALUES ( :to_user, '" + MSG_TYPE_KEEPER_ARCHIVING_MSG + "', :detail, :timestamp, 0 )")
                self.edb_session.execute(sql, dict(to_user=to_user, detail=detail, timestamp=timezone.now()))
                self.edb_session.commit()

                # add notification to gui
                cache = pylibmc.Client([CACHES['default']['LOCATION']])
                cache_key = normalize_cache_key(to_user, USER_NOTIFICATION_COUNT_CACHE_PREFIX)
                # django specific versioning
                cache.delete(':1:' + cache_key)

            except Exception as e:
                logging.error(e)
                self.edb_session.rollback()
            finally:
                self.edb_session.remove()

    def delete_archive(self, repo_id, version):
        try:
            a = self.kdb_session.query(KeeperArchive)\
                .filter(KeeperArchive.repo_id == repo_id,
                        KeeperArchive.version == version)\
                .first()
            if a:
                self.kdb_session.delete(a)
                self.kdb_session.commit()
            return 0
        except Exception as e:
            self.kdb_session.rollback()
            logging.warning('Failed to delete keeper archive record from db: {}.'.format(e))
            return -1
        finally:
            self.kdb_session.remove()

    def add_archive(self, repo_id, owner, version, checksum, external_path, md, repo_name, commit_id,
                    status, error_msg):
        try:
            a = KeeperArchive(repo_id, owner, version, checksum, external_path,
                              _prepare_md(md), repo_name, commit_id, status, error_msg)
            self.kdb_session.add(a)
            self.kdb_session.commit()
            return a
        except Exception as e:
            self.kdb_session.rollback()
            logging.warning('Failed to add keeper archive record to db: %s', e.with_traceback())

            return -1
        finally:
            self.kdb_session.remove()

    def add_or_update_archive(self, repo_id, owner, version, checksum, external_path, md, repo_name, commit_id, status, error_msg):
        try:
            q = self.kdb_session.query(KeeperArchive)\
                .filter(KeeperArchive.repo_id == repo_id,
                        KeeperArchive.version == version)
            a = q.first()
            if not a:
                return self.add_archive(repo_id, owner, version, checksum, external_path, md,
                                 repo_name, commit_id, status, error_msg)
            else:
                a.status = status
                if status == 'DONE':
                    a.archived = timezone.now()
                a.checksum = checksum
                a.external_path = external_path
                a.md = _prepare_md(md)
                a.error_msg = error_msg
                self.kdb_session.add(a)
                self.kdb_session.commit()
                return a
        except Exception as e:
            self.kdb_session.rollback()
            logging.warning('Failed to update keeper archive record from db: {}.'.format(e))
        finally:
            self.kdb_session.remove()

    def get_archive(self, aid):
        try:
            q = self.kdb_session.query(KeeperArchive).filter(KeeperArchive.aid == aid)
            return q.first()
        except Exception as e:
            logging.warning('Failed to get keeper archive: {}.'.format(e))
            return None
        finally:
            self.kdb_session.remove()

    def is_snapshot_archived(self, repo_id, commit_id):
        try:
            archive = self.kdb_session.query(KeeperArchive)\
                .filter(KeeperArchive.repo_id == repo_id,
                        KeeperArchive.commit_id == commit_id,
                        KeeperArchive.status == 'DONE')\
                .first()
            return archive is not None
        except Exception as e:
            logging.warning('Failed to get keeper archive: {}.'.format(e))
            return None
        finally:
            self.kdb_session.remove()

    def get_max_archive_version(self, repo_id, owner):
        try:
            archive = self.kdb_session.query(KeeperArchive)\
                .filter(KeeperArchive.repo_id == repo_id,
                    KeeperArchive.owner == owner,
                    KeeperArchive.status == 'DONE')\
                .order_by(desc(KeeperArchive.version))\
                .first()
            if not archive:
                return -1
            else:
                return archive.version
        except Exception as e:
            logging.warning('Failed to get max version of keeper archive for repo {}: {}.'\
                            .format(repo_id, e))
            return None
        finally:
            self.kdb_session.remove()

    def get_quota(self, repo_id, owner):
        try:
            archive = self.kdb_session.query(KeeperArchiveOwnerQuota)\
                .filter(KeeperArchiveOwnerQuota.repo_id == repo_id,
                        KeeperArchiveOwnerQuota.owner == owner,
                        KeeperArchive.status == 'DONE')\
                .first()
            if not archive:
                return None
            else:
                return archive.quota
        except Exception as e:
            logging.warning('Failed to get archiving quota for library {} and owner {}: {}.'\
                            .format(repo_id, owner, e))
            return None
        finally:
            self.kdb_session.remove()

    def get_latest_archive(self, repo_id, version=None):
        try:
            q = self.kdb_session.query(KeeperArchive)\
                .filter(KeeperArchive.repo_id == repo_id)
            if version:
                q = q.filter(KeeperArchive.version == version)
            q = q.order_by(desc(KeeperArchive.version))
            return q.first()
        except Exception as e:
            logging.warning('Failed to get latest archive for library {}: {}.'\
                            .format(repo_id, e))
            return None
        finally:
            self.kdb_session.remove()


    def get_not_completed_tasks(self):
        try:
            q = self.kdb_session.query(KeeperArchive)\
                .filter(KeeperArchive.status != 'DONE')\
                .order_by(desc(KeeperArchive.created))
            return q.all()
        except Exception as e:
            logging.warning('Failed to get not completed tasks: {}.'\
                            .format(e))
            return None
        finally:
            self.kdb_session.remove()

    def get_archives(self, repo_id=None, version=None, owner=None):
        try:
            q = self.kdb_session.query(KeeperArchive)
            if repo_id:
                q = q.filter(KeeperArchive.repo_id == repo_id)
            if version:
                q = q.filter(KeeperArchive.version == version)
            if owner:
                q = q.filter(KeeperArchive.owner == owner)
            return q.all()
        except Exception as e:
            logging.warning(
                'Failed to get keeper archives for repo {}, version {}, owner {}: {}.'\
                .format(repo_id, version, owner, e))
            return None
        finally:
            self.kdb_session.remove()
