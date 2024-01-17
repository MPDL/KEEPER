# coding: utf-8
import os
import json
import pytz
import copy
import logging
import logging.handlers
import datetime
from urllib import request
from datetime import timedelta
from os.path import splitext

from django.core.cache import cache
from sqlalchemy.sql import text
import pymysql

from seaserv import get_org_id_by_repo_id, seafile_api, get_commit
from seafobj import CommitDiffer, commit_mgr, fs_mgr
from seafobj.commit_differ import DiffEntry
from seafevents.events.db import save_file_audit_event, save_file_update_event, \
        save_perm_audit_event, save_user_activity, save_filehistory, update_user_activity_timestamp
from seafevents.app.config import TIME_ZONE
from seafevents.utils import get_opt_from_conf_or_env
from .change_file_path import ChangeFilePathHandler
from .models import Activity
# KEEPER
from keeper.cdc.cdc_manager import generate_certificate_by_commit
from keeper.catalog.catalog_manager import generate_catalog_entry_by_repo_id


def RepoUpdateEventHandler(config, session, msg):
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
                changer = ChangeFilePathHandler(session)
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

            time = datetime.datetime.utcfromtimestamp(msg['ctime'])
            if added_files or deleted_files or added_dirs or deleted_dirs or \
                    modified_files or renamed_files or moved_files or renamed_dirs or moved_dirs:

                fh_enabled = True
                if config.has_option('FILE HISTORY', 'enabled'):
                    fh_enabled = config.getboolean('FILE HISTORY', 'enabled')
                if fh_enabled:
                    records = generate_filehistory_records(added_files, deleted_files,
                                    added_dirs, deleted_dirs, modified_files, renamed_files,
                                    moved_files, renamed_dirs, moved_dirs, commit, repo_id,
                                    parent, time)
                    save_file_histories(config, session, records)

                records = generate_activity_records(added_files, deleted_files,
                        added_dirs, deleted_dirs, modified_files, renamed_files,
                        moved_files, renamed_dirs, moved_dirs, commit, repo_id,
                        parent, users, time)

                save_user_activities(session, records)
            # TODO check: catalog entry update
            # KEEPER
            logging.info("REPO UPDATED EVENT repo_id: %s" % repo_id)
            logging.info("Trying to create/update keeper catalog entry for repo_id: %s..." % repo_id)
            if bool(generate_catalog_entry_by_repo_id(repo_id)):
                logging.info("Success!")
            else:
                logging.error("Something went wrong...")


                # save repo monitor recodes
                records = generate_repo_monitor_records(repo_id, commit,
                                                        added_files, deleted_files,
                                                        added_dirs, deleted_dirs,
                                                        renamed_files, renamed_dirs,
                                                        moved_files, moved_dirs,
                                                        modified_files)
                save_message_to_user_notification(session, records)

            enable_collab_server = False
            if config.has_option('COLLAB_SERVER', 'enabled'):
                enable_collab_server = config.getboolean('COLLAB_SERVER', 'enabled')
            if enable_collab_server:
                send_message_to_collab_server(config, repo_id)


def send_message_to_collab_server(config, repo_id):
    collab_server = config.get('COLLAB_SERVER', 'server_url')
    collab_key = config.get('COLLAB_SERVER', 'key')
    url = '%s/api/repo-update' % collab_server
    form_data = 'repo_id=%s&key=%s' % (repo_id, collab_key)
    req = request.Request(url, form_data.encode('utf-8'))
    resp = request.urlopen(req)
    ret_code = resp.getcode()
    if ret_code != 200:
        logging.warning('Failed to send message to collab_server %s', collab_server)


