# coding: utf-8

import os
import copy
import logging
import logging.handlers
import datetime
from urllib import request, parse
from datetime import timedelta
from os.path import splitext

from seaserv import get_org_id_by_repo_id, seafile_api, get_commit
from seafobj import CommitDiffer, commit_mgr, fs_mgr
from seafobj.commit_differ import DiffEntry
from seafevents.events.db import save_file_audit_event, save_file_update_event, \
        save_perm_audit_event, save_user_activity, save_filehistory, update_user_activity_timestamp
from seafevents.app.config import appconfig
from seafevents.events.change_file_path import ChangeFilePathHandler
from seafevents.events.models import Activity

# KEEPER
from keeper.cdc.cdc_manager import generate_certificate_by_commit
from keeper.catalog.catalog_manager import generate_catalog_entry_by_repo_id


def RepoUpdateEventHandler(session, msg):
    elements = msg['content'].split('\t')
    if len(elements) != 3:
        logging.warning("got bad message: %s", elements)
        return

    repo_id = elements[1]
    commit_id = elements[2]

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
                changer = ChangeFilePathHandler()
                for r_file in renamed_files:
                    changer.update_db_records(repo_id, r_file.path, r_file.new_path, 0)
                for r_dir in renamed_dirs:
                    changer.update_db_records(repo_id, r_dir.path, r_dir.new_path, 1)
                for m_file in moved_files:
                    changer.update_db_records(repo_id, m_file.path, m_file.new_path, 0)
                for m_dir in moved_dirs:
                    changer.update_db_records(repo_id, m_dir.path, m_dir.new_path, 1)
                changer.close_session()

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

            time = datetime.datetime.utcfromtimestamp(msg['ctime'])
            if added_files or deleted_files or added_dirs or deleted_dirs or \
                    modified_files or renamed_files or moved_files or renamed_dirs or moved_dirs:

                if appconfig.fh.enabled:
                    records = generate_filehistory_records(added_files, deleted_files,
                                    added_dirs, deleted_dirs, modified_files, renamed_files,
                                    moved_files, renamed_dirs, moved_dirs, commit, repo_id,
                                    parent, time)
                    save_file_histories(session, records)

                records = generate_activity_records(added_files, deleted_files,
                        added_dirs, deleted_dirs, modified_files, renamed_files,
                        moved_files, renamed_dirs, moved_dirs, commit, repo_id,
                        parent, users, time)

                save_user_activities(session, records)
            else:
                save_repo_rename_activity(session, commit, repo_id, parent, org_id, users, time)

            # TODO check: catalog entry update
            # KEEPER
            logging.info("REPO UPDATED EVENT repo_id: %s" % repo_id)
            logging.info("Trying to create/update keeper catalog entry for repo_id: %s..." % repo_id)
            if bool(generate_catalog_entry_by_repo_id(repo_id)):
                logging.info("Success!")
            else:
                logging.error("Something went wrong...")


            if appconfig.enable_collab_server:
                send_message_to_collab_server(repo_id)

def send_message_to_collab_server(repo_id):
    url = '%s/api/repo-update' % appconfig.collab_server
    form_data = 'repo_id=%s&key=%s' % (repo_id, appconfig.collab_key)
    req = request.Request(url, form_data.encode('utf-8'))
    resp = request.urlopen(req)
    ret_code = resp.getcode()
    if ret_code != 200:
        logging.warning('Failed to send message to collab_server %s', appconfig.collab_server)

def save_repo_rename_activity(session, commit, repo_id, parent, org_id, related_users, time):
    repo = seafile_api.get_repo(repo_id)

    record = {
        'op_type': 'rename',
        'obj_type': 'repo',
        'timestamp': time,
        'repo_id': repo_id,
        'repo_name': repo.repo_name,
        'path': '/',
        'op_user': commit.creator_name,
        'related_users': related_users,
        'commit_id': commit.commit_id,
        'old_repo_name': parent.repo_name
    }
    save_user_activity(session, record)

def save_user_activities(session, records):
    # If a file was edited many times by same user in 30 minutes, just update timestamp.
    if len(records) == 1 and records[0]['op_type'] == 'edit':
        record = records[0]
        _timestamp = record['timestamp'] - timedelta(minutes=30)
        q = session.query(Activity)
        q = q.filter(Activity.repo_id==record['repo_id'],
                     Activity.op_type==record['op_type'],
                     Activity.op_user==record['op_user'],
                     Activity.path==record['path'],
                     Activity.timestamp > _timestamp)
        row = q.first()
        if row:
            activity_id = row.id
            update_user_activity_timestamp(session, activity_id, record)
        else:
            save_user_activity(session, record)
    else:
        for record in records:
            if os.path.dirname(record['path']) == '/images/auto-upload':
                continue
            save_user_activity(session, record)

