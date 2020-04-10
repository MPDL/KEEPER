import configparser
import logging
import os
import tempfile

key_enabled = 'enabled'
key_host = 'host'
key_port = 'port'
key_local_storage = 'local_storage'
key_workers = 'workers'
key_archive_max_size = 'archive-max-size'
key_archives_per_library = 'archives-per-library'
key_hpss_enabled = 'hpss_enabled'
key_hpss_url = 'hpss_url'
key_hpss_user = 'hpss_user'
key_hpss_password = 'hpss_password'
key_hpss_storage_path = 'hpss_storage_path'

def parse_workers(workers, default_workers):
    try:
        workers = int(workers)
    except ValueError:
        logging.warning('invalid workers value "{}"'.format(workers))
        workers = default_workers

    if workers <= 0 or workers > 10:
        logging.warning('insane workers value "{}"'.format(workers))
        workers = default_workers

    return workers

def parse_archives_per_library(archs, default_archs):
    try:
       archs = int(archs)
    except ValueError:
        logging.warning('invalid archives_per_library value "%s"' % archs)
        archs = default_archs

    if archs <= 0 or archs > 20:
        logging.warning('insane archives_per_library value "%s"' % archs)
        archs = default_archs

    return archs

def parse_max_size(val, default):
    try:
        val = int(val.lower().rstrip('gb')) * 1024 * 1024 * 1024
    except:
        logging.exception('xxx:')
        val = default

    return val


def parse_bool(v):
    if isinstance(v, bool):
        return v

    v = str(v).lower()

    if v == '1' or v == 'true':
        return True
    else:
        return False

def get_keeper_archiving_conf(config):
    '''Parse search related options from events.conf'''

    section_name = 'KEEPER ARCHIVING'

    default_archiving_storage = os.path.join(tempfile.gettempdir(), 'keeper_archiving_storage')

    default_host = '127.0.0.1'

    default_port = 6001

    default_workers = 1

    default_archive_max_size = 500 * 1024**3

    default_archives_per_library = 5

    default_hpss_storage_path = '/tmp/keeper_archiving_storage'


    d = { key_enabled: False }
    if not config.has_section(section_name):
        return d

    def get_option(key, default=None):
        try:
            value = config.get(section_name, key)
        except configparser.NoOptionError:
            value = default

        return value

    enabled = get_option(key_enabled, default=False)
    enabled = parse_bool(enabled)

    d[key_enabled] = enabled
    logging.debug('archiving enabled: %s', enabled)

    if not enabled:
        return d

    # [ local_storage ]
    local_storage = get_option(key_local_storage, default=default_archiving_storage)

    if not os.path.exists(local_storage):
        logging.error('Keeper archiving storage path {} does not exists, please mkdir manually!'.format(local_storage))
        return { key_enabled: False }

    if not os.access(local_storage, os.R_OK):
        logging.error('Permission Denied: {} is not readable'.format(local_storage))

    if not os.access(local_storage, os.W_OK):
        logging.error('Permission Denied: {} is not allowed to be written.'.format(local_storage))

    # [ workers ]
    workers = get_option(key_workers, default=default_workers)
    workers = parse_workers(workers, default_workers)

    # [ archives_per_library ]
    archives_per_library = get_option(key_archives_per_library, default=default_archives_per_library)
    archives_per_library = parse_archives_per_library(archives_per_library, default_archives_per_library)

    # [ archive_max_size ]
    archive_max_size = get_option(key_archive_max_size, default=default_archive_max_size)
    if archive_max_size != default_archive_max_size:
        archive_max_size = parse_max_size(archive_max_size, default=default_archive_max_size)



    # hpss_enabled
    hpss_enabled = parse_bool(get_option(key_hpss_enabled, default=False))

    # hpss_url
    hpss_url = get_option(key_hpss_url)

    # hpss_user
    hpss_user = get_option(key_hpss_user)

    # hpss_password
    hpss_password = get_option(key_hpss_password)

    # hpss_storage_path
    hpss_storage_path = get_option(key_hpss_storage_path, default=default_hpss_storage_path)

    # [ http server address ]
    host = get_option(key_host, default=default_host)
    port = get_option(key_port, default=default_port)

    logging.debug('keeper archiving workers: {}'.format(workers))
    logging.debug('keeper archiving local_storage: {}'.format(local_storage))
    logging.debug('keeper archiving archives per library: {}'.format(archives_per_library))
    logging.debug('keeper archive max size: {} GB'.format(archive_max_size / 1024 / 1024 / 1024))
    logging.debug('keeper hpss enabled: {} '.format(hpss_enabled))
    logging.debug('keeper archiving http host: {} '.format(host))
    logging.debug('keeper archiving http port: {} '.format(port))
    if hpss_enabled:
        logging.debug('keeper hpss url: {} '.format(hpss_url))
        logging.debug('keeper hpss user: {} '.format(hpss_user))
        logging.debug('keeper hpss storage path: {} '.format(hpss_storage_path))

    d[key_local_storage] = local_storage
    d[key_workers] = workers
    d[key_archive_max_size] = archive_max_size
    d[key_archives_per_library] = archives_per_library

    d[key_hpss_enabled] = hpss_enabled
    d[key_hpss_url] = hpss_url
    d[key_hpss_user] = hpss_user
    d[key_hpss_password] = hpss_password
    d[key_hpss_storage_path] = hpss_storage_path
    d[key_host] = host
    d[key_port] = port

    return d
