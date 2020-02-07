import ccnet
from pysearpc import searpc_func

KEEPER_ARCHIVING_RPC_SERVICE_NAME = 'keeper-archiving-rpcserver'

class KeeperArchivingRpcClient(ccnet.RpcClientBase):
    def __init__(self, ccnet_client_pool, *args, **kwargs):
        ccnet.RpcClientBase.__init__(self, ccnet_client_pool, KEEPER_ARCHIVING_RPC_SERVICE_NAME,
                                     *args, **kwargs)

    @searpc_func("object", ["string", "string"])
    def add_task(self, repo_id, owner):
        pass

    @searpc_func("object", ["string", "string", "string"])
    def query_task_status(self, repo_id, owner, version):
        pass

    @searpc_func("object", ["strng", "string", "string"])
    def check_repo_archiving_status(self, repo_id, owner, action):
        pass

    @searpc_func("object", [])
    def get_running_tasks(self):
        pass

    @searpc_func("object", ["strng"])
    def restart_task(self, archive_id):
        pass

