# coding: utf-8

import Queue
import atexit
import hashlib
import logging as _l
import os
import sys
import argparse
import shutil
import tarfile
import threading
import json
from base64 import b64encode
import subprocess
import traceback
from datetime import datetime
from paramiko import SSHClient, SFTPClient, AutoAddPolicy

from seafobj import commit_mgr, fs_mgr
from seahub_settings import ARCHIVE_METADATA_TARGET
from seaserv import seafile_api
import config as _cfg
from seafevents.utils import get_python_executable

from keeper.common import parse_markdown_doi, truncate_str

MSG_DB_ERROR = 'Error by DB query.'
MSG_ADD_TASK = 'Cannot add task.'
MSG_WRONG_OWNER = 'Cannot archive. User is not the owner of the library.'
MSG_MAX_NUMBER_ARCHIVES_REACHED = 'Maximum number of archives for the library has been reached.'
MSG_CANNOT_GET_QUOTA = 'Cannot get archiving quota.'
MSG_CANNOT_CHECK_REPO_SIZE = 'Cannot check library size.'
MSG_CANNOT_CHECK_SNAPSHOT_STATUS = 'Cannot check archiving status of the snapshot.'
MSG_LIBRARY_TOO_BIG = 'The library is too big to be archived.'
MSG_EXTRACT_REPO = 'Cannot extract library.'
MSG_ADD_MD = 'Cannot archive library if archive-metadata.md file is not filled or missing.'
MSG_CREATE_TAR = 'Cannot create tar file for the archive.'
MSG_CALC_CHECKSUM = 'Cannot calculate checksum for the archive.'
MSG_PUSH_TO_HPSS = 'Cannot push archive to HPSS.'
MSG_ARCHIVED = 'Archive for %(name)s has been successfully created.'
MSG_CANNOT_FIND_ARCHIVE = 'Cannot find archive.'
MSG_SNAPSHOT_ALREADY_ARCHIVED = 'The snapshot of the library has already been archived.'
MSG_LAST_TASK_FAILED = 'Archiving has failed. Please try again in a few minutes.'
MSG_CANNOT_QUERY_TASK = 'Cannot query archiving task.'
MSG_UNKNOWN_STATUS = 'Unknown status of archiving task.'
MSG_CANNOT_ARCHIVE_TRY_LATER = 'Archiving has failed. Please try again in a few minutes.'
MSG_CANNOT_ARCHIVE_CRITICAL = 'Archiving task has failed due to a system error. The Keeper team has been informed and is looking for a solution.'
PROCESSING_STATUSES = ('BUILD_TASK', 'EXTRACT_REPO', 'ADD_MD', 'CREATE_TAR', 'PUSH_TO_HPSS')
MSG_ARCHIVING_STARTED = 'Archiving has started.'
MSG_PROCESSING_STATUS = {
    'BUILD_TASK': 'Task has been built.',
    'EXTRACT_REPO': 'Extracting library from object storage.',
    'ADD_MD': 'Adding metadata file to archive.',
    'CREATE_TAR': 'Creating archive tar file from extracted library.',
    'PUSH_TO_HPSS': 'Pushing archive to HPSS.',
}

ACTION_ERROR_MSG = {
    'is_snapshot_archived': ['Cannot check snapshot archiving status for library {} and owner {}: {}', MSG_CANNOT_CHECK_SNAPSHOT_STATUS],
    'get_quota': ['Cannot get archiving quota for library {} and owner {}: {}', MSG_CANNOT_GET_QUOTA],
    'max_repo_size': ['Cannot check max archiving size for library {} and owner {}: {}', MSG_CANNOT_CHECK_REPO_SIZE],
}


__all__ = ["task_manager"]

def _check_dir(dname):
    # If you do not have permission for keeper-archiving-storage files, then false is returned event if the file exists.
    if os.path.exists(dname):
        if not os.path.isdir(dname):
            raise RuntimeError("{} exists, but not a directory".format(dname))
        if not os.access(dname, os.R_OK | os.W_OK):
            raise RuntimeError("Access to {} denied".format(dname))
    else:
        msg = "Path to archiving storage {} does not exist".format(dname)
        _l.error(msg)
        raise RuntimeError(msg)


def _remove_dir_or_file(path):
    """Remove dir or file
    """
    _l.debug('Remove dir: {}'.format(path))
    if path is not None and os.path.exists(path):
        if os.path.isdir(path):
            try:
                shutil.rmtree(path, ignore_errors=True)
            except Exception as e:
                _l.error('Cannot remove directory {}: {}'.format(path, e))
        elif os.path.isfile(path):
            try:
                os.remove(path)
            except Exception as e:
                _l.error('Cannot remove file {}: {}'.format(path, e))
    else:
        _l.warning('Directory/file {} does not exist.'.format(path))