def generate_repo_monitor_records(repo_id, commit,
                                  added_files, deleted_files,
                                  added_dirs, deleted_dirs,
                                  renamed_files, renamed_dirs,
                                  moved_files, moved_dirs,
                                  modified_files):

    OP_CREATE = 'create'
    OP_RECOVER = 'recover'
    OP_DELETE = 'delete'
    OP_RENAME = 'rename'
    OP_MOVE = 'move'
    OP_EDIT = 'edit'

    OBJ_FILE = 'file'
    OBJ_DIR = 'dir'

    # {'_dict': {'client_version': '8.0.8',
    #            'commit_id': '436a73b6253de071f29947ad15122e38bfd991eb',
    #            'creator': '3d486d5be28704428d613e86be533ad66286a839',
    #            'creator_name': 'lian@lian.com',
    #            'ctime': 1666689533,
    #            'description': 'Added or modified "1" and 2 more files.\n'
    #                           'Deleted "users.xlsx".\n',
    #            'device_name': 'lian mac work',
    #            'no_local_history': 1,
    #            'parent_id': 'e7dc5161cb00b2b5784fd58e303d5944fbd5d647',
    #            'repo_category': None,
    #            'repo_desc': '',
    #            'repo_id': '31191817-eda3-49f6-b2d9-d7bc534f6c5a',
    #            'repo_name': 'lian lib for test repo monitor',
    #            'root_id': '01e9bea5f8b525bed256afc46d24821d7ce9b8be',
    #            'second_parent_id': None,
    #            'version': 1}}

    repo = seafile_api.get_repo(repo_id)
    base_record = {
        'op_user': getattr(commit, 'creator_name', ''),
        'repo_id': repo_id,
        'repo_name': repo.repo_name,
        'commit_id': commit.commit_id,
        'timestamp': commit.ctime,
        'commit_desc': commit.description,
    }

    records = []

    if added_files:

        added_files_record = copy.copy(base_record)
        added_files_record["commit_diff"] = []

        # {'new_path': None,
        #  'obj_id': '0000000000000000000000000000000000000000',
        #  'path': '/3',
        #  'size': 0}
        for de in added_files:

            if commit.description.startswith('Reverted'):
                op_type = OP_RECOVER
            else:
                op_type = OP_CREATE

            commit_diff = dict()
            commit_diff['op_type'] = op_type
            commit_diff['obj_type'] = OBJ_FILE
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.path
            commit_diff['size'] = de.size

            added_files_record["commit_diff"].append(commit_diff)

        records.append(added_files_record)

    if deleted_files:

        deleted_files_record = copy.copy(base_record)
        deleted_files_record["commit_diff"] = []

        for de in deleted_files:

            commit_diff = dict()
            commit_diff['op_type'] = OP_DELETE
            commit_diff['obj_type'] = OBJ_FILE
            commit_diff['obj_id'] = de.obj_id
            commit_diff['size'] = de.size
            commit_diff['path'] = de.path

            deleted_files_record["commit_diff"].append(commit_diff)

        records.append(deleted_files_record)

    if added_dirs:

        added_dirs_record = copy.copy(base_record)
        added_dirs_record["commit_diff"] = []

        for de in added_dirs:

            if commit.description.startswith('Recovered'):
                op_type = OP_RECOVER
            else:
                op_type = OP_CREATE

            commit_diff = dict()
            commit_diff['op_type'] = op_type
            commit_diff['obj_type'] = OBJ_DIR
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.path

            added_dirs_record["commit_diff"].append(commit_diff)

        records.append(added_dirs_record)

    if deleted_dirs:

        deleted_dirs_record = copy.copy(base_record)
        deleted_dirs_record["commit_diff"] = []

        for de in deleted_dirs:

            commit_diff = dict()
            commit_diff['op_type'] = OP_DELETE
            commit_diff['obj_type'] = OBJ_DIR
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.path

            deleted_dirs_record["commit_diff"].append(commit_diff)

        records.append(deleted_dirs_record)

    if renamed_files:

        renamed_files_record = copy.copy(base_record)
        renamed_files_record["commit_diff"] = []

        for de in renamed_files:

            commit_diff = dict()
            commit_diff['op_type'] = OP_RENAME
            commit_diff['obj_type'] = OBJ_FILE
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.new_path
            commit_diff['size'] = de.size
            commit_diff['old_path'] = de.path

            renamed_files_record["commit_diff"].append(commit_diff)

        records.append(renamed_files_record)

    if renamed_dirs:

        renamed_dirs_record = copy.copy(base_record)
        renamed_dirs_record["commit_diff"] = []

        for de in renamed_dirs:

            commit_diff = dict()
            commit_diff['op_type'] = OP_RENAME
            commit_diff['obj_type'] = OBJ_DIR
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.new_path
            commit_diff['size'] = de.size
            commit_diff['old_path'] = de.path

            renamed_dirs_record["commit_diff"].append(commit_diff)

        records.append(renamed_dirs_record)

    if moved_files:

        moved_files_record = copy.copy(base_record)
        moved_files_record["commit_diff"] = []

        for de in moved_files:

            commit_diff = dict()
            commit_diff['op_type'] = OP_MOVE
            commit_diff['obj_type'] = OBJ_FILE
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.new_path
            commit_diff['size'] = de.size
            commit_diff['old_path'] = de.path

            moved_files_record["commit_diff"].append(commit_diff)

        records.append(moved_files_record)

    if moved_dirs:

        moved_dirs_record = copy.copy(base_record)
        moved_dirs_record["commit_diff"] = []

        for de in moved_dirs:

            commit_diff = dict()
            commit_diff['op_type'] = OP_MOVE
            commit_diff['obj_type'] = OBJ_DIR
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.new_path
            commit_diff['size'] = de.size
            commit_diff['old_path'] = de.path

            moved_dirs_record["commit_diff"].append(commit_diff)

        records.append(moved_dirs_record)

    if modified_files:

        modified_files_record = copy.copy(base_record)
        modified_files_record["commit_diff"] = []

        for de in modified_files:

            if commit.description.startswith('Reverted'):
                op_type = OP_RECOVER
            else:
                op_type = OP_EDIT

            commit_diff = dict()
            commit_diff['op_type'] = op_type
            commit_diff['obj_type'] = OBJ_FILE
            commit_diff['obj_id'] = de.obj_id
            commit_diff['path'] = de.path
            commit_diff['size'] = de.size

            modified_files_record["commit_diff"].append(commit_diff)

        records.append(modified_files_record)

    return records


