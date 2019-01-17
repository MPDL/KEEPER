
from seahub.api2.utils import json_response
from seahub import settings

from keeper.catalog.catalog_manager import get_catalog

from django.http import JsonResponse
import sys
import hashlib
from seafobj import commit_mgr, fs_mgr
from seaserv import seafile_api, get_repo

import datetime

from keeper.models import BCertificate
from seahub.notifications.models import UserNotification
import json
from seahub.base.templatetags.seahub_tags import email2nickname

MSG_TYPE_KEEPER_BLOXBERG_MSG = 'bloxberg_msg'

def hash_file(repo_id, path):
    file = get_file_by_path(repo_id, path)
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    file_hash_inc = hashlib.sha256()
    stream = file.get_stream()

    while True:
        data = stream.read(BUF_SIZE)
        if not data:
            break
        file_hash_inc.update(data);

    data = {
        'sha256': file_hash_inc.hexdigest(),
        'authorName': get_repo_owner(repo_id),
        'timestampString': datetime.datetime.now(),
    }
    return data

def get_file_by_path(repo_id, path):
    repo = seafile_api.get_repo(repo_id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, get_commit_root_id(repo_id))
    paths = filter(None, path.split("/"))
    for path in paths:
        dir = dir.lookup(path)
    return dir

def get_commit_root_id(repo_id):
    repo = seafile_api.get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return commit.root_id

def get_repo_owner(repo_id):
    return seafile_api.get_repo_owner(repo_id)

def create_bloxberg_certificate(repo_id, path, transaction_id, created_time):
    commit_id = get_commit_root_id(repo_id)
    owner = get_repo_owner(repo_id)
    obj_id =  BCertificate.objects.add_bloxberg_certificate(transaction_id, repo_id, path, commit_id, created_time, owner)
    data = {
        'msg': obj_id,
    }
    send_notification(repo_id, transaction_id)
    return data

def certified_with_keeper(repo_id, path):
    commit_id = get_commit_root_id(repo_id)
    return BCertificate.objects.has_bloxberg_certificate(repo_id, path, commit_id)

def send_notification(repo_id, transaction_id):
    BLOXBERG_MSG=[]
    msg = 'Your data was successfully certified!'
    msg_transaction = 'Transaction ID: ' + transaction_id
    BLOXBERG_MSG.append(msg)
    BLOXBERG_MSG.append(msg_transaction)
    UserNotification.objects._add_user_notification(get_repo_owner(repo_id), MSG_TYPE_KEEPER_BLOXBERG_MSG,
      json.dumps({
      'message':('; '.join(BLOXBERG_MSG)),
      'transaction_id': transaction_id,
      'author_name': email2nickname(get_repo_owner(repo_id)),
    }))