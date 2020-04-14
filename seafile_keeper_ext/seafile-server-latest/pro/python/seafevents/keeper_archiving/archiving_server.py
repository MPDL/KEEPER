import os
import sys
import re
import socket
import argparse
import logging
import json
from urllib import parse
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

from seafevents.keeper_archiving.task_manager import task_manager

logger = logging.getLogger(__name__)

sys.path.insert(0, os.environ.get('SEAHUB_DIR', ''))

try:
    from seahub.settings import SECRET_KEY
except ImportError:
    SECRET_KEY = None

REPO_ID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

def _valid_repo_id(repo_id):
    return REPO_ID_PATTERN.match(str(repo_id)) is not None


def add_task(repo_id, owner):
    if not _valid_repo_id(repo_id):
        raise Exception('invalid repo id by add_task: %s' % repo_id)
    return task_manager.add_task(repo_id, owner)

def query_task_status(repo_id, owner, version):
    if not _valid_repo_id(repo_id):
        raise Exception('invalid repo id by query_task: %s' % repo_id)
    return task_manager.query_task_status(repo_id, owner, version)

def check_repo_archiving_status(repo_id, owner, action):
    if not _valid_repo_id(repo_id):
        raise Exception('invalid repo id by check_repo_archiving_status: %s' % repo_id)
    return task_manager.check_repo_archiving_status(repo_id, owner, action)

def get_running_tasks():
    return task_manager.get_running_tasks()

def restart_task(archive_id):
    if not archive_id:
        raise Exception('archive_id is not defined')
    return task_manager.restart_task(archive_id)


class ArchivingRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        urlsplit = parse.urlsplit(self.path)
        path, arguments = urlsplit[2], urlsplit[3]
        arguments = parse.parse_qs(arguments)
        try:
            if path == '/add-task':
                resp = add_task(arguments['repo_id'][0], arguments['owner'][0])
            elif path == '/query-task-status':
                resp = query_task_status(arguments['repo_id'][0], arguments['owner'][0], arguments['version'][0])
            elif path == '/check-repo-archiving-status':
                resp = check_repo_archiving_status(arguments['repo_id'][0], arguments['owner'][0], arguments['action'][0])
            elif path == '/get-running-tasks':
                resp = get_running_tasks()
            elif path == '/restart-task':
                resp = restart_task(arguments['archive_id'][0])
            else:
                self.send_error(400, 'path %s invalid.' % path)
                return

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())

        except Exception as e:
            self.send_error(500, str(e))

def main():

    task_manager.init(
        num_workers=int(args.workers),
        local_storage=args.local_storage,
        archive_max_size=int(args.archive_max_size),
        archives_per_library=int(args.archives_per_library),
        hpss_enabled=args.hpss_enabled.lower() == 'true',
        hpss_url=args.hpss_url,
        hpss_user=args.hpss_user,
        hpss_password=args.hpss_password,
        hpss_storage_path=args.hpss_storage_path,
    )

    task_manager.run()

    # start http server
    server_address = (args.host, int(args.port))
    print("[%s] Starting keeper archiving on %s:%s..." % (datetime.now(), args.host, int(args.port)))

    # test if the http server has already started
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ret_code = sock.connect_ex((args.host, int(args.port)))
    if ret_code == 0:
        print("[%s] Existing keeper archiving  http server has been found, on %s:%s." %
              (datetime.now(), args.host, int(args.port)))
    else:
        archiving_server = HTTPServer(server_address, ArchivingRequestHandler)
        print("[%s] Keeper archiving http server has been started." % datetime.now())
        archiving_server.serve_forever()

    sock.close()


if __name__ == '__main__':
    # parse argument
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='archiving host')
    parser.add_argument('--port', help='archiving port')
    parser.add_argument('--local_storage', help='archiving local storage path')
    parser.add_argument('--workers', help='archiving workers amount')
    parser.add_argument('--archive_max_size', help='archive max size')
    parser.add_argument('--archives_per_library', help='max number of archives pro library')
    parser.add_argument('--hpss_enabled', help='hpss enabled trigger (True/False)')
    parser.add_argument('--hpss_url', help='office hpss url')
    parser.add_argument('--hpss_user', help='hpss user (if no ssh key available)')
    parser.add_argument('--hpss_password', help='hpss password (if no ssh key available)')
    parser.add_argument('--hpss_storage_path', help='office hpss staorage page')
    args = parser.parse_args()

    main()