def save_message_to_user_notification(session, records):

    repo_id_monitor_users = {}

    for record in records:

        repo_id = record.get('repo_id')
        if not repo_id:
            continue

        monitor_users = cache.get('{}_monitor_users'.format(repo_id))
        if not monitor_users:
            sql = "SELECT email FROM base_usermonitoredrepos where repo_id='{}'".format(repo_id)
            result = session.execute(text(sql))
            monitor_users = result.fetchall()
            monitor_users = [item[0] for item in monitor_users]

        cache_monitor_users = []
        for monitor_user in monitor_users:

            permission = seafile_api.check_permission_by_path(repo_id, '/', monitor_user)
            if permission not in ('r', 'rw'):
                del_sql = "DELETE FROM base_usermonitoredrepos where email='{}' and repo_id='{}'".format(monitor_user, repo_id)
                session.execute(text(del_sql))
                session.commit()
                continue

            cache_monitor_users.append(monitor_user)

        cache.set('{}_monitor_users'.format(repo_id),
                  cache_monitor_users,
                  24 * 60 * 60)

        repo_id_monitor_users[repo_id] = cache_monitor_users

    # process repo update record
    records_should_save = []
    for record in records:

        repo_id = record.get('repo_id')
        if not repo_id or repo_id not in repo_id_monitor_users:
            continue

        op_user = record.get('op_user')
        if not op_user:
            continue

        for monitor_user in repo_id_monitor_users[repo_id]:

            if op_user == monitor_user:
                continue

            info = {
                'record': record,
                'monitor_user': monitor_user
            }

            records_should_save.append(info)

        # {'monitor_user': 'lian@lian.com',
        #  'record': {'commit_desc': 'Deleted "users.xlsx" and 1 more files',
        #             'commit_diff': [{'obj_id': '4e1385391118ad01302a68f5ee1885f76382aa2f',
        #                              'obj_type': 'file',
        #                              'op_type': 'delete',
        #                              'path': '/users.xlsx',
        #                              'size': 8939},
        #                             {'obj_id': '82135d1f2687e56e2a9a7be530baf61f4abb0b5f',
        #                              'obj_type': 'file',
        #                              'op_type': 'delete',
        #                              'path': '/123456.md',
        #                              'size': 13}],
        #             'commit_id': 'b013adb9cf06631e835d42d10f7ccf49a69caad8',
        #             'op_user': 'foo@foo.com',
        #             'repo_id': '31191817-eda3-49f6-b2d9-d7bc534f6c5a',
        #             'repo_name': 'lian lib for test repo monitor',
        #             'timestamp': 1666774731}}

    # save to user notification
    step = 100
    for i in range(0, len(records_should_save), step):

        values = list()
        for item in records_should_save[i: i+step]:
            monitor_user = item['monitor_user']
            record = item['record']

            detail = {
                "commit_id": record["commit_id"],
                "repo_id": record["repo_id"],
                "repo_name": record["repo_name"],
                "op_user": record["op_user"],
                "op_type": record["commit_diff"][0]["op_type"],
                "obj_type": record["commit_diff"][0]["obj_type"],
                "obj_path_list": [item["path"] for item in record["commit_diff"]],
                "old_obj_path_list": [],
            }

            if record["commit_diff"][0].get("old_path"):
                detail["old_obj_path_list"] = [item["old_path"] for item in record["commit_diff"]]

            detail = json.dumps(detail)
            detail = pymysql.converters.escape_string(detail)

            time_zone = pytz.timezone(TIME_ZONE)

            utc_datetime = datetime.datetime.utcfromtimestamp(record['timestamp'])
            utc_datetime = utc_datetime.replace(microsecond=0)
            utc_datetime = pytz.utc.localize(utc_datetime)
            local_datetime = utc_datetime.astimezone(time_zone)
            local_datetime_str = local_datetime.strftime("%Y-%m-%d %H:%M:%S")

            values.append((monitor_user, 'repo_monitor', detail, local_datetime_str, 0))

        sql = """INSERT INTO notifications_usernotification (to_user, msg_type, detail, timestamp, seen)
                 VALUES %s""" % ', '.join(["('%s', '%s', '%s', '%s', %s)" % value for value in values])
        session.execute(text(sql))
        session.commit()


