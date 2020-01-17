# coding: utf-8

import Queue
import atexit
import hashlib
import logging as _l
import os
import shutil
import tarfile
import threading
import json
import paramiko
from paramiko import SSHClient

from seafobj import commit_mgr, fs_mgr
from seahub_settings import ARCHIVE_METADATA_TARGET
from seaserv import seafile_api
import config as _cfg

MSG_DB_ERROR = 'Error by DB query.'
MSG_ADD_TASK = 'Cannot add task.'
MSG_WRONG_OWNER = 'Wrong owner of the library.'
MSG_MAX_NUMBER_ARCHIVES_REACHED = 'Max number of archives for library is reached.'
MSG_CANNOT_GET_QUOTA = 'Cannot get archiving quota.'
MSG_CANNOT_CHECK_REPO_SIZE = 'Cannot check library size.'
MSG_CANNOT_CHECK_SNAPSHOT_STATUS = 'Cannot check snapshot archiving status.'
MSG_LIBRARY_TOO_BIG = 'The library is too big to be archived.'
MSG_EXTRACT_REPO = 'Cannot extract library.'
MSG_ADD_MD = 'Cannot attach metadata file to library archive.'
MSG_CREATE_TAR = 'Cannot create tar file for archive.'
MSG_PUSH_TO_HPSS = 'Cannot push archive to HPSS.'
MSG_ARCHIVING_SUCCESSFUL = 'Library is successfully archived.'
MSG_CANNOT_FIND_ARCHIVE = 'Cannot find archive.'
MSG_SNAPSHOT_ALREADY_ARCHIVED = 'The snapshot of the library is already archived.'

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
    """Calculate md5 for the file
    """
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


def get_commit(repo):
    """
    Get commit_root_id
    """
    try:
        commits = seafile_api.get_commit_list(repo.id, 0, 1)
    except Exception as e:
        # TODO:
        _l.error('exception: {}'.format(e))

    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return commit

def get_root_dir(repo, commit_root_id):
    """
    Get root commit dir
    """
    return fs_mgr.load_seafdir(repo.id, repo.version, commit_root_id)

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
        self._md = None

        self._checksum = None

        self._repo = None

        self._commit = None

        self._status = 'QUEUED'

        # verbose error for logs
        self.error = None

        # message for user
        self.msg = None

    def __str__(self):
        return "<owner: {}, id: {}>".format(self.owner, self.repo_id)

    def get_status(self):
        return self._status

    def set_status(self, status):
        assert status in ('NOT_QUEUED', 'QUEUED', 'PROCESSING', 'DONE', 'ERROR')

        # Remove temporary file when done or error
        # path = self._extracted_tmp_dir
        # if status == 'ERROR' or status == 'DONE':
        # _l.debug("removing extracted tmp library {}".format(path))
        # _remove_dir_or_file(path)

        self._status = status

    status = property(get_status, set_status, None, "status of this task")


def _set_error(task, msg, error):
    task.msg = msg
    task.error = error
    task.status = 'ERROR'
    _l.error(task.error)