def _generate_file_md5(path, blocksize=5 * 2 ** 20):
    """Calculate md5 for the file"""
    m = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def _get_archive_path(storage_path, owner, repo_id, version):
    """Construct full path to archive in fs
    """
    # return os.path.join(storage_path, owner, '{}_ver{}.tar.gz'.format(repo_id, version))
    return os.path.join(storage_path, owner, '{}_ver{}.tar'.format(repo_id, version))

def get_commit(repo, commit_id=None):
    """
    Get commit
    """
    try:
        if commit_id is not None:
            commit = commit_mgr.load_commit(repo.id, repo.version, commit_id)
        else:
            commits = seafile_api.get_commit_list(repo.id, 0, 1)
            commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    except Exception as e:
        # TODO:
        _l.error('exception: {}'.format(e))

    return commit

def get_root_dir(repo, commit_root_id):
    """
    Get root commit dir
    """
    return fs_mgr.load_seafdir(repo.id, repo.version, commit_root_id)


def _get_msg_part(task):
    """
    Populate messages part of response for task
    """
    resp = {}
    if task.status == 'ERROR':
        resp.update({
            'msg': task.msg,
            'status': 'ERROR',
            'error': task.error
        })
    elif task.status in PROCESSING_STATUSES:
        resp.update({
            'msg': MSG_ARCHIVING_STARTED,
            'status': 'PROCESSING'
        })
    else:
        resp.update({
            'msg': MSG_UNKNOWN_STATUS,
            'status': 'ERROR',
            'error': "Unknown status {} of archiving task".format(task.status),
        })

    return resp


class KeeperArchivingTask(object):
    """ A task is in one of these status:

    - QUEUED:  waiting to be archived
    - PROCESSING: being fetched or archived
    - DONE: succefully archived
    - ERROR: error in fetching or archiving

    """

    def __init__(self, repo_id, owner, local_storage):
        self.repo_id = repo_id
        self.owner = owner

        self.version = 1
        self.local_storage = local_storage

        # unique archive id of the task
        self.archive_id = None

        # path to tmp extracted library
        self._extracted_tmp_dir = None

        # path to the created archive tar in file system
        self._archive_path = None

        # path to the archive metadata markdown file
        self._md_path = None

        # md content
        self.md = None
        self.md_dict = None

        self.checksum = None

        self.external_path = None

        self._repo = None

        self._commit = None

        self.status = 'BUILD_TASK'

        # verbose error for logs
        self.error = None

        # message for user
        self.msg = None

    def __str__(self):
        return "<owner: {}, repo_id: {}, ver: {}>".format(self.owner, self.repo_id, self.version)


def _update_archive_db(task):

    a = None
    try:
        # update db
        a = task_manager._db_oper.add_or_update_archive(task.repo_id, task.owner, task.version,
            task.checksum, task.external_path, task.md, task._repo.name, task._commit.commit_id,
            task.status, task.error)
    except Exception as e:
        msg = "Cannot update archiving task {}: {}".format(task, e)
        _l.critical(msg)
        #TODO: send msg to admin!!!
        return None

    return a


def _set_error(task, msg, error):
    task.msg = msg
    task.error = json.dumps({
        'status': task.status,
        'ts': str(datetime.now()),
        'error': error,
    })
    _l.error(json.dumps({'message': msg, 'error': task.error}))

def _set_critical_error(task, msg, error):
    _set_error(task, msg, error)
    # for critical situations set status to ERROR,
    # archiving stage is saved in error body as 'status': task.status
    task.status = 'ERROR'


