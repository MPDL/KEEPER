import re
import logging
from pysearpc import searpc_server
from ccnet.async import RpcServerProc

from .task_manager import task_manager
from .rpc import KeeperArchivingRpcClient, KEEPER_ARCHIVING_RPC_SERVICE_NAME
from .db_oper import DBOper
import config as _cfg

__all__ = [
    'KeeperArchiving',
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
            self._conf = conf
            self._db_oper = DBOper()

    def add_task(self, repo_id, owner):
        if not _valid_repo_id(repo_id):
            raise Exception('invalid repo id by add_task')
        if not owner:
            raise Exception('No owner defined for repo {}'.format(repo_id))
        return task_manager.add_task(repo_id, owner)

    def query_task_status(self, repo_id, owner, version):
        if not _valid_repo_id(repo_id):
            raise Exception('invalid repo id by query_task: {}'.format(repo_id))
        if not owner:
            raise Exception('No owner defined for repo {}'.format(repo_id))
        return task_manager.query_task_status(repo_id, version)

    def check_repo_archiving_status(self, repo_id, owner, action):
        if not _valid_repo_id(repo_id):
            raise Exception('invalid repo id {}'.format(repo_id))
        if not owner:
            raise Exception('No owner defined for repo {}'.format(repo_id))
        if not action:
            raise Exception('No action defined for  for repo: {} and owner: {}'.format(repo_id, owner))
        return task_manager.check_repo_archiving_status(repo_id, owner, action)

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

        searpc_server.register_function(KEEPER_ARCHIVING_RPC_SERVICE_NAME,
                                        self.check_repo_archiving_status)

    def start(self):
        task_manager.init(db_oper=self._db_oper,
                          num_workers=self._conf[_cfg.key_workers],
                          local_storage=self._conf[_cfg.key_local_storage],
                          archive_max_size=self._conf[_cfg.key_archive_max_size],
                          archives_per_library=self._conf[_cfg.key_archives_per_library],
                          hpss_enabled=self._conf[_cfg.key_hpss_enabled],
                          hpss_url=self._conf[_cfg.key_hpss_url],
                          hpss_user=self._conf[_cfg.key_hpss_user],
                          hpss_password=self._conf[_cfg.key_hpss_password],
                          hpss_storage_path=self._conf[_cfg.key_hpss_storage_path])
        task_manager.run()

        logging.info('keeper archiving started')

    def stop(self):
        task_manager.stop()

    def is_enabled(self):
        return self._enabled
