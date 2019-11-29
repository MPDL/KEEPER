import os
import sys
import re
import logging
import tempfile
import ConfigParser
from pysearpc import searpc_server
from ccnet.async import RpcServerProc

from .task_manager import task_manager
from .rpc import KeeperArchivingRpcClient, KEEPER_ARCHIVING_RPC_SERVICE_NAME
from .db_oper import DBOper
from seafevents.keeper_archiving.config import parse_workers, parse_archives_per_library, parse_max_size, parse_bool

__all__ = [
    'keeper_archiving',
    'KeeperArchivingRpcClient',
]

REPO_ID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
def _valid_repo_id(repo_id):
    if not isinstance(repo_id, basestring):
        return False
    return REPO_ID_PATTERN.match(str(repo_id)) is not None

class KeeperArchiving(object):

    def __init__(self, conf):
        self._enabled = conf['enabled']

        if self._enabled:
            self._archiving_storage = conf['archiving_storage']
            self._num_workers = conf['workers']
            self._archive_max_size = conf['archive-max-size']
            self._archives_per_library = conf['archives-per-library']
            self._db_oper = DBOper()

    def add_task(self, repo_id, owner):

        if not _valid_repo_id(repo_id):
            raise Exception('invalid repo id by add_task')

        return task_manager.add_task(repo_id, owner)

    def query_task_status(self, repo_id, version):

        if not _valid_repo_id(repo_id):
                raise Exception('invalid repo id by query_task: {}'.format(repo_id))

        return task_manager.query_task_status(repo_id, version)

    def register_rpc(self, ccnet_client):
        '''Register archiving rpc service'''
        searpc_server.create_service(KEEPER_ARCHIVING_RPC_SERVICE_NAME)
        ccnet_client.register_service(KEEPER_ARCHIVING_RPC_SERVICE_NAME,
                                      'basic',
                                      RpcServerProc)

        searpc_server.register_function(KEEPER_ARCHIVING_RPC_SERVICE_NAME,
                                        self.query_task_status)

        searpc_server.register_function(KEEPER_ARCHIVING_RPC_SERVICE_NAME,
                                        self.add_task)

    def start(self):
        task_manager.init(db_oper=self._db_oper,
                          num_workers=self._num_workers,
                          archiving_storage=self._archiving_storage,
                          archive_max_size=self._archive_max_size,
                          archives_per_library=self._archives_per_library)
        task_manager.run()

        logging.info('keeper archiving started')

    def stop(self):
        task_manager.stop()

    def is_enabled(self):
        return self._enabled