def save_user_activities(session, records):
    # If a file was edited many times by same user in 30 minutes, just update timestamp.
    if len(records) == 1 and records[0]['op_type'] == 'edit':
        record = records[0]
        _timestamp = record['timestamp'] - timedelta(minutes=30)
        q = session.query(Activity).filter(Activity.timestamp > _timestamp)
        q = q.filter(Activity.repo_id==record['repo_id'],
                     Activity.op_type==record['op_type'],
                     Activity.op_user==record['op_user'],
                     Activity.path==record['path'])
        row = q.first()
        if row:
            activity_id = row.id
            update_user_activity_timestamp(session, activity_id, record)
        else:
            save_user_activity(session, record)
    else:
        for record in records:
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
        'op_user': getattr(commit, 'creator_name', ''),
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
        if os.path.dirname(record['path']).startswith('/images/auto-upload'):
            records.remove(record)
        if os.path.dirname(record['path']).startswith('/images/sdoc'):
            records.remove(record)
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
        'op_user': getattr(commit, 'creator_name', '')
    }
    records = []

    _added_files = copy.copy(added_files)
    _added_files.extend(list_file_in_dir(repo_id, added_dirs, 'add'))
    for de in _added_files:
        record = copy.copy(base_record)
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


def save_file_histories(config, session, records):
    if not isinstance(records, list):
        return
    for record in records:
        if should_record(config, record):
            fh_threshold = int(get_opt_from_conf_or_env(config, 'FILE HISTORY', 'threshold', default=5))
            save_filehistory(session, fh_threshold, record)


def should_record(config, record):
    """ return True if record['path'] is a specified office file
    """
    suffix = 'md,txt,doc,docx,xls,xlsx,ppt,pptx'
    fh_suffix_list = get_opt_from_conf_or_env(config, 'FILE HISTORY', 'suffix', default=suffix.strip(','))
    filename, suffix = splitext(record['path'])
    if suffix[1:] in fh_suffix_list:
        return True

    return False


def FileUpdateEventHandler(config, session, msg):
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
    creator_name = getattr(commit, 'creator_name', '')
    if creator_name is None:
        creator_name = ''

    # KEEPER
    logging.info("FILE UPDATE EVENT: %s, try generate_certificate", commit.desc)
    generate_certificate_by_commit(commit)

    save_file_update_event(session, time, creator_name, org_id,
                           repo_id, commit_id, commit.desc)

def FileAuditEventHandler(config, session, msg):
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
    if not file_path.startswith('/'):
        file_path = '/' + file_path

    org_id = get_org_id_by_repo_id(repo_id)

    save_file_audit_event(session, timestamp, msg_type, user_name, ip,
                          user_agent, org_id, repo_id, file_path)

def PermAuditEventHandler(config, session, msg):
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


def DraftPublishEventHandler(config, session, msg):

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
