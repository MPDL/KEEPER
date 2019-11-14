# coding: utf-8

import os
import Queue
import tempfile
import tarfile
import threading
import logging
import atexit

from .convert import Convertor, ConvertorFatalError

from seaserv import seafile_api

__all__ = ["task_manager"]

def _checkdir(dname):
    # If you do not have permission for keeper-archiving-storage files, then false is returned event if the file exists.
    if os.path.exists(dname):
        if not os.path.isdir(dname):
            raise RuntimeError("{} exists, but not a directory".format(dname))

        if not os.access(dname, os.R_OK | os.W_OK):
            raise RuntimeError("Access to {} denied".format(dname))
    else:
        msg = "Path to archiving storage {} does not exist".format(dname)
        logging.error(msg)
        raise RuntimeError(msg)


class KeeperArchivingTask(object):
    """ A task is in one of these status:

    - QUEUED:  waiting to be archived
    - PROCESSING: being fetched or archived
    - DONE: succefully archived
    - ERROR: error in fetching or archiving

    """
    def __init__(self, repo_id, owner, ver, archiving_storage):
        self.repo_id = repo_id
        self.owner = owner
        self.ver = ver
        self.archiving_storage = archiving_storage

        # path to tmp extracted library
        self._extracted_tmp_dir = None

        # path to the created archive tar in file system
        self._archive_path = None

        self._repo = seafile_api.get_repo(repo_id)

        self._status = 'QUEUED'
        self.error = None


    def __str__(self):
        return "<owner: {}, id: {}>".format(self.owner, self.repo_id)


    def get_status(self):
        return self._status

    def set_status(self, status):
        assert status in ('QUEUED', 'PROCESSING', 'DONE', 'ERROR')

        # Remove temporary file when done or error
        if status == 'ERROR' or status == 'DONE':
            path = self._extracted_tmp_dir
            if path and os.path.exists(path):
                logging.debug("removing extracted tmp library {}".format(path))
                try:
                    os.remove(path)
                except OSError, e:
                    logging.warning('failed to remove extracted tmp library {}: {}'.format(path, e))

        self._status = status

    status = property(get_status, set_status, None, "status of this task")

