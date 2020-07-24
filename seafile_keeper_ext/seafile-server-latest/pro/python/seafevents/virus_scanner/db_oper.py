# coding: utf-8

from .models import VirusScanRecord, VirusFile
from .scan_settings import logger
from seafevents.db import SeafBase


class DBOper(object):
    def __init__(self, settings):
        self.edb_session = settings.session_cls
        self.seafdb_session = settings.seaf_session_cls

    def get_repo_list(self):
        session = self.seafdb_session()
        repo_list = []
        try:
            repo = SeafBase.classes.Repo
            branch = SeafBase.classes.Branch
            virtual_repo = SeafBase.classes.VirtualRepo

            # select r.repo_id, b.commit_id from Repo r, Branch b
            # where r.repo_id = b.repo_id and b.name = "master"
            # and r.repo_id not in (select repo_id from VirtualRepo)
            q = session.query(repo.repo_id, branch.commit_id).\
                filter(repo.repo_id == branch.repo_id).filter(branch.name == 'master').\
                filter(repo.repo_id.notin_(session.query(virtual_repo.repo_id)))

            rows = q.all()
            for row in rows:
                repo_id, commit_id = row
                scan_commit_id = self.get_scan_commit_id(repo_id)
                repo_list.append((repo_id, commit_id, scan_commit_id))
        except Exception as e:
            logger.error('Failed to fetch repo list from db: %s.', e)
            repo_list = None
        finally:
            session.close()

        return repo_list

    def get_scan_commit_id(self, repo_id):
        session = self.edb_session()
        try:
            q = session.query(VirusScanRecord).filter(VirusScanRecord.repo_id == repo_id)
            r = q.first()
            scan_commit_id = r.scan_commit_id if r else None
            return scan_commit_id
        except Exception as e:
            logger.error(e)
        finally:
            session.close()

    def update_vscan_record(self, repo_id, scan_commit_id):
        session = self.edb_session()
        try:
            q = session.query(VirusScanRecord).filter(VirusScanRecord.repo_id == repo_id)
            r = q.first()
            if not r:
                vrecord = VirusScanRecord(repo_id, scan_commit_id)
                session.add(vrecord)
            else:
                r.scan_commit_id = scan_commit_id

            session.commit()
        except Exception as e:
            logger.warning('Failed to update virus scan record from db: %s.', e)
        finally:
            session.close()

    def add_virus_record(self, records):
        session = self.edb_session()
        try:
            session.add_all(VirusFile(repo_id, commit_id, file_path, 0)
                            for repo_id, commit_id, file_path in records)
            session.commit()
            return 0
        except Exception as e:
            logger.warning('Failed to add virus records to db: %s.', e)
            return -1
        finally:
            session.close()


def get_virus_record(session, repo_id, start, limit):
    if start < 0:
        logger.error('start must be non-negative')
        raise RuntimeError('start must be non-negative')

    if limit <= 0:
        logger.error('limit must be positive')
        raise RuntimeError('limit must be positive')

    try:
        q = session.query(VirusFile)
        if repo_id:
            q = q.filter(VirusFile.repo_id == repo_id)
        q = q.slice(start, start+limit)
        return q.all()
    except Exception as e:
        logger.warning('Failed to get virus record from db: %s.', e)
        return None


def handle_virus_record(session, vid):
    try:
        q = session.query(VirusFile).filter(VirusFile.vid == vid)
        r = q.first()
        r.has_handle = 1
        session.commit()
        return 0
    except Exception as e:
        logger.warning('Failed to handle virus record: %s.', e)
        return -1


def get_virus_record_by_id(session, vid):
    try:
        q = session.query(VirusFile).filter(VirusFile.vid == vid)
        return q.first()
    except Exception as e:
        logger.warning('Failed to get virus record by id: %s.', e)
        return None
