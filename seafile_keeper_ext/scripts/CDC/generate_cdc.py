#!/usr/bin/env python


import os
from seahub import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")

from seaserv import seafile_api
from seahub.settings import SERVICE_URL, SERVER_EMAIL, DATABASES
from seahub.share.models import FileShare

from seafobj import commit_mgr, fs_mgr
from subprocess import check_call


import mistune

import MySQLdb
db = MySQLdb.connect(host=DATABASES['default']['HOST'],
                     user=DATABASES['default']['USER'],
                     passwd=DATABASES['default']['PASSWORD'],
                     db="keeper-db")
cur = db.cursor()

MAX_INT = 2147483647
ARCHIVE_METADATA_FILE = 'archive-metadata.md'
TEMPLATE_DESC = u"Template for creating 'My Libray' for users"

CDC_GENERATOR_MAIN_CLASS = "de.mpg.mpdl.keeper.CDCGenerator.MainApp"
CDC_GENERATOR_JARS =  "CDCGenerator.jar:fonts-ext.jar"
CDC_PDF_PREFIX = "cared-data-certificate_"

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
    """parse markdown string"""  
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

def is_certified (repo_id):
    """Check whether the repo is already certified"""
    cur.execute("SELECT * FROM cdc_repos WHERE repo_id='" + repo_id + "'")
    return len(cur.fetchall()) > 0;

def validate (cdc_dict):
    print """Validate the CDC mandatory fields and content..."""
    # 1. check mandatory fields
    s1 = set(cdc_dict.keys())
    s2 = set(cdc_headers_mandatory)
    valid = s2.issubset(s1)
    #2. check content"
    # TODO:
    return valid;

def get_repo_share_url (repo_id, owner):
    share = FileShare.objects.get_dir_link_by_path(owner, repo_id, "/")
    if not share:
        raise Exception('Cannot get share URL: repo is not shared')
    return SERVICE_URL + '/' + share.s_type + '/' + share.token;

def register_cdc_in_db(repo_id, owner):
    try:
        cur.execute("INSERT INTO cdc_repos (`repo_id`, `cdc_id`, `owner`, `created`) VALUES ('" + repo_id + "', NULL, '" + owner + "', CURRENT_TIMESTAMP)")
        db.commit()
    except Exception as err:
        db.rollback()
        raise Exception('Cannot register in DB: ' + ": ".join(str(i) for i in err))

    cur.execute("SELECT * FROM cdc_repos WHERE repo_id='" + repo_id + "'")
    cdc_id = cur.fetchone()[1]
    return str(cdc_id) 


###### START

repos_all = seafile_api.get_repo_list(0, MAX_INT)
#Filter global Lib Template
#Filter already certified repos
repos_all = [r for r in repos_all if r.repo_desc != TEMPLATE_DESC and not is_certified(r.id)]


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
                    """ java -cp "CDCGenerator.jar:fonts-ext.jar" de.mpg.mpdl.keeper.CDCGenerator.MainApp -i 1 -aa "Author1, Author2" -d "Description" -c "keeper@mpdl.mpg.de" -u "http://keeper.mpdl.mpg.de/library" -t "Project 1" a.pdf """
                    print "Register CDC in DB..."
                    cdc_id = register_cdc_in_db(repo.id, owner) 

                    print "Generate CDC..."
                    cdc_pdf = CDC_PDF_PREFIX + cdc_id + ".pdf"
                    args = [ "java", "-cp", CDC_GENERATOR_JARS, CDC_GENERATOR_MAIN_CLASS, 
                            "-i", "\"" + cdc_id + "\"", 
                            "-t", "\"" + cdc_dict['Title']  + "\"", 
                            "-aa", "\"" + cdc_dict['Authors']  + "\"", 
                            "-d", "\"" + cdc_dict['Description']  + "\"", 
                            "-c", "\"" + owner  + "\"", 
                            "-u", "\"" + get_repo_share_url(repo.id, owner)  + "\"",
                            cdc_pdf
                            ]
                    check_call(args)

                    print "Add " + cdc_pdf + " to the repo..."
                    tmp_path = os.path.abspath(cdc_pdf)
                    seafile_api.post_file(repo.id, tmp_path, "/", cdc_pdf, SERVER_EMAIL)
                    os.remove(tmp_path)
                    print "OK"

                    print "Send CDC email and keeper notification..."
                    # TODO:
        except Exception as err:
            print err
            err_list.append({'name:':repo.name, 'id':repo.id, 'err':str(err)})


print "Amount of libraries:", len(repos_all)    

print "Problematic repos:", err_list

db.close()

exit(0)
