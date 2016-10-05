from signals import repo_created, repo_deleted, file_modified
from handlers import repo_created_cb, repo_deleted_cb

repo_created.connect(repo_created_cb)
repo_deleted.connect(repo_deleted_cb)

# user defined callback func
try:
    from seahub_settings import repo_created_callback
    repo_created.connect(repo_created_callback)
except ImportError:
    pass

