from sqlalchemy import Column, Integer, String, Text, Boolean, SmallInteger, DateTime
from sqlalchemy import func
from  sqlalchemy.schema import UniqueConstraint

from seafevents.db import Base

class KeeperArchive(Base):
    __tablename__ = 'keeper_archive'

    aid = Column(Integer, primary_key=True, autoincrement=True)
    repo_id = Column(String(length=37), nullable=False, index=True)
    owner = Column(String(length=255), nullable=False, index=True)
    version = Column(SmallInteger, index=True, nullable=False)
    checksum = Column(String(length=255), nullable=False)
    external_path = Column(Text, nullable=False)
    md = Column(Text, nullable=False)
    created = Column(DateTime, server_default=func.now(), index=True)
    UniqueConstraint(repo_id, version, name='unq_repo_id_version')
    __table_args__ = {'extend_existing': True}

    def __init__(self, repo_id, owner, version, checksum, external_path, md):
        self.repo_id = repo_id
        self.owner = owner
        self.version = version
        self.checksum = checksum
        self.external_path = external_path
        self.md = md

class KeeperArchiveOwnerQuota(Base):
    __tablename__ = 'keeper_archive_owner_quota'

    qid = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String(length=255), primary_key=True)
    quota = Column(SmallInteger, default=5)
    __table_args__ = {'extend_existing': True}

    def __init__(self, owner, quota):
        self.owner = owner
        self.quota = quota
