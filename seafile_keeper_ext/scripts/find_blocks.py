import sys
from seaserv import seafile_api, get_repo
from seafobj import commit_mgr, fs_mgr, block_mgr

MAX_INT = 2147483647

def usage():
    print "Usage: %s file_name [commit_id]" % __file__

def get_blocks(repo_id, fname, commit_id=None):
    """Print out blocks of file for repo and commit
        repo_id: repo id
        commit_id: commit id
    """
    repo = get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, MAX_INT)

    print "commits:", [(c.id, c.ctime) for c in commits]

    commit_id = commit_id if commit_id else commits[0].id
    commit = commit_mgr.load_commit(repo.id, repo.version, commit_id)

    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)

    file = dir.lookup(fname)
    print "File: %s, commit id: %s, root_id: %s" % (fname, commit_id, commit.root_id)

    if file:
        print "blocks: ", file.blocks
    else:
        print "No file for this commit!"


# get_blocks('b31859bf-69f3-4839-960e-2ddff7a2873f', '10MB.img', '98c0c4b2b9a5c47f62cd67e372e8aef66ee1c1f7')

if len(sys.argv) < 3:
    usage()
    sys.exit(1)
else:
    get_blocks(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