class Worker(threading.Thread):
    """Worker thread for task manager.
    """
    should_exit = False

    def __init__(self, tasks_queue, index, local_storage, hpss_params, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self._tasks_queue = tasks_queue

        self._index = index

        self.local_storage = local_storage

        self.hpss_enabled = hpss_params[_cfg.key_hpss_enabled]

        if self.hpss_enabled:
            self.hpss_url = hpss_params[_cfg.key_hpss_url]
            self.hpss_user = hpss_params[_cfg.key_hpss_user]
            self.hpss_password = hpss_params[_cfg.key_hpss_password]
            self.hpss_storage_path = hpss_params[_cfg.key_hpss_storage_path]

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
                    target.close()
            except Exception as e:
                _l.error('failed to write extracted file {}: e'.format(to_path, e))
                task.status = 'ERROR'
                task.error = 'failed to write extracted file {}'.format(to_path)
                return False
            else:
                return True

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
        """Clean up tmps
        """
        # clean extracted library dir
        if task._extracted_tmp_dir is not None:
            _remove_dir_or_file(task._extracted_tmp_dir)
            task._extracted_tmp_dir = None
        # clean tar.gz and tar.gz.md only if task is DONE, i.e. pushed to HPSS
        # if self.hpss_enabled and task.status == 'DONE':
        # _remove_dir_or_file(task._archive_path)
        # task._archive_path = None
        # TODO: md can be stored in archived_storage to make archive search faster
        # _remove_dir_or_file(task._md_path)
        # task._md_path = None

    def _extract_repo(self, task):
        """
        Extract repo from object storage to tmp directory
        """
        _l.debug('Start extract repo for task: {}'.format(task))
        try:
            self.copy_repo_into_tmp_dir(task)
        except Exception as e:
            _set_error(task, MSG_EXTRACT_REPO,
                       u'Failed to extract repo {} of task {}: {}'.format(task.repo_id, task, e))
            # clean up
            self._clean_up(task)
            return False
        else:
            return True

    def _add_md(self, task):
        """
        Add metadata markdown file of archive
        """
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
                    _set_error(task, MSG_EXTRACT_REPO,
                               'Cannot copy md file {} to {} for task {}: {}'.format(md_path, new_md_path, task, e))
                    return False
                try:
                    # save content for DB
                    md = open(md_path, "r")
                    task._md = md.read()
                    md.close()
                except Exception as e:
                    _set_error(task, MSG_EXTRACT_REPO,
                               'Cannot get content of md file {} for task {}: {}'.format(md_path, task, e))
                    return False
            else:
                _set_error(task, MSG_EXTRACT_REPO, 'Cannot find md file {} for task {}'.format(md_path, task))
                return False
        else:
            _set_error(task,
                       'Extracted library tmp dir {} for task {} is not defined'.format(task._extracted_tmp_dir, task))
            return False

        return True

    def _create_tar(self, task):
        """
        Create tar file for extracted repo
        """
        _l.info('Start creating a tar for repo: {}'.format(task.repo_id))
        assert task._extracted_tmp_dir is not None
        try:
            task._archive_path = _get_archive_path(self.local_storage, task.owner, task.repo_id, task.version)
            # with tarfile.open(task._archive_path, mode='w:gz', format=tarfile.PAX_FORMAT) as archive:
            with tarfile.open(task._archive_path, mode='w:', format=tarfile.PAX_FORMAT) as archive:
                archive.add(task._extracted_tmp_dir, '')
        except Exception as e:
            _set_error(task, MSG_CREATE_TAR,
                       'Failed to archive dir {} to tar {} for task {}: {}'.format(task._extracted_tmp_dir,
                                                                                   task._archive_path, task, e))
            # clean up
            if archive:
                archive.close()
            self._clean_up(task)
            return False
        else:
            archive.close()
            _l.info('Calculate tar checksum for repo: {}...'.format(task.repo_id))
            task._checksum = _generate_file_md5(task._archive_path)
            _l.info('Checksum for repo {}: '.format(task._checksum))

        return True

    def _push_to_hpss(self, task):
        """
        Push created archive tar to HPSS
        """
        assert task._archive_path is not None


        if not self.hpss_enabled:
            _l.info('HPSS is not enabled, do not push archive to it')
            return True

        _l.info('Start pushing archive to HPSS: {}'.format(task._archive_path))
        try:
            # scp to HPSS

            ssh = SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ### ssh.load_system_host_keys() ### no keys, do not load

            ssh.connect(self.hpss_url, username=self.hpss_user, password=self.hpss_password)

            transport = ssh.get_transport()
            transport.set_keepalive(0)
            # best performance options
            transport.get_security_options().ciphers = ('aes128-gcm@openssh.com', )
            transport.use_compression(False)

            sftp = paramiko.SFTPClient.from_transport(transport)

            # create dirs on remote
            remote_dir = self.hpss_storage_path
            for dir in (task.owner, ):
                remote_dir = os.path.join(remote_dir, dir)
                try:
                    sftp.mkdir(remote_dir)
                    _l.info("Dir {} is created on HPSS".format(remote_dir))
                except IOError as e:
                    _l.error("Cannot create dir {} on HPSS: {}, dir already exists?".format(remote_dir, e))

            # push archive tar and md file
            remote_archive_path = os.path.join(remote_dir, os.path.basename(task._archive_path))
            sftp.put(task._archive_path, remotepath=remote_archive_path)

            # push md file
            sftp.put(task._md_path, remotepath=os.path.join(remote_dir, os.path.basename(task._md_path)))

            # calc checksum remotely
            _l.info('Calculate checksum for {} on remote...'.format(task._archive_path))
            stdin, stdout, stderr = ssh.exec_command('md5sum {}'.format(remote_archive_path))
            # block until command finished
            stdout.channel.recv_exit_status()
            resp = ''.join(stdout.read())
            remote_checksum = resp.split()[0]
            _l.info('Remote checksum: {}'.format(remote_checksum))

            # check checksums
            if task._checksum == remote_checksum:
                _l.info('Remote checksum equals to local checksum')
            else:
                _l.error('Remote checksum {} does not match local checksum {}'.format(remote_checksum, task._checksum))
                # TODO: Do not clean tmp files/dirs, try to resume or notify
                # keeper admin
                return False

            _l.info('Successfully pushed archive to HPSS')

        except Exception as e:
            _set_error(task, MSG_PUSH_TO_HPSS,
                       'Failed to push archive {} to HPSS for task {}: {}'.format(task._archive_path, task, e))
            # TODO: Do not clean tmp files/dirs, try to resume or notify
            # keeper admin
            return False
        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

        return True

    def _handle_task(self, task):
        """
        extract repo from object storage to tmp dir ==> create tar.gz ==> put to archive storage
        """
        task.status = 'PROCESSING'

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

        ## Put into DB, if success
        task_manager._db_oper.add_archive(task.repo_id, task.owner, task.version,
                                          task._checksum, task._archive_path, task._md, task._repo.name,
                                          task._commit.commit_id)

        task.status = 'DONE'
        task.msg = MSG_ARCHIVING_SUCCESSFUL

        task_manager._notify_user(task)

        self._clean_up(task)

        with task_manager._tasks_map_lock:
            task_manager._tasks_map.pop(task.repo_id)

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

        # TODO: Connection to HPSS

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

    def _archive_exists(self, repo_id, version):
        """Archive has been successfully created and stored in HPSS and DB """
        a = self._db_oper.get_archives(repo_id=repo_id, version=version)
        _l.debug(a)
        return a is not None and len(a) > 0

    def _build_task(self, repo_id, owner, storage_path):
        """
        TODO:
        """
        at = KeeperArchivingTask(repo_id, owner, storage_path)
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

    def _notify_user(self, task):
        """
        Notify user
        """
        d = {'status': task.status, 'repo_id': task.repo_id, 'version': task.version}
        task._repo and d.update(repo_name=task._repo.name)
        task.msg and d.update(msg=task.msg)
        task.error and d.update(error=task.error)
        self._db_oper.add_user_notification(task.owner, json.dumps(d))

    def add_task(self, repo_id, owner):
        """Create an archiving task and dispatch it to worker threads"""
        ret = {}
        with self._tasks_map_lock:
            # task is already in queue, return this one
            ret['repo_id'] = repo_id
            if repo_id in self._tasks_map:
                task = self._tasks_map[repo_id]
                ret['version'] = task.version
                ret['in_task_map'] = 'true'
                if task.error:
                    ret['msg'] = task.msg
                    ret['error'] = task.error
            else:
                # add new task
                task = self._build_task(repo_id, owner, self.local_storage)
                if task.status == 'ERROR':
                    # notify user!!!
                    self._notify_user(task)
                    ret['msg'] = task.msg
                    ret['error'] = task.error
                else:
                    self._tasks_map[repo_id] = task
                    self._tasks_queue.put(task)
                    ret['version'] = task.version
            ret['status'] = task.status
        return ret

    def query_task_status(self, repo_id, owner=None, version=None):
        """Query archiving task"""
        ret = {'repo_id': repo_id}
        with self._tasks_map_lock:
            if repo_id in self._tasks_map:
                task = self._tasks_map[repo_id]
                ret['status'] = task.status
                ret['version'] = task.version
                if task.status == 'ERROR':
                    ret.update({
                        'msg': task.msg,
                        'error': task.error
                    })
            else:
                if not version:
                    ret['status'] = 'NOT_QUEUED'
                elif self._archive_exists(repo_id, version):
                    ret['status'] = 'DONE'
                else:
                    ret.update({
                        'msg': MSG_CANNOT_FIND_ARCHIVE,
                        'status': 'ERROR',
                        'error': 'Cannot find archiving task or archive for repo_id: {}, version: {}'.format(repo_id, version)
                    })
        return ret


    ACTION_ERROR_MSG = {
        'is_snapshot_archived': ['Cannot check snapshot archiving status for library {} and owner {}: {}', MSG_CANNOT_CHECK_SNAPSHOT_STATUS],
        'get_quota': ['Cannot get archiving quota for library {} and owner {}: {}', MSG_CANNOT_GET_QUOTA],
        'max_repo_size': ['Cannot check max archiving size for library {} and owner {}: {}', MSG_CANNOT_CHECK_REPO_SIZE],
    }
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
        # stop HPSS session
        #_l.info('stop HPSS session...')
        pass


task_manager = TaskManager()
