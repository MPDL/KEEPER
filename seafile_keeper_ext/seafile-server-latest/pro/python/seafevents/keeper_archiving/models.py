from sqlalchemy import Column, Integer, String, CHAR, Text, UnicodeText, SmallInteger, DateTime
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import UniqueConstraint

# KeeperBase = automap_base()
KeeperBase = declarative_base()

MAX_UNICODE_TEXT_LEN = 2**24-1

class KeeperArchive(KeeperBase):
    __tablename__ = 'keeper_archive'

    aid = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(CHAR(length=37), nullable=False, index=True)
    commit_id = Column(CHAR(length=41), nullable=False)
    repo_name = Column(String(length=255), nullable=False)
    owner = Column(String(length=255), nullable=False, index=True)
    version = Column(SmallInteger, index=True, nullable=False)
    checksum = Column(String(length=100))
    external_path = Column(Text)
    status = Column(String(length=30), default='NOT_QUEUED')
    error = Column(Text)
    #like mediumtext, 16 MB
    md = Column(UnicodeText(length=MAX_UNICODE_TEXT_LEN))
    created = Column(DateTime, server_default=func.now(), index=True)
    UniqueConstraint(repo_id, owner, version, name='unq_keeper_archive_repo_id_version')
    __table_args__ = {'extend_existing': True}

    def __init__(self, repo_id, owner, version, checksum, external_path, md, repo_name, commit_id):
        self.repo_id = repo_id
        self.owner = owner
        self.version = version
        self.checksum = checksum
        self.external_path = external_path
        self.md = md
        self.repo_name = repo_name
        self.commit_id = commit_id

class KeeperArchiveOwnerQuota(KeeperBase):
    __tablename__ = 'keeper_archive_owner_quota'

    qid = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String(length=255), primary_key=True)
    repo_id = Column(CHAR(length=37), nullable=False, index=True)
    quota = Column(SmallInteger)
    UniqueConstraint(repo_id, owner, name='unq_keeper_archive_quota_owner_repo_id')
    __table_args__ = {'extend_existing': True}

    def __init__(self, owner, repo_id, quota):
        self.owner = owner
        self.repo_id = repo_id
        self.quota = quota
