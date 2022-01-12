import os
import configparser
import logging
import uuid
from urllib.parse import quote_plus

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.event import contains as has_event_listener, listen as add_event_listener
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool
from sqlalchemy.ext.automap import automap_base

logger = logging.getLogger(__name__)

## base class of model classes in events.models and stats.models
Base = declarative_base()
SeafBase = automap_base()

def create_mysql_session(host, port, username, passwd, dbname):
    db_url = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8" % (username, quote_plus(passwd), host, port, dbname)
    # Add pool recycle, or mysql connection will be closed by mysqld if idle
    # for too long.
    kwargs = dict(pool_recycle=300, echo=False, echo_pool=False)

    engine = create_engine(db_url, **kwargs)

    if not has_event_listener(Pool, 'checkout', ping_connection):
        # We use has_event_listener to double check in case we call create_engine
        # multipe times in the same process.
        add_event_listener(Pool, 'checkout', ping_connection)

    Session = sessionmaker(bind=engine)
    return Session

def create_engine_from_conf(config_file, db = 'seafevent'):
    config = configparser.ConfigParser()
    config.read(config_file)

    need_connection_pool_fix = True

    db_sec = 'DATABASE'
    user = 'username'
    db_name = 'name'

    if db == 'seafile':
        db_sec = 'database'
        user = 'user'
        db_name = 'db_name'

    backend = config.get(db_sec, 'type')
    if backend == 'sqlite' or backend == 'sqlite3':
        path = config.get(db_sec, 'path')
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(config_file), path)
        db_url = "sqlite:///%s" % path
        logger.info('[seafevents] database: sqlite3, path: %s', path)
        need_connection_pool_fix = False
    elif backend == 'mysql':
        if config.has_option(db_sec, 'host'):
            host = config.get(db_sec, 'host').lower()
        else:
            host = 'localhost'

        if config.has_option(db_sec, 'port'):
            port = config.getint(db_sec, 'port')
        else:
            port = 3306
        username = config.get(db_sec, user)
        passwd = config.get(db_sec, 'password')
        dbname = config.get(db_sec, db_name)
        db_url = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8" % (username, quote_plus(passwd), host, port, dbname)
        logger.info('[seafevents] database: mysql, name: %s', dbname)
    elif backend == 'oracle':
        if config.has_option(db_sec, 'host'):
            host = config.get(db_sec, 'host').lower()
        else:
            host = 'localhost'

        if config.has_option(db_sec, 'port'):
            port = config.getint(db_sec, 'port')
        else:
            port = 1521
        username = config.get(db_sec, user)
        passwd = config.get(db_sec, 'password')
        service_name = config.get(db_sec, 'service_name')
        db_url = "oracle://%s:%s@%s:%s/%s" % (username, quote_plus(passwd),
                host, port, service_name)

        logger.info('[seafevents] database: oracle, service_name: %s', service_name)
    else:
        logger.error("Unknown database backend: %s" % backend)
        raise RuntimeError("Unknown database backend: %s" % backend)

    # Add pool recycle, or mysql connection will be closed by mysqld if idle
    # for too long.
    kwargs = dict(pool_recycle=300, echo=False, echo_pool=False)

    engine = create_engine(db_url, **kwargs)

    if need_connection_pool_fix and not has_event_listener(Pool, 'checkout', ping_connection):
        # We use has_event_listener to double check in case we call create_engine
        # multipe times in the same process.
        add_event_listener(Pool, 'checkout', ping_connection)

    return engine

def init_db_session_class(config_file, db = 'seafevent'):
    """Configure Session class for mysql according to the config file."""
    try:
        engine = create_engine_from_conf(config_file, db)
    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        logger.error(e)
        raise RuntimeError("invalid config file %s", config_file)

    if db == 'seafile':
        # reflect the tables
        SeafBase.prepare(engine, reflect=True)

    Session = sessionmaker(bind=engine)
    return Session


def create_db_tables():
    # create seafevents tables if not exists.
    config_file = os.environ.get('EVENTS_CONFIG_FILE')

    try:
        engine = create_engine_from_conf(config_file)
    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        logger.error(e)
        raise RuntimeError("invalid config file %s", config_file)

    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error("Failed to create database tables: %s" % e)
        raise RuntimeError("Failed to create database tables")


# This is used to fix the problem of "MySQL has gone away" that happens when
# mysql server is restarted or the pooled connections are closed by the mysql
# server beacause being idle for too long.
#
# See http://stackoverflow.com/a/17791117/1467959
def ping_connection(dbapi_connection, connection_record, connection_proxy): # pylint: disable=unused-argument
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
        cursor.close()
    except:
        logger.info('fail to ping database server, disposing all cached connections')
        connection_proxy._pool.dispose() # pylint: disable=protected-access

        # Raise DisconnectionError so the pool would create a new connection
        raise DisconnectionError()


class GroupIdLDAPUuidPair(Base):
    """
    """
    __tablename__ = 'GroupIdLDAPUuidPair'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, unique=True, nullable=False)
    group_uuid = Column(String(36), default=uuid.uuid4, unique=True, nullable=False)


    def __init__(self, record):
        self.group_id = record['group_id']
        self.group_uuid = record['group_uuid']

    def __str__(self):
        return 'GroupIdLDAPUuidPair<id: %s, group_id: %s, group_uuid: %s>' % \
            (self.id, self.group_id, self.group_uuid)