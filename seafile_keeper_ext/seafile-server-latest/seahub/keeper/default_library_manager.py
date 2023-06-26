import logging
import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

from seaserv import seafile_api
from seahub.settings import DEBUG, SERVER_EMAIL, KEEPER_DEFAULT_LIBRARY, SEAFILE_DIR, ARCHIVE_METADATA_TARGET


def create_keeper_default_library():
    """ create keeper default library
        and put CDC files into it
    """
    # create repo
    repo_id = seafile_api.create_repo(KEEPER_DEFAULT_LIBRARY, "The library is used for keeper CDC generation", SERVER_EMAIL, passwd=None)
    if repo_id:
        # add CDC files
        dir_path = os.path.join(SEAFILE_DIR, 'seafile-server-latest', 'seahub', 'keeper', 'cdc')
        for fn in (ARCHIVE_METADATA_TARGET, 'Cared-Data-Certificate-HowTo.pdf'):
            path = os.path.join(dir_path, fn)
            if os.path.isfile(path):
                seafile_api.post_file(repo_id, path, "/", fn, SERVER_EMAIL)
            else:
                logging.error("File {} does not exist.".format(path))
                return None
        return repo_id
    else:
        return None

def get_keeper_default_library():
    try:
        from_repos = seafile_api.get_owned_repo_list(SERVER_EMAIL)
        from_repos = [r for r in from_repos if r.name == KEEPER_DEFAULT_LIBRARY]
        if from_repos:
            from_repo_id = from_repos[0].id
        else:
            logging.info("Cannot find KEEPER_DEFAULT_LIBRARY repo in admin libraries, trying to create...")
            from_repo_id = create_keeper_default_library()
            if from_repo_id is None:
                raise Exception("Cannot create KEEPER_DEFAULT_LIBRARY repo in admin libraries, please check!")
            else:
                logging.info("KEEPER_DEFAULT_LIBRARY has been successfully created!")
        return { 'repo_id': from_repo_id, 'dirents': seafile_api.list_dir_by_path(from_repo_id, '/') }
    except Exception as err:
        logging.error("Cannot find KEEPER_DEFAULT_LIBRARY dirents, err: " + str(err))
        return None

def copy_keeper_default_library(to_repo_id):
    logging.info("Add KEEPER_DEFAULT_LIBRARY files to the repo %s..." % to_repo_id)
    try:
        kdl = get_keeper_default_library()
        if kdl:
            for e in kdl['dirents']:
                obj_name = e.obj_name
                seafile_api.copy_file(kdl['repo_id'], '/', json.dumps([obj_name]), to_repo_id, '/',
                                  json.dumps([obj_name]), SERVER_EMAIL, 0, 0)
            logging.info("KEEPER_DEFAULT_LIBRARY has been successfully copied to repo: " + to_repo_id)
    except Exception as err:
        logging.error("Cannot copy KEEPER_DEFAULT_LIBRARY, err: " + str(err))

# if DEBUG:
#     copy_keeper_default_library('d1fe0133-25f2-4ce3-b5c1-055f1ec9716d')
