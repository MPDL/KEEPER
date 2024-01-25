import sys
from datetime import datetime
from seaserv import seafile_api, get_repo
from seafobj import commit_mgr, fs_mgr, block_mgr


def usage():
    print(f"Usage: {__file__} repo_id num_last_commits")

def get_history(args):
    """Print out blocks of file for repo and commit
        repo_id: repo id
    """
    print(args)
    repo_id = args[1]
    num_last_commits = int(args[2]) if len(args)==3 else 10
    repo = get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, num_last_commits)

    print(f"History of Commits for repo_id: {repo_id})")
    for c in commits:
        # print(c.__dict__)
        print("ts:", datetime.fromtimestamp(c.ctime).strftime("%Y-%m-%d %H:%M:%S")) 
        print("creator:", c.creator_name) 
        print("action:", c.desc)


print(sys.argv)
if len(sys.argv) < 2:
    usage()
    sys.exit(1)
else:
    get_history(sys.argv)
