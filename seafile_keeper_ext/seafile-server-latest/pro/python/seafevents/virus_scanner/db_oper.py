#coding: utf-8

import logging
from sqlalchemy.orm.scoping import scoped_session
from models import VirusScanRecord, VirusFile

class DBOper(object):
    def __init__(self, settings):
        self.edb_session = None
        self.sdb_conn = None
        self.sdb_cursor = None
        self.is_enable = False
        self.init_db(settings)

    def init_db(self, settings):
        try:
            import MySQLdb
        except ImportError:
            logging.info('Failed to import MySQLdb module, stop virus scan.')
            return

        try:
            self.edb_session = scoped_session(settings.session_cls)

            self.sdb_conn = MySQLdb.connect(host=settings.sdb_host, port=settings.sdb_port,
                                            user=settings.sdb_user, passwd=settings.sdb_passwd,
                                            db=settings.sdb_name, charset=settings.sdb_charset)
            self.sdb_conn.autocommit(True)
            self.sdb_cursor = self.sdb_conn.cursor()

            self.is_enable = True
        except Exception as e:
            logging.info('Failed to init mysql db: %s, stop virus scan.' %  e)
            if self.edb_session:
                self.edb_session.close()
            if self.sdb_cursor:
                self.sdb_cursor.close()
            if self.sdb_conn:
                self.sdb_conn.close()

    def is_enabled(self):
        return self.is_enable

    def close_db(self):
        if self.is_enable:
            self.edb_session.close()
            self.sdb_cursor.close()
            self.sdb_conn.close()

    def get_repo_list(self):
        repo_list = []
        try:
            self.sdb_cursor.execute('select r.repo_id, b.commit_id from Repo r, Branch b '
                                    'where r.repo_id = b.repo_id and b.name = "master" and '
                                    'r.repo_id not in (select repo_id from VirtualRepo)')
            rows = self.sdb_cursor.fetchall()
            for row in rows:
                repo_id, commit_id = row
                scan_commit_id = self.get_scan_commit_id(repo_id)
                repo_list.append((repo_id, commit_id, scan_commit_id))
        except Exception as e:
            logging.warning('Failed to fetch repo list from db: %s.', e)
            repo_list = None

        return repo_list

    def get_scan_commit_id(self, repo_id):
        q = self.edb_session.query(VirusScanRecord).filter(VirusScanRecord.repo_id==repo_id)
        r = q.first()
        scan_commit_id = r.scan_commit_id if r else None
        self.edb_session.remove()
        return scan_commit_id

    def update_vscan_record(self, repo_id, scan_commit_id):
        try:
            q = self.edb_session.query(VirusScanRecord).filter(VirusScanRecord.repo_id==repo_id)
            r = q.first()
            if not r:
                vrecord = VirusScanRecord(repo_id, scan_commit_id)
                self.edb_session.add(vrecord)
            else:
                r.scan_commit_id = scan_commit_id

            self.edb_session.commit()
            self.edb_session.remove()
        except Exception as e:
            logging.warning('Failed to update virus scan record from db: %s.', e)

    def add_virus_record(self, records):
        try:
            self.edb_session.add_all(VirusFile(repo_id, commit_id, file_path, 0) \
                                     for repo_id, commit_id, file_path in records)
            self.edb_session.commit()
            self.edb_session.remove()
            return 0
        except Exception as e:
            logging.warning('Failed to add virus records to db: %s.', e)
            return -1

    def get_virus_records(self):
        try:
            q = self.edb_session.query(VirusFile)
            return q.all()
        except Exception as e:
            logging.warning('Failed to get virus records: %s.', e)
            return None


def get_virus_record(session, repo_id, start, limit):
    if start < 0:
        raise RuntimeError('start must be non-negative')

    if limit <= 0:
        raise RuntimeError('limit must be positive')

    try:
        q = session.query(VirusFile)
        if repo_id:
            q = q.filter(VirusFile.repo_id==repo_id)
        q = q.slice(start, start+limit)
        return q.all()
    except Exception as e:
        logging.warning('Failed to get virus record from db: %s.', e)
        return None

def handle_virus_record(session, vid):
    try:
        q = session.query(VirusFile).filter(VirusFile.vid==vid)
        r = q.first()
        r.has_handle = 1
        session.commit()
        return 0
    except Exception as e:
        logging.warning('Failed to handle virus record: %s.', e)
        return -1

def get_virus_record_by_id(session, vid):
    try:
        q = session.query(VirusFile).filter(VirusFile.vid==vid)
        return q.first()
    except Exception as e:
        logging.warning('Failed to get virus record by id: %s.', e)
        return None
