#coding: utf-8

import os
import tempfile
import subprocess
import multiprocessing as mp
from seafobj import commit_mgr, fs_mgr, block_mgr
from db_oper import DBOper
from commit_differ import CommitDiffer
from seafevents.utils import get_python_executable
from scan_settings import logger

def scan_file_virus(repo_id, head_commit_id, file_id, file_path, scan_cmd, nscan, ntotal, pflag):
    try:
        tfd, tpath = tempfile.mkstemp(dir = '/run/tmp')
        seafile = fs_mgr.load_seafile(repo_id, 1, file_id)
        for blk_id in seafile.blocks:
            os.write(tfd, block_mgr.load_block(repo_id, 1, blk_id))
        with open(os.devnull, 'w') as devnull:
            ret_code = subprocess.call([scan_cmd, tpath],
                                       stdout=devnull, stderr=devnull)
        if ret_code == 0:
            logger.debug('File %s virus scan by %s: OK.',
                                          file_path, scan_cmd)
        elif ret_code == 1:
            logger.info('File %s virus scan by %s: Found virus.',
                                          file_path, scan_cmd)
        else:
            logger.debug('File %s virus scan by %s: Failed.',
                                          file_path, scan_cmd)
        if pflag == 1:
            logger.info('Scan progress: %d/%d total items', nscan, ntotal)

        scan_file_task = ScanFileTask(repo_id, head_commit_id, file_id, file_path)

        scan_file_task.result = ret_code
        return scan_file_task

    except Exception as e:
        logger.warning('Virus scan for file %s encounter error: %s.',
                        file_path, e)
        return -1
    finally:
        if tfd > 0:
            os.close(tfd)
            os.unlink(tpath)


class ScanTask(object):
    def __init__(self, repo_id, head_commit_id, scan_commit_id):
        self.repo_id = repo_id
        self.head_commit_id = head_commit_id
        self.scan_commit_id = scan_commit_id

class ScanFileTask(object):
    def __init__(self, repo_id, head_commit_id, fid, fpath):
        self.repo_id = repo_id
        self.head_commit_id = head_commit_id
        self.fid = fid
        self.fpath = fpath
        self.result = -1

class VirusScan(object):
    def __init__(self, settings):
        self.settings = settings
        self.db_oper = DBOper(settings)
        self.res = []

    def start(self):
        if not self.db_oper.is_enabled():
            return

        repo_list = self.db_oper.get_repo_list()
        if repo_list is None:
            self.db_oper.close_db()
            return

        for row in repo_list:
            repo_id, head_commit_id, scan_commit_id = row

            if self.settings.rescan:
                virus_list = self.db_oper.get_virus_records()
                for VirusFile in virus_list:
                    if repo_id == VirusFile.repo_id:
                        scan_commit_id = 0

            if head_commit_id == scan_commit_id:
                logger.debug('No change occur for repo %.8s, skip virus scan.',
                              repo_id)
                continue

            self.scan_virus(ScanTask(repo_id, head_commit_id, scan_commit_id))

        self.db_oper.close_db()

    def scan_virus(self, scan_task):
        try:
            sroot_id = None
            hroot_id = None

            if scan_task.scan_commit_id:
                sroot_id = commit_mgr.get_commit_root_id(scan_task.repo_id, 1,
                                                         scan_task.scan_commit_id)
            else:
                sroot_id = '0000000000000000000000000000000000000000'

            if scan_task.head_commit_id:
                hroot_id = commit_mgr.get_commit_root_id(scan_task.repo_id, 1,
                                                         scan_task.head_commit_id)
            differ = CommitDiffer(scan_task.repo_id, 1, sroot_id, hroot_id)
            scan_files = differ.diff()

            if len(scan_files) == 0:
                logger.debug('No change occur for repo %.8s, skip virus scan.',
                              scan_task.repo_id)
                self.db_oper.update_vscan_record(scan_task.repo_id, scan_task.head_commit_id)
                return
            else:
                logger.info('Start to scan virus for repo %.8s [%d total items].', scan_task.repo_id, len(scan_files))

            vnum = 0
            nvnum = 0
            nfailed = 0
            nscan = 0
            pflag = 0
            vrecords = []
            pool = mp.Pool(self.settings.threads)

            for scan_file in scan_files:
                fpath, fid, fsize = scan_file
                nscan += 1
                if nscan%1000 == 0:
                    pflag = 1
                if not self.should_scan_file(fpath, fsize):
                    continue
                handler = pool.apply_async(scan_file_virus, args = (scan_task.repo_id, scan_task.head_commit_id, fid, fpath, self.settings.scan_cmd, nscan, len(scan_files), pflag), callback = self.do_result)
                pflag = 0

            pool.close();
            pool.join()

            for proc in self.res:
                if proc.repo_id == scan_task.repo_id:
                    ret = self.parse_scan_result(proc.result);

                    if ret == 0:
                        nvnum += 1
                    elif ret == 1:
                        vnum += 1
                        vrecords.append((proc.repo_id, proc.head_commit_id, proc.fpath.decode('utf-8')))
                    else:
                        nfailed += 1

            if nfailed == 0:
                ret = 0
                if len(vrecords) > 0:
                    ret = self.db_oper.add_virus_record(vrecords)
                    if ret == 0 and self.settings.enable_send_mail:
                        self.send_email(vrecords)
                if ret == 0:
                    self.db_oper.update_vscan_record(scan_task.repo_id, scan_task.head_commit_id)

            logger.info('Virus scan for repo %.8s finished: %d virus, %d non virus, %d failed.',
                         scan_task.repo_id, vnum, nvnum, nfailed)

        except Exception as e:
            logger.warning('Failed to scan virus for repo %.8s: %s.',
                            scan_task.repo_id, e)

    def do_result(self, result):
        self.res.append(result)

    def parse_scan_result(self, ret_code):
        rcode_str = str(ret_code)
        for code in self.settings.nonvir_codes:
            if rcode_str == code:
               return 0
        for code in self.settings.vir_codes:
            if rcode_str == code:
               return 1

        return ret_code


    def send_email(self, vrecords):
        args = ["%s:%s" % (e[0], e[2]) for e in vrecords]
        cmd = [
            get_python_executable(),
            os.path.join(self.settings.seahub_dir, 'manage.py'),
            'notify_admins_on_virus',
        ] + args
        subprocess.Popen(cmd, cwd=self.settings.seahub_dir)

    def should_scan_file(self, fpath, fsize):
        if fsize >= self.settings.scan_size_limit << 20:
            logger.debug('File %s size exceed %sM, skip virus scan.' %
                          (fpath, self.settings.scan_size_limit))
            return False

        ext = os.path.splitext(fpath)[1].lower()
        if ext in self.settings.scan_skip_ext:
            logger.debug('File %s type in scan skip list, skip virus scan.' %
                          fpath)
            return False

        return True