class Worker(threading.Thread):
    """Worker thread for task manager.
    """
    should_exit = False

    def __init__(self, tasks_queue, index, local_storage, hpss_params, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self._tasks_queue = tasks_queue

        self.local_storage = local_storage

        self.hpss_enabled = hpss_params[_cfg.key_hpss_enabled]

        if self.hpss_enabled:
            self.hpss_url = hpss_params[_cfg.key_hpss_url]
            self.hpss_user = hpss_params[_cfg.key_hpss_user]
            self.hpss_password = hpss_params[_cfg.key_hpss_password]
            self.hpss_storage_path = hpss_params[_cfg.key_hpss_storage_path]

        self.my_task = None

    def copy_repo_into_tmp_dir(self, task):
        """TODO: Docstring for copy_repo_into_tmp_dir.

        """
        assert task._repo is not None
        assert task._commit is not None
        assert task.owner is not None

        seaf_dir = get_root_dir(task._repo, task._commit.root_id)
        owner = task.owner
        task._extracted_tmp_dir = os.path.join(self.local_storage, owner, task._repo.id)

        def write_seaf_to_path(seaf, to_path):
            """ Write SeafFile to path with stream
            """
            BUF_SIZE = 5 * 1024 * 1024  # 5MB chunks
            try:
                stream = seaf.get_stream()

                with open(to_path, "a") as target:
                    while True:
                        data = stream.read(BUF_SIZE)
                        if not data:
                            break
                        target.write(data)
                return True
            except Exception:
                _set_critical_error(task, MSG_EXTRACT_REPO,
                        u'Faled to write extracted file {}: {}'.format(to_path, traceback.format_exc()))
                return False

        def copy_dirent(obj, repo, owner, path):
            """
            Copies the files from Object Storage to local filesystem
            dir - SeafDir object
            fn - file name to be copied
            path - path in local file system where fn should be saved
            """
            if obj.is_dir():
                dpath = path + os.sep + obj.name
                d = fs_mgr.load_seafdir(repo.id, repo.version, obj.id)
                for dname, dobj in d.dirents.items():
                    copy_dirent(dobj, repo, owner, dpath)
            elif obj.is_file():
                plist = [p.decode('utf-8') for p in path.split(os.sep) if p]
                absdirpath = os.path.join(task._extracted_tmp_dir, *plist)
                if not os.path.exists(absdirpath):
                    os.makedirs(absdirpath)
                seaf = fs_mgr.load_seafile(repo.id, repo.version, obj.id)
                fname = obj.name.decode('utf-8')
                to_path = os.path.join(absdirpath, fname)
                write_seaf_to_path(seaf, to_path)
                _l.debug(u'File: {} copied to {}'.format(fname, to_path))
            else:
                _l.debug(u'Wrong seafile object: {}'.format(obj))

        # start traversing repo
        for name, obj in seaf_dir.dirents.items():
            copy_dirent(obj, task._repo, owner, '')

    def _clean_up(self, task):
        """Clean up worker state, db, tmp dirs, etc.
        """
        self.my_task = None
        # clean extracted library dir
        if task._extracted_tmp_dir is not None:
            _remove_dir_or_file(task._extracted_tmp_dir)
            task._extracted_tmp_dir = None
        # remove archive db entry
        # if not task.status in ('ERROR', 'DONE'):
            # task_manager._db_oper.delete_archive(task.repo_id, task.version)

    def _extract_repo(self, task):
        """
        Extract repo from object storage to tmp directory
        """

        task.status = 'EXTRACT_REPO'

        try:
            _l.info('Extracting repo for task: {}...'.format(task))
            self.copy_repo_into_tmp_dir(task)
            return True

        except Exception:
            _set_critical_error(task, MSG_EXTRACT_REPO,
                       u'Failed to extract repo {} of task {}: {}'.format(task.repo_id, task, traceback.format_exc()))
            return False

        finally:
            a = _update_archive_db(task)
            if a is not None and a.aid:
                task.archive_id = a.aid


    def _add_md(self, task):
        """
        Add metadata markdown file of archive
        """

        task.status = 'ADD_MD'

        try:
            _l.info('Adding md to repo: {}...'.format(task.repo_id))

            if task._extracted_tmp_dir is not None:
                arch_path = _get_archive_path(self.local_storage, task.owner, task.repo_id, task.version)
                md_path = os.path.join(task._extracted_tmp_dir, ARCHIVE_METADATA_TARGET)
                # check if md file exists
                if os.path.exists(md_path) and os.path.isfile(md_path):
                    new_md_path = arch_path + '.md'
                    try:
                        # copy to new place
                        shutil.copyfile(md_path, new_md_path)
                        task._md_path = new_md_path
                    except Exception as e:
                        _set_error(task, MSG_ADD_MD,
                                'Cannot copy md file {} to {} for task {}: {}'.format(md_path, new_md_path, task, e))
                        return False
                    try:
                        # prepare content for DB
                        with open(md_path, "r") as md:
                            task.md = md.read()
                            task.md_dict = parse_markdown_doi(task.md)
                            _l.debug("md_dict:{}".format(task.md_dict))
                    except Exception as e:
                        _set_error(task, MSG_ADD_MD,
                                'Cannot get content of md file {} for task {}: {}'.format(md_path, task, e))
                        return False
                else:
                    _set_error(task, MSG_ADD_MD, 'Cannot find md file {} for task {}'.format(md_path, task))
                    return False
            else:
                _set_error(task, MSG_ADD_MD,
                        'Extracted library tmp dir {} for task {} is not defined'.format(task._extracted_tmp_dir, task))
                return False

            return True

        except Exception as e:
            _set_error(task, MSG_ADD_MD,
                       'Cannot add md file for task {} to archive: {}'.format(task, e))
            return False

        finally:
            _update_archive_db(task)



    def _create_tar(self, task):
        """
        Create tar file for extracted repo
        """

        task.status = 'CREATE_TAR'

        archive = None

        try:

            _l.info('Creating a tar for repo: {}...'.format(task.repo_id))
            task._archive_path = _get_archive_path(self.local_storage, task.owner, task.repo_id, task.version)
            # with tarfile.open(task._archive_path, mode='w:gz', format=tarfile.PAX_FORMAT) as archive:
            with tarfile.open(task._archive_path, mode='w:', format=tarfile.PAX_FORMAT) as archive:
                archive.add(task._extracted_tmp_dir, '')

            _l.info('Calculate tar checksum for repo: {}...'.format(task.repo_id))
            try:
                task.checksum = _generate_file_md5(task._archive_path)
                _l.info('Checksum for repo {}: '.format(task.checksum))
            except Exception:
                _set_critical_error(task, MSG_CALC_CHECKSUM,
                    'Failed to calculate checksum for tar {} for task {}: {}'.format(task._archive_path, task, traceback.format_exc()))
                return False

            # raise Exception("BREAK TAR!")

            return True

        except Exception:
            _set_critical_error(task, MSG_CREATE_TAR,
                'Failed to archive dir {} to tar {} for task {}: {}'.format(task._extracted_tmp_dir,
                                                            task._archive_path, task, traceback.format_exc()))
            return False

        finally:
            _update_archive_db(task)
            archive and archive.close()


    def _push_to_hpss(self, task):
        """
        Push created archive tar to HPSS
        """

        task.status = 'PUSH_TO_HPSS'

        ssh = None
        sftp = None
        remote_md_path = None
        remote_archive_path = None

        if not self.hpss_enabled:
            _l.info('HPSS is not enabled, skip the action.')
            return True

        try:

            _l.info('Pushing archive to HPSS: {}...'.format(task._archive_path))

            # import time
            # time.sleep(60*5)


            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())

            ssh.connect(self.hpss_url, username=self.hpss_user, password=self.hpss_password)

            transport = ssh.get_transport()
            transport.set_keepalive(0)
            # best performance options
            # transport.get_security_options().ciphers = ('aes128-gcm@openssh.com', )
            transport.use_compression(False)

            sftp = SFTPClient.from_transport(transport)

            # create dirs on remote
            remote_dir = self.hpss_storage_path
            for dir in (task.owner, ):
                remote_dir = os.path.join(remote_dir, dir)
                try:
                    sftp.mkdir(remote_dir)
                    _l.info("Dir {} is created on HPSS".format(remote_dir))
                except IOError as e:
                    _l.info("Cannot create dir {} on HPSS: {}, dir already exists? Trying process further... ".format(remote_dir, e))

            # push archive tar

            ###### subprocess.Popen fast implementation
            remote_archive_path = os.path.join(remote_dir, os.path.basename(task._archive_path))

            task.external_path = remote_archive_path

            args = [ "scp", "-c", "aes128-gcm@openssh.com", "-o", "StrictHostKeyChecking=no",
                    task._archive_path, "{}@{}:{}".format(self.hpss_user, self.hpss_url, remote_archive_path) ]

            _l.info(" ".join(args))
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sts = os.waitpid(p.pid, 0)

            if sts[1] != 0:
                raise Exception('Error by {}, error code: {}'.format(" ".join(args), sts[1]))

            ###### end of subprocess.Popen implementation

            # remote_archive_path = os.path.join(remote_dir, os.path.basename(task._archive_path))
            # sftp.put(task._archive_path, remotepath=remote_archive_path)

            # push md file
            remote_md_path = os.path.join(remote_dir, os.path.basename(task._md_path))
            sftp.put(task._md_path, remotepath=remote_md_path)

            # calc checksum remotely
            _l.info('Calculate checksum for {} on remote...'.format(task._archive_path))
            stdin, stdout, stderr = ssh.exec_command('md5sum {}'.format(remote_archive_path))
            # block until command finished
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error_msg = ''.join(stderr.read())
                error_msg = error_msg.replace('\n', '')
                raise Exception('Cannot calculate checksum: {}, exit_status: {}'.format(error_msg, exit_status))

            resp = ''.join(stdout.read())
            remote_checksum = resp.split()[0]
            _l.info('Remote checksum: {}'.format(remote_checksum))

            # check checksums
            if task.checksum == remote_checksum:
                _l.info('Remote checksum equals to local checksum')
            else:
               raise Exception('Remote checksum {} does not match local checksum {}'.format(remote_checksum, task.checksum))

            _l.info('Successfully pushed archive to HPSS')

            return True

        except Exception:
            # All error in _push_to_hpss are CRITICAL!!!
            _set_critical_error(task, MSG_PUSH_TO_HPSS,
                    'Failed to push archive {} to HPSS for task {}: {}'.format(task._archive_path, task, traceback.format_exc()))
            # clean up hpss!!!
            try:
                if sftp:
                    remote_archive_path and sftp.remove(remote_archive_path)
                    remote_md_path and sftp.remove(remote_md_path)
            except Exception:
                _l.error('Cannot clean up HPSS: {}'.format(traceback.format_exc()))

            return False

        finally:
            _update_archive_db(task)
            sftp and sftp.close()
            ssh and ssh.close()



    def _handle_task(self, task):
        """
        extract repo from object storage to tmp dir ==> create tar.gz ==> put to archive storage
        """

        self.my_task = task

        try:
            success = self._extract_repo(task)
            if not success:
                return

            success = self._add_md(task)
            if not success:
                return

            success = self._create_tar(task)
            if not success:
                return

            success = self._push_to_hpss(task)
            if not success:
                return

            task.status = 'DONE'
            task.msg = MSG_ARCHIVED

        finally:
            with task_manager._tasks_map_lock:
                task_manager._tasks_map.pop(task.repo_id)

            _update_archive_db(task)
            task_manager._notify(task)
            self._clean_up(task)

        return

    def run(self):
        """Repeatedly get task from tasks queue and process it."""
        while True:
            try:
                task = self._tasks_queue.get(timeout=1)
            except Queue.Empty:
                continue

            self._handle_task(task)


