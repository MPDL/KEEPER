#coding: utf-8

import logging
import os
import tempfile
import subprocess
from seafobj import commit_mgr, fs_mgr, block_mgr
from db_oper import DBOper
from commit_differ import CommitDiffer
from thread_pool import ThreadPool
from seafevents.utils import get_python_executable

class ScanTask(object):
    def __init__(self, repo_id, head_commit_id, scan_commit_id):
        self.repo_id = repo_id
        self.head_commit_id = head_commit_id
        self.scan_commit_id = scan_commit_id

class VirusScan(object):
    def __init__(self, settings):
        self.settings = settings
        self.db_oper = DBOper(settings)

    def start(self):
        if not self.db_oper.is_enabled():
            return

        repo_list = self.db_oper.get_repo_list()
        if repo_list is None:
            self.db_oper.close_db()
            return

        thread_pool = ThreadPool(self.scan_virus, self.settings.threads)
        thread_pool.start()

        for row in repo_list:
            repo_id, head_commit_id, scan_commit_id = row

            if head_commit_id == scan_commit_id:
                logging.debug('No change occur for repo %.8s, skip virus scan.',
                              repo_id)
                continue

            thread_pool.put_task(ScanTask(repo_id, head_commit_id, scan_commit_id))

        thread_pool.join()

        self.db_oper.close_db()

    def scan_virus(self, scan_task):
        try:
            sroot_id = None
            hroot_id = None

            if scan_task.scan_commit_id:
                sroot_id = commit_mgr.get_commit_root_id(scan_task.repo_id, 1,
                                                         scan_task.scan_commit_id)
            if scan_task.head_commit_id:
                hroot_id = commit_mgr.get_commit_root_id(scan_task.repo_id, 1,
                                                         scan_task.head_commit_id)

            differ = CommitDiffer(scan_task.repo_id, 1, sroot_id, hroot_id)
            scan_files = differ.diff()

            if len(scan_files) == 0:
                logging.debug('No change occur for repo %.8s, skip virus scan.',
                              scan_task.repo_id)
                self.db_oper.update_vscan_record(scan_task.repo_id, scan_task.head_commit_id)
                return
            else:
                logging.info('Start to scan virus for repo %.8s.', scan_task.repo_id)

            vnum = 0
            nvnum = 0
            nfailed = 0
            vrecords = []

            for scan_file in scan_files:
                fpath, fid, fsize = scan_file
                if not self.should_scan_file(fpath, fsize):
                    continue

                ret = self.scan_file_virus(scan_task.repo_id, fid, fpath)

                if ret == 0:
                    logging.debug('File %s virus scan by %s: OK.',
                                  fpath, self.settings.scan_cmd)
                    nvnum += 1
                elif ret == 1:
                    logging.info('File %s virus scan by %s: Found virus.',
                                 fpath, self.settings.scan_cmd)
                    vnum += 1
                    vrecords.append((scan_task.repo_id, scan_task.head_commit_id, fpath))
                else:
                    logging.debug('File %s virus scan by %s: Failed.',
                                  fpath, self.settings.scan_cmd)
                    nfailed += 1

            if nfailed == 0:
                ret = 0
                if len(vrecords) > 0:
                    ret = self.db_oper.add_virus_record(vrecords)
                    if ret == 0 and self.settings.enable_send_mail:
                        self.send_email(vrecords)
                if ret == 0:
                    self.db_oper.update_vscan_record(scan_task.repo_id, scan_task.head_commit_id)

            logging.info('Virus scan for repo %.8s finished: %d virus, %d non virus, %d failed.',
                         scan_task.repo_id, vnum, nvnum, nfailed)

        except Exception as e:
            logging.warning('Failed to scan virus for repo %.8s: %s.',
                            scan_task.repo_id, e)

    def scan_file_virus(self, repo_id, file_id, file_path):
        try:
            tfd, tpath = tempfile.mkstemp()
            seafile = fs_mgr.load_seafile(repo_id, 1, file_id)
            for blk_id in seafile.blocks:
                os.write(tfd, block_mgr.load_block(repo_id, 1, blk_id))

            with open(os.devnull, 'w') as devnull:
                ret_code = subprocess.call([self.settings.scan_cmd, tpath],
                                           stdout=devnull, stderr=devnull)

            return self.parse_scan_result(ret_code)

        except Exception as e:
            logging.warning('Virus scan for file %s encounter error: %s.',
                            file_path, e)
            return -1
        finally:
            if tfd > 0:
                os.close(tfd)
                os.unlink(tpath)

    def send_email(self, vrecords):
        args = ["%s:%s" % (e[0], e[2]) for e in vrecords]
        cmd = [
            get_python_executable(),
            os.path.join(self.settings.seahub_dir, 'manage.py'),
            'notify_admins_on_virus',
        ] + args
        subprocess.Popen(cmd, cwd=self.settings.seahub_dir)

    def parse_scan_result(self, ret_code):
        rcode_str = str(ret_code)

        for code in self.settings.nonvir_codes:
            if rcode_str == code:
                return 0

        for code in self.settings.vir_codes:
            if rcode_str == code:
                return 1

        return ret_code

    def should_scan_file(self, fpath, fsize):
        if fsize >= self.settings.scan_size_limit << 20:
            logging.debug('File %s size exceed %sM, skip virus scan.' %
                          (fpath, self.settings.scan_size_limit))
            return False

        ext = os.path.splitext(fpath)[1].lower()
        if ext in self.settings.scan_skip_ext:
            logging.debug('File %s type in scan skip list, skip virus scan.' %
                          fpath)
            return False

        return True