# TODO:
class Worker(threading.Thread):
    """Worker thread for task manager.
    """
    should_exit = False

    def __init__(self, tasks_queue, index, **kwargs):
        threading.Thread.__init__(self, **kwargs)

        self._tasks_queue = tasks_queue

        self._index = index

    # def _convert_to_pdf(self, task):
        # """Use libreoffice API to convert document to pdf"""
        # convertor = task_manager.convertor
        # if os.path.exists(task.pdf):
            # logging.debug('task %s already handle', task)
            # task.status = 'DONE'
            # return True

        # logging.debug('start to convert task %s', task)

        # success = False
        # _checkdir_with_mkdir(os.path.dirname(task.pdf))
        # try:
            # success = convertor.convert_to_pdf(task.document, task.pdf)
        # except ConvertorFatalError:
            # task.status = 'ERROR'
            # task.error = 'failed to convert document'
            # return False

        # if success:
            # logging.debug("succefully converted %s to pdf", task)
            # task.status = 'DONE'
        # else:
            # logging.warning("failed to convert %s to pdf", task)
            # task.status = 'ERROR'
            # task.error = 'failed to convert document'

        # return success

    # def _convert_excel_to_html(self, task):
        # '''Use libreoffice to convert excel to html'''
        # _checkdir_with_mkdir(task.htmldir)
        # if not task_manager.convertor.excel_to_html(
                # task.document, os.path.join(task.htmldir, 'index.html')):
            # logging.warning('failed to convert %s from excel to html', task)
            # task.status = 'ERROR'
            # task.error = 'failed to convert excel to html'
            # return False
        # else:
            # logging.debug('successfully convert excel %s to html', task)
            # task.status = 'DONE'
            # return True

    # def write_content_to_tmp(self, task):
        # '''write the document/pdf content to a temporary file'''
        # content = task.content
        # try:
            # suffix = "." + task.doctype
            # fd, tmpfile = tempfile.mkstemp(suffix=suffix)
            # os.close(fd)

            # with open(tmpfile, 'wb') as fp:
                # fp.write(content)
        # except Exception, e:
            # logging.warning('failed to write fetched document for task %s: %s', task, str(e))
            # task.status = 'ERROR'
            # task.error = 'failed to write fetched document to temporary file'
            # return False
        # else:
            # if task.doctype == 'pdf':
                # task.pdf = tmpfile
            # else:
                # task.document = tmpfile
            # return True

    def copy_repo_into_tmp_dir(self, repo):
        """TODO: Docstring for copy_repo_into_tmp_dir.

        :repo_id: TODO
        :returns: TODO
        """

        def get_root_dir(repo):
            """
            Get root commit dir
            """
            commits = seafile_api.get_commit_list(repo.id, 0, 1)
            commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
            return fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)


        seaf_dir = get_root_dir(repo)
        owner = seafile_api.get_repo_owner(repo.id)

        tmp_root_dir_path = os.path.join(self.archiving_storage, owner, repo.id)

        def write_seaf_to_path(seaf, to_path):
            """ Write SeafFile to path with stream
            """
            BUF_SIZE = 5 * 1024 * 1024 # 5MB chunks

            try:
                stream = seaf.get_stream()

                with open(to_path, "a") as target:
                    while True:
                        data = stream.read(BUF_SIZE)
                        if not data:
                            break
                        target.write(data)
                    target.close()
            except Exception, e:
                logging.warning('failed to write extracted file for task {}: {}'.format(task, e))
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
                # print(obj.get_files_list())
                # print(fs_mgr.obj_store.__dict__)
                dpath = path + os.sep + obj.name
                d = fs_mgr.load_seafdir(repo.id, repo.version, obj.id)
                for dname, dobj in d.dirents.items():
                    copy_dirent(dobj, repo, owner, dpath)
            elif obj.is_file():
                plist = [p for p in path.split(os.sep) if p]
                absdirpath = os.path.join(tmp_root_dir_path, *plist)
                if not os.path.exists(absdirpath):
                    os.makedirs(absdirpath)
                    seaf = fs_mgr.load_seafile(repo.id, repo.version, obj.id)
                    to_path = os.path.join(absdirpath, obj.name)
                    write_seaf_to_path(seaf, to_path)
                    logging.debug(u"File: {} copied to {}".format(obj.name, to_path))

                else:
                    logging.debug(u"Wrong object: {}".format(obj))


        for name, obj in seaf_dir.dirents.items():
            copy_dirent(seaf_dir, repo, owner, '')


        return tmp_root_dir_path


    def _extract_repo(self, task):
        """
        Extract repo from object storage to tmp directory
        """
        logging.debug('start to extract repo: %s', task)
        try:
            tmp_dir = copy_repo_into_tmp_dir(task._repo)
        except Exception as e:
            logging.warning('failed to extract repo {} of task {}: %s', task, e)
            task.status = 'ERROR'
            task.error = 'failed to fetch document'
            return False
        else:
            task._extracted_tmp_dir = tmp_dir
            return True

    def get_archive_path(task):
        """Construct path to archive
        """
        return os.path.join(task.archiving_storage, task.owner, "{}_ver{}.tar.gz".format(task.repo_id, task.ver))


    def _create_tar(self, task):
        """
        Create tar file for extracted repo
        """
        logging.debug('start to create tar for repo: {}', task.repo_id)
        try:
            #create tar.gz
            src_path = task._extracted_tmp_dir
            dest_path = get_archive_path(task)
            with tarfile.open(dest_path, mode='w:gz', format=tarfile.PAX_FORMAT) as archive:
                archive.add(src_path, '')

        except Exception as e:
            logging.warning('failed to archive dir {} to tar {} of task {}: {}'.format(src_path, dest_path, task, e))
            task.status = 'ERROR'
            task.error = 'failed to tar archive'
            return False
        else:
            task._archive_path = dest_path
            return True
        finally:
            archive.close()

    def _push_to_hpss(self, task):
        """
        Push created archive tar to HPSS
        """
        logging.debug('start to push archive to hpss: {}', task.repo_id)
        try:
            pass
        except Exception as e:
            logging.warning('failed to push archive tar {} of task {} to hpss: {}'.format(task._archive_path, task, e))
            task.status = 'ERROR'
            task.error = 'failed to push to hpss'
            return False
        else:
            return True


    def _handle_task(self, task):
        """
        extract repo from object storage to tmp dir ==> create tar.gz ==> put to archive storage
        """
        task.status = 'PROCESSING'

        success = self._extract_repo(task)
        if not success:
            return

        success = self._create_tar(task)
        if not success:
            return

        success = self._push_to_hpss(task)
        if not success:
            return

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

    - extract library from object storage to tmp dir
    - archive tmp library dir to tar.gz
    - push tar.gz to hpss
    """
    def __init__(self):
        # (file id, task) map
        self._tasks_map = {}
        self._tasks_map_lock = threading.Lock()

        # tasks queue
        self._tasks_queue = Queue.Queue()
        self._workers = []

        self.archiving_storage = None
        self.archive_max_size = 500 * 1024 * 1024 * 1024
        self._num_workers = 1
        self.archives_per_library = 5

        # TODO: Connection to HPSS???

    def init(self, num_workers=1,
             archiving_storage='/tmp/keeper-archiving-storage',
             archive_max_size=500 * 1024 * 1024 * 1024,
             archives_per_library=5):
        self._set_archiving_storage(archiving_storage)
        self._num_workers = num_workers
        self.archive_max_size = archive_max_size
        self.archives_per_library = archives_per_library

    def _set_archiving_storage(self, arch_dir):
        """Check the directory to store archive"""
        _checkdir(arch_dir)
        self.archiving_storage = arch_dir

    # ???
    def _task_file_exists(self, file_id, doctype=None):
        '''Test whether the file has already been converted'''
        file_html_dir = os.path.join(self.html_dir, file_id)
        pdf_dir = os.path.dirname(self.html_dir)
        # handler document->pdf
        if doctype not in EXCEL_TYPES:
            done_file = os.path.join(pdf_dir, 'pdf', file_id + '.pdf')
        else:
            done_file = os.path.join(file_html_dir, 'index.html')

        return os.path.exists(done_file)

    def add_task(self, repo_id, owner, ver):
        """Create an archiving task and dispatch it to worker threads"""
        with self._tasks_map_lock:
            if repo_id in self._tasks_map:
                task = self._tasks_map[repo_id]
                if task.status != 'ERROR' and task.status != 'DONE':
                    # If there is already a archiving  task in progress, don't create a
                    # new one.
                    return

            task = KeeperArchivingTask(repo_id, owner, ver, self.archiving_storage)
            self._tasks_map[repo_id] = task
            self._tasks_queue.put(task)


    # TODO:
    def query_task_status(self, file_id, doctype):
        ret = {}
        with self._tasks_map_lock:
            if file_id in self._tasks_map:
                task = self._tasks_map[file_id]
                if task.status == 'ERROR':
                    ret['status'] = 'ERROR'
                    ret['error'] = task.error
                else:
                    ret['status'] = task.status
            else:
                if self._task_file_exists(file_id):
                    ret['status'] = 'DONE'
                else:
                    ret['status'] = 'ERROR'
                    # handler document->pdf
                    ret['error'] = 'invalid file id'
        return ret

    def run(self):
        assert self._tasks_map is not None
        assert self._tasks_map_lock is not None
        assert self._tasks_queue is not None
        assert self.pdf_dir is not None
        assert self.html_dir is not None

        atexit.register(self.stop)

        self.convertor.start()

        for i in range(self._num_workers):
            t = Worker(self._tasks_queue, i)
            t.setDaemon(True)
            t.start()
            self._workers.append(t)

    def stop(self):
        logging.info('stop libreoffice...')
        self.convertor.stop()

task_manager = TaskManager()
