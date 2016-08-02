#!/usr/bin/env python

from seaserv import seafile_api
from seafobj import commit_mgr, fs_mgr
from subprocess import call

import mistune

MAX_INT = 2147483647
ARCHIVE_METADATA_FILE = 'archive-metadata.md'
TEMPLATE_DESC = u"Template for creating 'My Libray' for users"

HEADER_STEP = 2
cdc_headers =  ['Title', 'Authors', 'Year', 'Publisher', 'Genre', 'Description', 'Comments']
cdc_headers_mandatory =  ['Title', 'Authors', 'Year', 'Description']
err_list = []

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
            #return [(name, args, kwargs)]
            return [name, args]
        return fake_method

md_processor = mistune.Markdown(renderer=TokenTreeRenderer())

def parse_markdown (md):
    "parse markdown string"  
    cdc = {}
    stack = []
    parsed = md_processor.render(md)

    for i in range(0, len(parsed)-1, 2):
        str = parsed[i]
        h = parsed[i+1]  
        if str == 'header':
            if h[2] in cdc_headers and h[1] == HEADER_STEP:
                stack.append(h[2])
        elif str == 'paragraph':
            if len(stack) > 0:
                txt_list = [] 
                for i1 in range(0, len(h[0])-1, 2):
                    if h[0][i1] == 'text':
                        txt_list.append(h[0][i1+1][0])
                val = '\n'.join(txt_list).strip()
                #print val
                if val:
                    cdc[stack.pop()] = val
                else:
                    stack.pop()
    return cdc;

def is_certified (id):
    "Check whether the CDC already exists"
    return False;

def validate (cdc_dict):
    "Validate the CDC mandatory fields and content"
    "1. check mandatory fields"
    s1 = set(cdc_dict.keys())
    s2 = set(cdc_headers_mandatory)
    valid = s2.issubset(s1)
    "2. check content"
    return valid;


###### START

repos_all = seafile_api.get_repo_list(0, MAX_INT)
#Filter global Lib Template
repos_all = [r for r in repos_all if r.repo_desc != TEMPLATE_DESC]
#Filter already certified repos
repos_all = [r for r in repos_all if not is_certified(r.id)]


for repo in repos_all:

    if not repo.encrypted: 
        commits = seafile_api.get_commit_list(repo.id, 0, 1)
       
        commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)

        try:
            dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
            file = dir.lookup(ARCHIVE_METADATA_FILE)
            if file:
                owner = seafile_api.get_repo_owner(repo.id)
                print "Repo to be certified: %s %40s %30s" % (repo.id, repo.name, owner)
                cdc_dict = parse_markdown(file.get_content())
                if validate(cdc_dict):
                    print "Generate CDC pdf..."
                    call(["ls", "-la"])
                    print "Add CDC pdf to the repo..."
                    print "Register CDC in DB..."
                    print "Send CDC email and keeper notification..."
        except Exception as err:
            err_list.append({'name:':repo.name, 'id':repo.id, 'err':str(err)})


print "Amount of libraries:", len(repos_all)    

print "Problematic repos:", err_list


#TEST

#sample = open('sample.md')
#md = sample.read()

#cdc_dict = parse_markdown(md)
#print cdc_dict

