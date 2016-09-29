import os
import sys

import datetime
import re

import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings") 

from seaserv import seafile_api
from seahub.settings import SERVICE_URL, SERVER_EMAIL, DATABASES, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT, ARCHIVE_METADATA_TARGET
from seahub.share.models import FileShare

from seahub.profile.models import Profile
from seafobj import commit_mgr, fs_mgr
from subprocess import check_call

from keeper.default_library_manager import get_keeper_default_library

import mistune

from string import Template

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


import MySQLdb

MAX_INT = 2147483647
TEMPLATE_DESC = u"Template for creating 'My Libray' for users"

CDC_GENERATOR_MAIN_CLASS = "de.mpg.mpdl.keeper.CDCGenerator.MainApp"
CDC_GENERATOR_JARS =  ('CDCGenerator.jar', 'fonts-ext.jar')
CDC_PDF_PREFIX = "cared-data-certificate_"
CDC_LOGO = 'Keeper-Cared-Data-Certificate-Logo.png'
CDC_EMAIL_TEMPLATE = 'cdc_mail_template.html'
CDC_EMAIL_SUBJECT = 'KEEPER Cared Data Certificate'

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

if DEBUG:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

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
                if val:
                    cdc[stack.pop()] = val
                else:
                    stack.pop()
    return cdc;

def is_certified (db, cur, repo_id):
    """Check whether the repo is already certified"""
    if DEBUG:
        return False
    cur.execute("SELECT * FROM cdc_repos WHERE repo_id='" + repo_id + "'")
    return len(cur.fetchall()) > 0;

def validate (cdc_dict):
    logging.info("""Validate the CDC mandatory fields and content...""")
    # 1. check mandatory fields
    s1 = set(cdc_dict.keys())
    s2 = set(cdc_headers_mandatory)
    valid = s2.issubset(s1)
    #2. check content"
    """Year checking"""
    format = "%Y"
    try:
        d = datetime.datetime.strptime(cdc_dict['Year'], format)
    except Exception as err:
        logging.info("Wrong year: " + cdc_dict['Year'])
        valid = False
    """Authors/Affiliations checking"""
    # Lastname1, Firstname1; Affiliation11, Affiliation12, ...
    # Lastname2, Firstname2; Affiliation21, Affiliation22, ..
    # ...
    pattern = re.compile("^\s*\w+,(\s+[\w.]+)+(;\s*\S+\s*)+")
    for line in cdc_dict['Authors'].splitlines():
        if not re.match(pattern, line):
            logging.info('Wrong Author/Affiliation string: ' + line) 
            valid = False

    logging.info('valid' if valid else 'not valid') 
    return valid;

def get_repo_share_url (repo_id, owner):
    """Repo should be shared to be certified?"""
    share = FileShare.objects.get_dir_link_by_path(owner, repo_id, "/")
    if not share:
        raise Exception('Cannot get share URL: repo is not shared')
    return SERVICE_URL + '/' + share.s_type + '/' + share.token;

def register_cdc_in_db(db, cur, repo_id, owner):
    logging.info("""Register CDC in keeper-db""")
    try:
        cur.execute("INSERT INTO cdc_repos (`repo_id`, `cdc_id`, `owner`, `created`) VALUES ('" + repo_id + "', NULL, '" + owner + "', CURRENT_TIMESTAMP)")
        db.commit()
    except Exception as err:
        db.rollback()
        if not DEBUG:
            raise Exception('Cannot register in DB: ' + ": ".join(str(i) for i in err))

    cur.execute("SELECT * FROM cdc_repos WHERE repo_id='" + repo_id + "'")
    cdc_id = str(cur.fetchone()[1])
    logging.info("Sucessfully registered, cdc_id: " + cdc_id)
    return cdc_id 

def send_email (to, msg_ctx):
    logging.info("Send CDC email and keeper notification...")
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

        f = open(MODULE_PATH + '/' + CDC_EMAIL_TEMPLATE)
        tmpl = Template(f.read())   
        
        msg = MIMEMultipart()
        msg.attach(MIMEText(tmpl.substitute(msg_ctx), 'html'))
        msg['Subject'] = CDC_EMAIL_SUBJECT