class TaskManager(object):
    """Task manager schedules the processing of archiving tasks. A task comes
    from a http archive request. The handling of a task consists of these steps:

    - extract library from object storage to a tmp dir
    - pack the tmp dir to tar.gz
    - push tar.gz to hpss
    """

    def __init__(self):
        self._tasks_map = {}
        self._tasks_map_lock = threading.Lock()

        # tasks queue
        self._tasks_queue = Queue.Queue()
        self._workers = []

        self.local_storage = None
        self.archive_max_size = 500 * 1024 ** 3
        self._num_workers = 1
        self.archives_per_library = 5

        self._db_oper = None

    def init(self, db_oper, num_workers,
             local_storage, archive_max_size, archives_per_library,
             hpss_enabled, hpss_url, hpss_user, hpss_password, hpss_storage_path):
        self._db_oper = db_oper
        self._set_local_storage(local_storage)
        self._num_workers = num_workers
        self.archive_max_size = archive_max_size
        self.archives_per_library = archives_per_library
        (self.hpss_enabled, self.hpss_url, self.hpss_user, self.hpss_password, self.hpss_storage_path) = \
            (True, hpss_url, hpss_user, hpss_password, hpss_storage_path) if hpss_enabled else (
            False, None, None, None, None)


    def _set_local_storage(self, arch_dir):
        """Check the directory to store archive"""
        _check_dir(arch_dir)
        self.local_storage = arch_dir


    def _last_version_is_ok_(self, repo_id, version):
        """Archive has been successfully created and stored in HPSS and DB """
        a = self._db_oper.get_archives(repo_id=repo_id, version=version)
        _l.debug(a)
        return a is not None and a.status == 'DONE'


    def _try_rebuild_task_from_db(self, archive_id):
        """
        Try rebuild archiving task from db
        """

        a = self._db_oper.get_archive(archive_id)
        at = None

        if a is not None:
            at = KeeperArchivingTask(a.repo_id, a.owner, self.local_storage)
            at.status = a.status
            repo_id = a.repo_id
            if repo_id is not None:
                try:
                    at._repo = seafile_api.get_repo(repo_id)
                except Exception as e:
                    _set_error(at, MSG_ADD_TASK, 'Cannot get library {}: {}'.format(repo_id, e))
                    return at
            else:
                msg = 'repo_id is not defined'
                _set_error(at, msg, msg)
                return at

            owner = a.owner
            if owner is not None:
                ro = seafile_api.get_repo_owner(repo_id)
                if ro != a.owner:
                    _set_error(at, MSG_WRONG_OWNER, 'Wrong owner of library {}: {}'.format(repo_id, owner))
                    return at
            else:
                msg = 'owner is not defined'
                _set_error(at, msg, msg)
                return at

            commit_id = a.commit_id
            if commit_id is not None:
                commit = get_commit(at._repo, commit_id)
                if commit is None:
                    _set_error(at, 'Cannot find commit in library.', 'Cannot find commit {} in library {}.'.format(commit_id, repo_id))
                    return at
            else:
                msg = 'commit_id is not defined'
                _set_error(at, msg, msg)
                return at
            at._commit = commit

            # check version
            if a.version is None:
                msg = 'version is not defined'
                _set_error(at, msg, msg)
                return at
            at.version = a.version

        return at

    def send_archiving_email(self, task):
        """
        Send emails on archiving ERROR or DONE
        """
        try:
            seahub_dir = os.environ['SEAHUB_DIR']
            args = None
            if task.status == 'DONE':
                md = task.md_dict
                md = dict(
                    Title=truncate_str(md.get('Title')),
                    Author=truncate_str(md.get('Author')),
                    Year=truncate_str(md.get('Year')),
                )
                args = "|".join((task.status, task.owner, task.repo_id,
                                 task._repo.name, str(task.version), str(task.archive_id),
                                 b64encode(json.dumps(md))))
            elif task.status == 'ERROR':
                args = "|".join((task.status, task.owner, str(task.archive_id),
                                 task.repo_id, task._repo.name, task.error))
            else:
                _l.error("Unknown status: {}, direct email will not be sent.".format(task.status))
                return

            cmd = [
                get_python_executable(),
                os.path.join(seahub_dir, 'manage.py'),
                'notify_on_archiving',
                args,
            ]
            _l.debug("CMD: {}".format(cmd))
            p = subprocess.Popen(cmd, cwd=seahub_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(p.stdout.readline, ''):
                line = line.replace('\r', '').replace('\n', '')
                _l.debug(line)
                sys.stdout.flush()
        except Exception as e:
            _l.error("Cannot execute send_email: {}".format(e))



    def _build_task(self, repo_id, owner, storage_path):
        """
        Archiving task builder
        """
        at = KeeperArchivingTask(repo_id, owner, storage_path)
        at.status = 'BUILD_TASK'
        # check repo exists
        try:
            at._repo = seafile_api.get_repo(repo_id)
        except Exception as e:
            _set_error(at, MSG_ADD_TASK, 'Cannot get library {}: {}'.format(repo_id, e))
            return at

        # check owner
        ro = seafile_api.get_repo_owner(repo_id)
        if ro != owner:
            _set_error(at, MSG_WRONG_OWNER, 'Wrong owner of library {}: {}'.format(repo_id, owner))
            return at
        at.owner = owner

        # check repo snapshot is already archived
        commit = get_commit(at._repo)
        if self._db_oper.is_snapshot_archived(repo_id, commit.commit_id):
            _set_error(at, MSG_SNAPSHOT_ALREADY_ARCHIVED, 'Snapshot {} of library {} is already archived'.format(commit.commit_id, repo_id))
            return at
        at._commit = commit

        # check version
        max_ver = self._db_oper.get_max_archive_version(repo_id, owner)
        if max_ver is None:
            _set_error(at, MSG_ADD_TASK, 'Cannot get max version of archive for library {}: {}'.format(repo_id, owner))
            return at
        owner_quota = self._db_oper.get_quota(repo_id, owner) or self.archives_per_library
        _l.info("db_quota;{},archives_per_library:{}".format(self._db_oper.get_quota(repo_id, owner),self.archives_per_library))
        if max_ver >= owner_quota:
            _set_error(at, MSG_MAX_NUMBER_ARCHIVES_REACHED,
                       'Max number of archives {} for library {} and owner {} is reached'.format(max_ver, repo_id,
                                                                                                 owner))
            return at
        elif max_ver == -1:
            at.version = 1
        else:
            at.version = max_ver + 1

        # check max repo size
        try:
            repo_size = seafile_api.get_repo_size(repo_id)
        except Exception as e:
            _set_error(at, MSG_ADD_TASK, 'Cannot get library size {}: {}'.format(repo_id, e))
            return at

        # check max repo size
        # TODO: check units
        if repo_size > self.archive_max_size:
            _set_error(at, MSG_LIBRARY_TOO_BIG,
                       'Size of library {} is too big to be archived: {}.'.format(repo_id, repo_size))
            return at

        return at


    def _notify(self, task):
        """
        Notify user and keeper admin, send direct emails
        """
        d = {'status': task.status, 'repo_id': task.repo_id, 'version': task.version}
        task._repo and d.update(repo_name=task._repo.name)

        if task.status == 'ERROR':
            d.update(msg=MSG_CANNOT_ARCHIVE_CRITICAL)
            task.msg and d.update(error=task.msg)
            task.error and d.update(error=task.error)
            # send email
            self.send_archiving_email(task)
        elif task.status != 'DONE' and task.error is not None:
            d.update(msg=MSG_CANNOT_ARCHIVE_TRY_LATER)
            task.msg and d.update(error=task.msg)
        elif task.status == 'DONE':
            d.update(msg=MSG_ARCHIVED)
            # send email
            self.send_archiving_email(task)
        else:
            d.update(msg=MSG_UNKNOWN_STATUS, error='Unknown status: ' + task.status)

        self._db_oper.add_user_notification(task.owner, json.dumps(d))



    def add_task(self, repo_id, owner):
        """Create an archiving task and dispatch it to worker threads"""
        resp = {}
        with self._tasks_map_lock:
            # task is already in queue, return this one
            resp['repo_id'] = repo_id
            if repo_id in self._tasks_map:
                task = self._tasks_map[repo_id]
                resp['version'] = task.version
                resp.update(_get_msg_part(task))
                return resp

        resp = self.query_task_status(repo_id, owner)
        if resp['status'] == 'RESTART':
            # restart failed task
            return self.restart_task(resp['archive_id'])
        else:
            # build new task
            task = self._build_task(repo_id, owner, self.local_storage)
            if task.status == 'ERROR':
                # notify user!!!
                self._notify(task)
            else:
                with self._tasks_map_lock:
                    self._tasks_map[repo_id] = task
                    self._tasks_queue.put(task)

                _update_archive_db(task)

            resp['version'] = task.version

        resp.update(_get_msg_part(task))

        return resp

    def restart_task(self, archive_id):
        """
        Restart an archiving task and dispatch it to worker threads
        """
        resp = {'archive_id' : archive_id}
        task = self._try_rebuild_task_from_db(archive_id)
        if task is not None:
            resp.update(
                status=task.status,
                repo_id=task.repo_id,
                version=task.version,
            )
            if task.status == 'DONE':
                resp.update(msg='The task has been already done.')
            else:
                with self._tasks_map_lock:
                    self._tasks_map[task.repo_id] = task
                    self._tasks_queue.put(task)
        else:
            resp.update(
                status='ERROR',
                error='Cannot get archiving task: {} from db.'.format(archive_id)
            )

        return resp


    def query_task_status(self, repo_id, owner=None, version=None):
        """
        Query archiving task
        """
        resp = {'repo_id': repo_id}
        with self._tasks_map_lock:
            if repo_id in self._tasks_map:
                task = self._tasks_map[repo_id]
                resp['status'] = task.status
                resp['version'] = task.version
                resp.update(_get_msg_part(task))
                return resp

        try:
            a = self._db_oper.get_latest_archive(repo_id, version)
            if a is None:
                resp.update({
                    'msg': MSG_CANNOT_FIND_ARCHIVE,
                    'status': 'NOT_FOUND',
                })
            # CRIRTICAL ERROR
            elif a.status == 'ERROR':
                resp.update({
                    'msg': MSG_LAST_TASK_FAILED,
                    'status': 'ERROR',
                    'error': a.error_msg,
                })
            elif a.status == 'DONE':
                resp.update({
                    'msg': MSG_ARCHIVED,
                    'repo_name': a.repo_name,
                    'status': 'DONE',
                })
            elif a.status in PROCESSING_STATUSES:
                # CURRENTLY IN PROCESSING
                if a.error_msg is None:
                    resp.update({
                        'msg': MSG_PROCESSING_STATUS[a.status],
                        'status': 'PROCESSING',
                    })
                # NON CRIRTICAL ERROR, TRY RESTART
                else:
                    resp.update({
                        'archive_id': a.aid,
                        'msg': MSG_CANNOT_ARCHIVE_TRY_LATER,
                        'status': 'RESTART',
                    })
            else:
                resp.update({
                    'msg': MSG_UNKNOWN_STATUS,
                    'status': 'ERROR',
                    'error': "Unknown status {} of archiving task".format(a.status),
                })
        except Exception as e:
            error_msg = "Cannot query archiving task: {}".format(e)
            _l.error(error_msg)
            resp.update({
                'msg': MSG_CANNOT_QUERY_TASK,
                'status': 'ERROR',
                'error': error_msg,
            })
        return resp


    def check_repo_archiving_status(self, repo_id, owner, action):
        """TODO:
        """
        if repo_id is None:
            return {
                'status': 'ERROR',
                'error': 'No repo_id is defined.'
            }

        if owner is None:
            return {
                'status': 'ERROR',
                'error': 'No owner is defined.'
            }

        if action is None:
            return {
                'status': 'ERROR',
                'error': 'No action is defined.'
            }

        resp = {'repo_id': repo_id, 'owner': owner, 'action': action}
        try:
            repo = seafile_api.get_repo(repo_id)
            if owner != seafile_api.get_repo_owner(repo_id):
                resp.update({
                    'status': 'ERROR',
                    'error': MSG_WRONG_OWNER
                })
                return resp

            ####### is_snapshot_archived
            if action == 'is_snapshot_archived':
                # get root commit_id
                commit_id = get_commit(repo).commit_id
                is_archived = self._db_oper.is_snapshot_archived(repo_id, commit_id)
                if is_archived is None:
                    resp.update({
                        'status': 'ERROR',
                        'error': MSG_DB_ERROR
                    })
                    return resp
                resp.update({
                    'is_snapshot_archived': 'true' if is_archived else 'false',
                })
                return resp

            ####### get_quota
            if action == 'get_quota':
                # get current version
                curr_ver = self._db_oper.get_max_archive_version(repo_id, owner)
                if curr_ver is None:
                    resp.update({
                        'status': 'ERROR',
                        'error': MSG_DB_ERROR
                    })
                    return resp
                curr_ver = 0 if curr_ver == -1 else curr_ver
                # get quota from db or from config
                quota = self._db_oper.get_quota(repo_id, owner) or self.archives_per_library
                resp.update({
                    'curr_ver': curr_ver,
                    'remains': quota - curr_ver
                })
                return resp


            ####### max_repo_size
            if action == 'is_repo_too_big':
                repo_size = seafile_api.get_repo_size(repo_id)
                resp.update({
                    'is_repo_too_big': 'true' if repo_size > self.archive_max_size else 'false',
                })
                return resp

            ##### no action found!!!!
            return {
                'status': 'ERROR',
                'error': 'Unknown action: ' + action
            }

        except Exception as e:
            _l.error(ACTION_ERROR_MSG[action][0].format(repo_id, owner, e))
            resp.update({
                'status': 'ERROR',
                'error': ACTION_ERROR_MSG[action][1]
            })
            return resp


    def get_running_tasks(self):
        tasks = {}
        tasks['QUEUED'] = self._tasks_queue.qsize()
        tasks['PROCESSED'] = []
        for worker in self._workers:
            t = worker.my_task
            if t is not None:
                # tasks.append(int(t.repo_id))
                tasks['PROCESSED'].append({
                    'repo_id': t.repo_id,
                    'owner': t.owner,
                    'version': t.version,
                    'status': t.status,
                })
        return tasks


    def run(self):
        assert self._tasks_map is not None
        assert self._tasks_map_lock is not None
        assert self._tasks_queue is not None
        assert self.local_storage is not None

        atexit.register(self.stop)

        hpss_params = {
            _cfg.key_hpss_enabled: self.hpss_enabled,
            _cfg.key_hpss_url: self.hpss_url,
            _cfg.key_hpss_user: self.hpss_user,
            _cfg.key_hpss_password: self.hpss_password,
            _cfg.key_hpss_storage_path: self.hpss_storage_path,
        }

        # start HPSS session

        for i in range(self._num_workers):
            t = Worker(self._tasks_queue, i, self.local_storage, hpss_params)
            t.setDaemon(True)
            t.start()
            self._workers.append(t)

    def stop(self):

        # if background stopped, dump running tasks in DB
        _l.info("Shutdown has been forced, trying to save active archiving tasks into DB...")
        has_active_task = False
        for worker in self._workers:
            my_task = worker.my_task
            if my_task is not None:
                has_active_task = True
                _l.info("Found task {} in processing, saving...".format(my_task))
                my_task.error = 'FORCED_SHUTDOWN: Task interrupted by Keeper Background Service shutdown.'
                _update_archive_db(my_task)
                _l.info("Task has been saved.")

        if not has_active_task:
            _l.info("No active archiving tasks have been found.")



task_manager = TaskManager()

from seafevents.utils import get_config
from config import get_keeper_archiving_conf
import ccnet
import seaserv
from seafevents.keeper_archiving.rpc import KeeperArchivingRpcClient
from db_oper import DBOper

keeper_archiving_rpc = None

def _get_keeper_archiving_rpc():
    global keeper_archiving_rpc
    if keeper_archiving_rpc is None:
        pool = ccnet.ClientPool(
                seaserv.CCNET_CONF_PATH,
                central_config_dir=seaserv.SEAFILE_CENTRAL_CONF_DIR
            )
    keeper_archiving_rpc = KeeperArchivingRpcClient(pool)
    return keeper_archiving_rpc


if __name__ == "__main__":
    # kw = {
		# 'format': '[%(asctime)s] [%(levelname)s] %(message)s',
		# 'datefmt': '%m/%d/%Y %H:%M:%S',
		# 'level': _l.INFO,
		# 'stream': sys.stdout,
	# }
    # _l.basicConfig(**kw)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file',
                        default=os.path.join(os.path.abspath('..'), 'events.conf'),
                        help='seafevents config file')
    parser.add_argument('--is-processing',  action='store_true')
    parser.add_argument('-ls', '--list-tasks', action='store_true')
    parser.add_argument('-r', '--restart', help='restart archiving task(s)', nargs='+')

    args = parser.parse_args()

    cfg = get_config(args.config_file)
    cfg = get_keeper_archiving_conf(cfg)

    if not cfg[_cfg.key_enabled]:
        print ('Keeper Archiving is disabled.')
        exit(0)


    db = DBOper()
    rpc = _get_keeper_archiving_rpc()

    # IS PROCESSING
    if args.is_processing:
        tasks = rpc.get_running_tasks()
        tasks = tasks._dict
        if ('QUEUED' in tasks and tasks['QUEUED'] > 0) or ('PROCESSED' in tasks and len(tasks['PROCESSED']) > 0):
            print("true")
        else:
            print("false")

    # LIST OF PROCESSED AND NOT COMPLETED TASKS
    elif args.list_tasks:
        if rpc is not None:
            tasks = rpc.get_running_tasks()
            tasks = tasks._dict
            # queued tasks
            if 'QUEUED' in tasks:
                print("Number of queued tasks: {}".format(tasks['QUEUED']))
            else:
                print('No queued tasks.')
            # currently processed tasks
            if 'PROCESSED' in tasks and len(tasks['PROCESSED']) > 0:
                print("List of running Keeper Archiving tasks:")
                for t in tasks['PROCESSED']:
                    print("repo_id: {}, ver: {}, owner: {}, status: {}".format(
                        t['repo_id'], t['version'], t['owner'], t['status']
                    ))
            else:
                print("Number of currently proccesed tasks: 0")

        # not compeletd tasks in db
        tasks = db.get_not_completed_tasks()
        if tasks:
            print("Not completed tasks:")
            for t in tasks:
                print("id: {}, repo_id: {}, ver: {}, owner: {}, status: {}, error: {}, created: {}".format(
                    t.aid, t.repo_id, t.version, t.owner, t.status, t.error_msg, t.created,
                ))

    elif args.restart:
        print("Restart task(s)")
        if args.restart and len(args.restart) > 0:
            for aid in args.restart:
                task = rpc.restart_task(aid)
                if task:
                    print( task._dict )
        else:
            print("Usage: {}".format(parser.format_help()))

    else:
        print('Wrong argument.')


    exit(0)
