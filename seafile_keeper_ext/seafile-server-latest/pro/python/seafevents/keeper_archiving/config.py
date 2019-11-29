import os
import logging
import ConfigParser
import tempfile

def parse_workers(workers, default_workers):
    try:
        workers = int(workers)
    except ValueError:
        logging.warning('invalid workers value "%s"' % workers)
        workers = default_workers

    if workers <= 0 or workers > 5:
        logging.warning('insane workers value "%s"' % workers)
        workers = default_workers

    return workers

def parse_archives_per_library(archs, default_archs):
    try:
       archs = int(archs)
    except ValueError:
        logging.warning('invalid archives_per_library value "%s"' % archs)
        archs = default_archs

    if archs <= 0 or archs > 5:
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
    key_enabled = 'enabled'

    key_archiving_storage = 'archiving_storage'
    default_archiving_storage = os.path.join(tempfile.gettempdir(), 'keeper_archiving_storage')

    key_workers = 'workers'
    default_workers = 1

    key_archive_max_size = 'archive-max-size'
    default_archive_max_size = 500 * 1024 * 1024 * 1024

    key_archives_per_library = 'archives-per-library'
    default_archives_per_library = 5

    d = { key_enabled: False }
    if not config.has_section(section_name):
        return d

    def get_option(key, default=None):
        try:
            value = config.get(section_name, key)
        except ConfigParser.NoOptionError:
            value = default

        return value

    enabled = get_option(key_enabled, default=False)
    enabled = parse_bool(enabled)

    d[key_enabled] = enabled
    logging.debug('archiving enabled: %s', enabled)

    if not enabled:
        return d

    # [ archiving_storage ]
    archiving_storage = get_option(key_archiving_storage, default=default_archiving_storage)

    if not os.path.exists(archiving_storage):
        logging.error('Keeper archiving storage path {} does not exists, please mkdir manually!'.format(archiving_storage))
        return { key_enabled: False }

    if not os.access(archiving_storage, os.R_OK):
        logging.error('Permission Denied: {} is not readable'.format(archiving_storage))

    if not os.access(archiving_storage, os.W_OK):
        logging.error('Permission Denied: {} is not allowed to be written.'.format(archiving_storage))

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

    logging.debug('keeper archiving workers: {}'.format(workers))
    logging.debug('keeper archiving archiving_storage: {}'.format(archiving_storage))
    logging.debug('keeper archiving archives per library: {}'.format(archives_per_library))
    logging.debug('keeper archive max size: {} GB'.format(archive_max_size / 1024 / 1024 / 1024))

    d[key_archiving_storage] = archiving_storage
    d[key_workers] = workers
    d[key_archive_max_size] = archive_max_size
    d[key_archives_per_library] = archives_per_library

    return d