#        msg['Cc'] = SERVER_EMAIL
        f = open(MODULE_PATH + '/' + CDC_LOGO, 'rb').read()
        logo = MIMEImage(f, name=CDC_LOGO)
        msg.attach(logo)
        try:
            server.sendmail(SERVER_EMAIL, [to, SERVER_EMAIL], msg.as_string())
        finally:    
            server.quit()

    except Exception as err:
        raise Exception('Cannot send email: ' + str(err))

    logging.info("Sucessfully sent")

def has_at_least_one_creative_dirent(dir):

    #ARCHIVE_METADATA_TARGET should be in    
    check_set = set([ARCHIVE_METADATA_TARGET])

    #+KEEPER_DEFAULT_LIBRARY stuff
    kdl = get_keeper_default_library()
    if kdl:
        dirents = [d.obj_name for d in kdl['dirents']]
        if dirents:
            check_set.update(dirents)
   
    #get dir files
    files = dir.get_files_list()
    if files:
        files = [f for f in files if f.name not in check_set]
    
    #get dir dirs 
    dirs = dir.get_subdirs_list()
    if dirs:
        dirs = [d for d in dirs if d.name not in check_set]

    return (len(files) + len(dirs)) > 0 


def generate_certificate(repo):
    """ Generate Cared Data Certificate according to markdown file """

    #exit if repo encrypted
    if repo.encrypted:
        return False

    # exit if repo is system template
    if repo.rep_desc == TEMPLATE_DESC:
        return False
    
    # get latest version of the ARCHIVE_METADATA_TARGET
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
    file = dir.lookup(ARCHIVE_METADATA_TARGET)
    
    #exit if no metadata file exists
    if not file:
        return False

    #check wether there is at least one creative dirent
    if not has_at_least_one_creative_dirent(dir):
        return False
    logging.info('Repo has creative dirents')
    

    try:
        db = MySQLdb.connect(host=DATABASES['default']['HOST'],
                 user=DATABASES['default']['USER'],
                 passwd=DATABASES['default']['PASSWORD'],
                 db="keeper-db")
        cur = db.cursor()
        
        if is_certified(db, cur, repo.id):
            return False

        owner = seafile_api.get_repo_owner(repo.id)
        logging.info("Certifying repo id: %s, name: %s, owner: %s ..." % (repo.id, repo.name, owner))
        cdc_dict = parse_markdown(file.get_content())
        if validate(cdc_dict):

            cdc_id = register_cdc_in_db(db, cur, repo.id, owner)

            logging.info("Generate CDC PDF...")
            cdc_pdf = CDC_PDF_PREFIX + cdc_id + ".pdf"
            # TODO: specify which url should be in CDC
            # as tmp decision: SERVICE_URL
            # repo_share_url = get_repo_share_url(repo.id, owner)
            repo_share_url = SERVICE_URL 
            jars = ":".join(map(lambda e : MODULE_PATH + '/' + e, CDC_GENERATOR_JARS))
            args = [ "java", "-cp", jars, CDC_GENERATOR_MAIN_CLASS, 
                    "-i", "\"" + cdc_id + "\"", 
                    "-t", "\"" + cdc_dict['Title']  + "\"", 
                    "-aa", "\"" + cdc_dict['Authors']  + "\"", 
                    "-d", "\"" + cdc_dict['Description']  + "\"", 
                    "-c", "\"" + owner  + "\"", 
                    "-u", "\"" + repo_share_url  + "\"",
                    cdc_pdf ]
            check_call(args)
            tmp_path = os.path.abspath(cdc_pdf)
            logging.info("PDF sucessfully generated") 

            logging.info("Add " + cdc_pdf + " to the repo...")
            seafile_api.post_file(repo.id, tmp_path, "/", cdc_pdf, SERVER_EMAIL)
            logging.info("Sucessfully added")

            if not DEBUG:
                nick = Profile.objects.get_profile_by_user(owner).nickname
                send_email(owner, {'USER_NAME': nick if nick else owner, 'PROJECT_NAME':repo.name})
            
            #TODO: Send seafile notification
    except Exception as err:
        logging.info(str(err))
    finally: 
        db.close()
        if 'tmp_path' in vars() and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return True


#test 
if DEBUG:
    repo = seafile_api.get_repo('eba0b70c-8d20-4949-841b-29f13c5246fd')
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
    print has_at_least_one_creative_dirent(dir)
