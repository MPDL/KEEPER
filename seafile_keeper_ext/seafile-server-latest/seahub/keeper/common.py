# -*- coding: utf-8 -*-

import logging
import mistune
import json
import MySQLdb

from seahub.settings import DATABASES

from thirdpart.seafobj import fs_mgr, commit_mgr
from seaserv import seafile_api, get_repo

def get_logger(name, logfile):
    logger = logging.getLogger(name)
    handler = logging.handlers.WatchedFileHandler(logfile)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

def print_json(obj):
    print((json.dumps(obj, ensure_ascii = False, indent=4, sort_keys=True, separators=(',', ': '))))

def get_db(db_name):
    """Get DB connection"""
    return MySQLdb.connect(host=DATABASES['default']['HOST'],
         user=DATABASES['default']['USER'],
         passwd=DATABASES['default']['PASSWORD'],
         db=db_name,
         charset='utf8')

HEADER_STEP = 2
# Headers in MD file to be processed by the parse_markdown
MD_HEADERS =  ('Title', 'Author', 'Description', 'Publisher', 'Year', 'Institute', 'Comments', 'Resource Type', 'RelatedIdentifier', 'License')

class TokenTreeRenderer(mistune.Renderer):
    # options is required
    options = {}

    def placeholder(self):
        return []

    def __getattribute__(self, name):
        """Saves the arguments to each Markdown handling method."""
        found = TokenTreeRenderer.__dict__.get(name)
        if found is not None:
            return object.__getattribute__(self, name)

        def fake_method(*args, **kwargs):
            # return [(name, args, kwargs)]
            return [name, args]
        return fake_method

md_processor = mistune.Markdown(renderer=TokenTreeRenderer())

import pprint
pp = pprint.PrettyPrinter(indent=4)

def parse_markdown (md):
    """Parse markdown file"""

    res = {}
    stack = []
    prev_p = None
    parsed = md_processor.render(md)

    # skip non-headers at the beginning
    k = 0
    while (k+1 < len(parsed) and parsed[k] != 'header'):
        k += 2

    # start processing
    for i in range(k, len(parsed)-1 , 2):
        line = parsed[i]
        h = parsed[i+1]
        if line == 'header':
            # put prev paragraph in res
            if prev_p:
                val = ''
                if len(stack):
                    val = "\n".join(stack)
                res.update({prev_p: val})
            # set new paragraph 
            stack = []
            if h[2] in MD_HEADERS and h[1] == HEADER_STEP:
                prev_p = h[2]
            else:
                prev_p = None
        elif line == 'paragraph':
            print("h: %r, prev_p: %s" % (h, prev_p))
            if h[0][0] in ('text'):
                if h[0][1]:
                    stack.append(h[0][1][0])

    # put last field if available
    prev_p and res.update({prev_p: "\n".join(stack) if len(stack) else ''})

    return res

def parse_markdown_doi (md):
    res = {}
    stack = []
    content = []
    parsed = md_processor.render(md)

    for i in range(0, len(parsed)-1, 2):
        str = parsed[i]
        h = parsed[i+1]
        if str == 'header':
            if len(stack) > 0:
                header = stack.pop()
                if "\n".join(content):
                    res[header] = "\n".join(content)
                content = []
            if h[2] in MD_HEADERS and h[1] == HEADER_STEP:
                stack.append(h[2])
        elif str == 'paragraph':
            if len(stack) > 0:
                txt_list = []
                for i1 in range(0, len(h[0])-1, 2):
                    if h[0][i1] in ['text', 'autolink']:
                        txt_list.append(h[0][i1+1][0])
                val = ''.join(txt_list).strip()
                if val:
                    content.append(val)

    if len(stack) > 0 and "\n".join(content):
        res[stack.pop()] = "\n".join(content)
    return res


def truncate_str(s, max_len=256, sfx='...'):
    """
    Cut too long str
    """
    if s is None:
        return None;
    return (s[:max_len - len(sfx)] + sfx) if len(s) > max_len else s

def get_repo_root_dir(repo_id):
    """
    Get repo root dir from object storage
    """
    repo = get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
    return dir
