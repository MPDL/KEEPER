import logging
from seahub.api2.utils import json_response
from seafobj import commit_mgr, fs_mgr
from seaserv import seafile_api, get_repo
from keeper.common import parse_markdown
from seahub.settings import SERVICE_URL, SERVER_EMAIL, ARCHIVE_METADATA_TARGET
from keeper.cdc.cdc_manager import validate

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)
TEMPLATE_DESC = u"Template for creating 'My Libray' for users"

def get_metadata(repo_id):
    """ Read metadata from libray root folder"""
    event = None

    repo = seafile_api.get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    # exit if repo encrypted
    if repo.encrypted:
        return False

    # exit if repo is system template
    if repo.rep_desc == TEMPLATE_DESC:
        return False

    try:
        dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
        file = dir.lookup(ARCHIVE_METADATA_TARGET)

        if not file:
            return False
        LOGGER.info('Repo has creative dirents')
        owner = seafile_api.get_repo_owner(repo.id)
        LOGGER.info("Certifying repo id: %s, name: %s, owner: %s ..." % (repo.id, repo.name, owner))
        metadata = parse_markdown(file.get_content())
        isValidate = validate(metadata)
        LOGGER.info(metadata)
        LOGGER.info(isValidate)
        return metadata

    except Exception as err:
        LOGGER.error(str(err))
        raise err    