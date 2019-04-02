# coding: utf-8

import logging
import logging.handlers
import datetime

from seaserv import get_org_id_by_repo_id, seafile_api, get_commit
from seafobj import CommitDiffer, commit_mgr
from seafevents.events.db import save_user_events, save_org_user_events, \
        save_file_audit_event, save_file_update_event, save_perm_audit_event
from change_file_path import ChangeFilePathHandler

from keeper.cdc.cdc_manager import generate_certificate_by_commit
from keeper.catalog.catalog_manager import generate_catalog_entry_by_repo_id

changer = ChangeFilePathHandler()

def RepoUpdateEventHandler(session, msg):
    elements = msg.body.split('\t')
    if len(elements) != 3:
        logging.warning("got bad message: %s", elements)
        return

    etype = 'repo-update'
    repo_id = elements[1]
    commit_id = elements[2]

    detail =  {'repo_id': repo_id,
               'commit_id': commit_id}

    commit = commit_mgr.load_commit(repo_id, 1, commit_id)
    if commit is None:
        commit = commit_mgr.load_commit(repo_id, 0, commit_id)

    # TODO: maybe handle merge commit.
    if commit is not None and commit.parent_id and not commit.second_parent_id:

        parent = commit_mgr.load_commit(repo_id, commit.version, commit.parent_id)

        if parent is not None:
            differ = CommitDiffer(repo_id, commit.version, parent.root_id, commit.root_id,
                                  True, True)
            added_files, deleted_files, added_dirs, deleted_dirs, modified_files,\
                    renamed_files, moved_files, renamed_dirs, moved_dirs = differ.diff()

            if renamed_files or renamed_dirs or moved_files or moved_dirs:
                for r_file in renamed_files:
                    changer.update_db_records(repo_id, r_file.path, r_file.new_path, 0)
                for r_dir in renamed_dirs:
                    changer.update_db_records(repo_id, r_dir.path, r_dir.new_path, 1)
                for m_file in moved_files:
                    changer.update_db_records(repo_id, m_file.path, m_file.new_path, 0)
                for m_dir in moved_dirs:
                    changer.update_db_records(repo_id, m_dir.path, m_dir.new_path, 1)

    users = []
    org_id = get_org_id_by_repo_id(repo_id)
    if org_id > 0:
        users = seafile_api.org_get_shared_users_by_repo(org_id, repo_id)
        owner = seafile_api.get_org_repo_owner(repo_id)
    else:
        users = seafile_api.get_shared_users_by_repo(repo_id)
        owner = seafile_api.get_repo_owner(repo_id)

    if owner not in users:
        users = users + [owner]
    if not users:
        return

    time = datetime.datetime.utcfromtimestamp(msg.ctime)
    if org_id > 0:
        save_org_user_events(session, org_id, etype, detail, users, time)
    else:
        save_user_events(session, etype, detail, users, time)
    # KEEPER
    logging.info("REPO UPDATED EVENT repo_id: %s" % repo_id)
    logging.info("Trying to create/update keeper catalog entry for repo_id: %s..." % repo_id)
    if bool(generate_catalog_entry_by_repo_id(repo_id)):
        logging.info("Success!")
    else:
        logging.error("Something went wrong...")


def FileUpdateEventHandler(session, msg):
    elements = msg.body.split('\t')
    if len(elements) != 3:
        logging.warning("got bad message: %s", elements)
        return

    repo_id = elements[1]
    commit_id = elements[2]

    org_id = get_org_id_by_repo_id(repo_id)

    commit = get_commit(repo_id, 1, commit_id)
    if commit is None:
        commit = get_commit(repo_id, 0, commit_id)
        if commit is None:
            return

    time = datetime.datetime.utcfromtimestamp(msg.ctime)

    # KEEPER
    logging.info("FILE UPDATE EVENT: %s, try generate_certificate", commit.desc)
    generate_certificate_by_commit(commit)


    save_file_update_event(session, time, commit.creator_name, org_id,
                           repo_id, commit_id, commit.desc)

def FileAuditEventHandler(session, msg):
    elements = msg.body.split('\t')
    if len(elements) != 6:
        logging.warning("got bad message: %s", elements)
        return

    timestamp = datetime.datetime.utcfromtimestamp(msg.ctime)
    msg_type = elements[0]
    user_name = elements[1]
    ip = elements[2]
    user_agent = elements[3]
    repo_id = elements[4]
    file_path = elements[5].decode('utf-8')

    org_id = get_org_id_by_repo_id(repo_id)

    save_file_audit_event(session, timestamp, msg_type, user_name, ip,
                          user_agent, org_id, repo_id, file_path)

def PermAuditEventHandler(session, msg):
    elements = msg.body.split('\t')
    if len(elements) != 7:
        logging.warning("got bad message: %s", elements)
        return

    timestamp = datetime.datetime.utcfromtimestamp(msg.ctime)
    etype = elements[1]
    from_user = elements[2]
    to = elements[3]
    repo_id = elements[4]
    file_path = elements[5].decode('utf-8')
    perm = elements[6]

    org_id = get_org_id_by_repo_id(repo_id)

    save_perm_audit_event(session, timestamp, etype, from_user, to,
                          org_id, repo_id, file_path, perm)

def register_handlers(handlers, enable_audit):
    handlers.add_handler('seaf_server.event:repo-update', RepoUpdateEventHandler)
    if enable_audit:
        handlers.add_handler('seaf_server.event:repo-update', FileUpdateEventHandler)
        handlers.add_handler('seaf_server.event:repo-download-sync', FileAuditEventHandler)
        handlers.add_handler('seaf_server.event:repo-upload-sync', FileAuditEventHandler)
        handlers.add_handler('seaf_server.event:seadrive-download-file', FileAuditEventHandler)

        handlers.add_handler('seahub.audit:file-download-web', FileAuditEventHandler)
        handlers.add_handler('seahub.audit:file-download-api', FileAuditEventHandler)
        handlers.add_handler('seahub.audit:file-download-share-link', FileAuditEventHandler)
        handlers.add_handler('seahub.audit:perm-change', PermAuditEventHandler)