def generate_activity_records(added_files, deleted_files, added_dirs,
        deleted_dirs, modified_files, renamed_files, moved_files, renamed_dirs,
        moved_dirs, commit, repo_id, parent, related_users, time):

    OP_CREATE = 'create'
    OP_DELETE = 'delete'
    OP_EDIT = 'edit'
    OP_RENAME = 'rename'
    OP_MOVE = 'move'
    OP_RECOVER = 'recover'

    OBJ_FILE = 'file'
    OBJ_DIR = 'dir'

    repo = seafile_api.get_repo(repo_id)
    base_record = {
        'commit_id': commit.commit_id,
        'timestamp': time,
        'repo_id': repo_id,
        'related_users': related_users,
        'op_user': commit.creator_name,
        'repo_name': repo.repo_name
    }
    records = []

    for de in added_files:
        record = copy.copy(base_record)
        op_type = ''
        if commit.description.startswith('Reverted'):
            op_type = OP_RECOVER
        else:
            op_type = OP_CREATE
        record['op_type'] = op_type
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_FILE
        record['path'] = de.path
        record['size'] = de.size
        records.append(record)

    for de in deleted_files:
        record = copy.copy(base_record)
        record['op_type'] = OP_DELETE
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_FILE
        record['size'] = de.size
        record['path'] = de.path
        records.append(record)

    for de in added_dirs:
        record = copy.copy(base_record)
        op_type = ''
        if commit.description.startswith('Recovered'):
            op_type = OP_RECOVER
        else:
            op_type = OP_CREATE
        record['op_type'] = op_type
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_DIR
        record['path'] = de.path
        records.append(record)

    for de in deleted_dirs:
        record = copy.copy(base_record)
        record['op_type'] = OP_DELETE
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_DIR
        record['path'] = de.path
        records.append(record)

    for de in modified_files:
        record = copy.copy(base_record)
        op_type = ''
        if commit.description.startswith('Reverted'):
            op_type = OP_RECOVER
        else:
            op_type = OP_EDIT
        record['op_type'] = op_type
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_FILE
        record['path'] = de.path
        record['size'] = de.size
        records.append(record)

    for de in renamed_files:
        record = copy.copy(base_record)
        record['op_type'] = OP_RENAME
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_FILE
        record['path'] = de.new_path
        record['size'] = de.size
        record['old_path'] = de.path
        records.append(record)

    for de in moved_files:
        record = copy.copy(base_record)
        record['op_type'] = OP_MOVE
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_FILE
        record['path'] = de.new_path
        record['size'] = de.size
        record['old_path'] = de.path
        records.append(record)

    for de in renamed_dirs:
        record = copy.copy(base_record)
        record['op_type'] = OP_RENAME
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_DIR
        record['path'] = de.new_path
        record['size'] = de.size
        record['old_path'] = de.path
        records.append(record)

    for de in moved_dirs:
        record = copy.copy(base_record)
        record['op_type'] = OP_MOVE
        record['obj_id'] = de.obj_id
        record['obj_type'] = OBJ_DIR
        record['path'] = de.new_path
        record['size'] = de.size
        record['old_path'] = de.path
        records.append(record)

    for record in records:
        if 'old_path' in record:
            record['old_path'] = record['old_path'].rstrip('/')
        record['path'] = record['path'].rstrip('/') if record['path'] != '/' else '/'

    return records

def list_file_in_dir(repo_id, dirents, op_type):
    _dirents = copy.copy(dirents)
    files = []
    while True:
        try:
            d = _dirents.pop()
        except IndexError:
            break
        else:
            dir_obj = fs_mgr.load_seafdir(repo_id, 1, d.obj_id)
            new_path = None

            file_list = dir_obj.get_files_list()
            for _file in file_list:
                if op_type in ['rename', 'move']:
                    new_path = os.path.join(d.new_path, _file.name)
                new_file = DiffEntry(os.path.join(d.path, _file.name), _file.id, _file.size, new_path)
                files.append(new_file)

            subdir_list = dir_obj.get_subdirs_list()
            for _dir in subdir_list:
                if op_type in ['rename', 'move']:
                    new_path = os.path.join(d.new_path, _dir.name)
                new_dir = DiffEntry(os.path.join(d.path, _dir.name), _dir.id, new_path=new_path)
                _dirents.append(new_dir)

    return files

def generate_filehistory_records(added_files, deleted_files, added_dirs,
        deleted_dirs, modified_files, renamed_files, moved_files, renamed_dirs,
        moved_dirs, commit, repo_id, parent, time):

    OP_CREATE = 'create'
    OP_DELETE = 'delete'
    OP_EDIT = 'edit'
    OP_RENAME = 'rename'
    OP_MOVE = 'move'
    OP_RECOVER = 'recover'

    OBJ_FILE = 'file'
    OBJ_DIR = 'dir'

    repo = seafile_api.get_repo(repo_id)
    base_record = {
        'commit_id': commit.commit_id,
        'timestamp': time,
        'repo_id': repo_id,
        'op_user': commit.creator_name
    }
    records = []

    _added_files = copy.copy(added_files)
    _added_files.extend(list_file_in_dir(repo_id, added_dirs, 'add'))
    for de in _added_files:
        record = copy.copy(base_record)
        op_type = ''
        logging.info(commit.description)
        if commit.description.startswith('Reverted') or commit.description.startswith('Recovered'):
            op_type = OP_RECOVER
        else:
            op_type = OP_CREATE
        record['op_type'] = op_type
        record['obj_id'] = de.obj_id
        record['path'] = de.path.rstrip('/')
        record['size'] = de.size
        records.append(record)

    _deleted_files = copy.copy(deleted_files)
    _deleted_files.extend(list_file_in_dir(repo_id, deleted_dirs, 'delete'))
    for de in _deleted_files:
        record = copy.copy(base_record)
        record['op_type'] = OP_DELETE
        record['obj_id'] = de.obj_id
        record['size'] = de.size
        record['path'] = de.path.rstrip('/')
        records.append(record)

    for de in modified_files:
        record = copy.copy(base_record)
        op_type = ''
        if commit.description.startswith('Reverted'):
            op_type = OP_RECOVER
        else:
            op_type = OP_EDIT
        record['op_type'] = op_type
        record['obj_id'] = de.obj_id
        record['path'] = de.path.rstrip('/')
        record['size'] = de.size
        records.append(record)

    _renamed_files = copy.copy(renamed_files)
    _renamed_files.extend(list_file_in_dir(repo_id, renamed_dirs, 'rename'))
    for de in _renamed_files:
        record = copy.copy(base_record)
        record['op_type'] = OP_RENAME
        record['obj_id'] = de.obj_id
        record['path'] = de.new_path.rstrip('/')
        record['size'] = de.size
        record['old_path'] = de.path.rstrip('/')
        records.append(record)

    _moved_files = copy.copy(moved_files)
    _moved_files.extend(list_file_in_dir(repo_id, moved_dirs, 'move'))
    for de in _moved_files:
        record = copy.copy(base_record)
        record['op_type'] = OP_MOVE
        record['obj_id'] = de.obj_id
        record['path'] = de.new_path.rstrip('/')
        record['size'] = de.size
        record['old_path'] = de.path.rstrip('/')
        records.append(record)

    return records

def save_file_histories(session, records):
    if not isinstance(records, list):
        return
    for record in records:
        if should_record(record):
            save_filehistory(session, record)

def should_record(record):
    """ return True if record['path'] is a specified office file
    """
    if not appconfig.fh.enabled:
        return False

    filename, suffix = splitext(record['path'])
    if suffix[1:] in appconfig.fh.suffix_list:
        return True

    return False

def FileUpdateEventHandler(session, msg):
    elements = msg['content'].split('\t')
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

    time = datetime.datetime.utcfromtimestamp(msg['ctime'])

    # KEEPER
    logging.info("FILE UPDATE EVENT: %s, try generate_certificate", commit.desc)
    generate_certificate_by_commit(commit)

    save_file_update_event(session, time, commit.creator_name, org_id,
                           repo_id, commit_id, commit.desc)

def FileAuditEventHandler(session, msg):
    elements = msg['content'].split('\t')
    if len(elements) != 6:
        logging.warning("got bad message: %s", elements)
        return

    timestamp = datetime.datetime.utcfromtimestamp(msg['ctime'])
    msg_type = elements[0]
    user_name = elements[1]
    ip = elements[2]
    user_agent = elements[3]
    repo_id = elements[4]
    file_path = elements[5]

    org_id = get_org_id_by_repo_id(repo_id)

    save_file_audit_event(session, timestamp, msg_type, user_name, ip,
                          user_agent, org_id, repo_id, file_path)

def PermAuditEventHandler(session, msg):
    elements = msg['content'].split('\t')
    if len(elements) != 7:
        logging.warning("got bad message: %s", elements)
        return

    timestamp = datetime.datetime.utcfromtimestamp(msg['ctime'])
    etype = elements[1]
    from_user = elements[2]
    to = elements[3]
    repo_id = elements[4]
    file_path = elements[5]
    perm = elements[6]

    org_id = get_org_id_by_repo_id(repo_id)

    save_perm_audit_event(session, timestamp, etype, from_user, to,
                          org_id, repo_id, file_path, perm)


def DraftPublishEventHandler(session, msg):

    elements = msg['content'].split('\t')
    if len(elements) != 6:
        logging.warning("got bad message: %s", elements)
        return

    record = dict()
    record["timestamp"] = datetime.datetime.utcfromtimestamp(msg['ctime'])
    record["op_type"] = elements[0]
    record["obj_type"] = elements[1]
    record["repo_id"] = elements[2]
    repo = seafile_api.get_repo(elements[2])
    record["repo_name"] = repo.name if repo else ''
    record["op_user"] = elements[3]
    record["path"] = elements[4]
    record["old_path"] = elements[5]

    users = []
    org_id = get_org_id_by_repo_id(elements[2])
    if org_id > 0:
        users.extend(seafile_api.org_get_shared_users_by_repo(org_id, elements[2]))
        owner = seafile_api.get_org_repo_owner(elements[2])
    else:
        users.extend(seafile_api.get_shared_users_by_repo(elements[2]))
        owner = seafile_api.get_repo_owner(elements[2])

    if owner not in users:
        users = users + [owner]
    if not users:
        return

    record["related_users"] = users

    save_user_activity(session, record)


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
        handlers.add_handler('seahub.draft:publish', DraftPublishEventHandler)
