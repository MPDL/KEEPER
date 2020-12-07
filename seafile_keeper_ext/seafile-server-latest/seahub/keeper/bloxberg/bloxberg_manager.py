import logging
import datetime
import requests
import zipfile
import os, errno
import PyPDF2
import sys
import hashlib
import json
from seahub.api2.utils import json_response
from seahub import settings
from keeper.catalog.catalog_manager import get_catalog
from django.http import JsonResponse
from seafobj import commit_mgr, fs_mgr
from seaserv import seafile_api, get_repo
from keeper.models import BCertificate
from seahub.notifications.models import UserNotification
from seahub.base.templatetags.seahub_tags import email2nickname
from seahub.utils import send_html_email, get_site_name
from seahub.settings import ARCHIVE_METADATA_TARGET
from keeper.common import parse_markdown_doi
from django.utils.translation import ugettext as _
from lds_merkle_proof_2019.merkle_proof_2019 import MerkleProof2019
from seahub.settings import BLOXBERG_SERVER, BLOXBERG_CERTS_STORAGE
from django.db import connection
from threading import Thread
from pathlib import Path
# Get an instance of a logger
logger = logging.getLogger(__name__)

BLOXBERG_CERTIFY_URL = BLOXBERG_SERVER + "/createBloxbergCertificate"
BLOXBERG_GENERATE_CERTIFICATE_URL = BLOXBERG_SERVER + "/generatePDF"
MSG_TYPE_KEEPER_BLOXBERG_MSG = 'bloxberg_msg'

def generate_certify_payload(user_email, checksumArr):
    metadataJson = {
        'authors': email2nickname(user_email)
    }
    data = {
        "publicKey": "0x69575606E8b8F0cAaA5A3BD1fc5D032024Bb85AF",
        "crid": checksumArr,
        "cridType": "sha2-256",
        "enableIPFS": False,
        "metadataJson": json.dumps(metadataJson)
    }
    return data

def hash_file_payload(repo_id, path, user_email):
    file = get_file_by_path(repo_id, path)
    checksum = hash_file(file)

def hash_file(file):
    BUF_SIZE = 65536  # read stuff in 64kb chunks
    file_hash_inc = hashlib.sha256()
    stream = file.get_stream()

    while True:
        data = stream.read(BUF_SIZE)
        if not data:
            break
        file_hash_inc.update(data)
    return file_hash_inc.hexdigest()

def hash_library(repo_id, user_email):
    repo = seafile_api.get_repo(repo_id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, get_commit_root_id(repo_id))
    file_map = get_all_files_by_path(dir, repo, '', {})
    return file_map

def decode_metadata(metadata_json):
    mp2019 = MerkleProof2019()
    if isinstance(metadata_json, dict) and 'proof' in metadata_json:
        encoded_value = metadata_json['proof']['proofValue']
    else:
        encoded_value = metadata_json[0]['proof']['proofValue']
    decoded_json = mp2019.decode(encoded_value)
    return decoded_json['anchors'][0].split(':')[-1]

def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator

@start_new_thread
def generate_bloxberg_certificate_pdf(metadata_json, transaction_id, repo_id, user_email):
    path = BLOXBERG_CERTS_STORAGE + '/' + user_email + '/' + transaction_id

    response_generate_certificate = request_generate_pdf(metadata_json)
    if response_generate_certificate is not None:
        if response_generate_certificate.status_code == 200:
            Path(path).mkdir(parents=True, exist_ok=True)
            try:
                # with open(path + '/' + repo_id + '_' + transaction_id + '.pdf', 'wb') as f:
                zipname = repo_id + '_' + transaction_id + '.zip'
                with open(path + '/' + zipname, 'wb') as f:
                    for chunk in response_generate_certificate:
                        f.write(chunk)
                logger.info(zipname + ' is saved.')
                with zipfile.ZipFile(path + '/' + zipname, 'r') as zip_ref:
                    zip_ref.extractall(path + '/')
                silentremove(path + '/' + zipname)
                scan_certificates(path)

                connection.close()
                logger.error("Thread ends, close db connection")
            except IOError as error:
                logger.info(error)

def request_create_bloxberg_certificate(certify_payload):
    try:
        response = requests.post(BLOXBERG_CERTIFY_URL, json=certify_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def request_bloxberg(certify_payload):
    try:
        response = requests.post(BLOXBERG_CERTIFY_URL, json=certify_payload)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def request_generate_pdf(certificate_payload):
    try:
        response = requests.post(BLOXBERG_GENERATE_CERTIFICATE_URL, json=certificate_payload, stream=True)
        return response
    except ConnectionError as e:
        logger.error(str(e))

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def scan_certificates(directory):
    for entry in os.scandir(directory):
        if entry.path.endswith(".pdf") and entry.is_file():
            pdfPath, pdfName = os.path.split(entry.path)
            handler = open(entry.path, 'rb')
            reader = PyPDF2.PdfFileReader(handler)
            dictionary = getAttachments(reader)
            for fName, fData in dictionary.items():
                metadata_json = json.loads(fData)
                fHash = metadata_json['crid']
                transaction_id = decode_metadata(metadata_json)
                try:
                    certificate = BCertificate.objects.get_semi_bloxberg_certificate(transaction_id, fHash)
                    certificate.pdf = pdfName
                    certificate.md_json = fData
                    certificate.save()
                except BCertificate.DoesNotExist:
                    logger.error("Update certificate pdf failed, certificate not found")

def getAttachments(reader):
      """
      Retrieves the file attachments of the PDF as a dictionary of file names
      and the file data as a bytestring.

      :return: dictionary of filenames and bytestrings
      """
      catalog = reader.trailer["/Root"]
      fileNames = catalog['/Names']['/EmbeddedFiles']['/Names']
      attachments = {}
      for f in fileNames:
          if isinstance(f, str):
              name = f
              dataIndex = fileNames.index(f) + 1
              fDict = fileNames[dataIndex].getObject()
              fData = fDict['/EF']['/F'].getData()
              attachments[name] = fData

      return attachments

def get_file_by_path(repo_id, path):
    repo = seafile_api.get_repo(repo_id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, get_commit_root_id(repo_id))
    paths = [_f for _f in path.split("/") if _f]
    for path in paths:
        dir = dir.lookup(path)
    return dir

def get_all_files_by_path(dir, repo, path, dir_map):
    for dName, dObj in list(dir.dirents.items()):
        dPath = path + os.sep + dObj.name
        if dObj.is_dir():
            get_all_files_by_path(fs_mgr.load_seafdir(repo.id, repo.version, dObj.id), repo, dPath, dir_map)
        if dObj.is_file():
            dir_map.update({dPath: hash_file(dir.lookup(dObj.name))})
    return dir_map

def get_md_json(repo_id):
    repo = seafile_api.get_repo(repo_id)
    commit_id = get_latest_commit_root_id(repo)

    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit_id)
    file = dir.lookup(ARCHIVE_METADATA_TARGET)
    if not file:
        logger.info('archive-metadata.md file is not filled or missing.')

    md_dict = parse_markdown_doi(file.get_content().decode())
    if not md_dict.get('Author'):
        md_dict['Author'] = seafile_api.get_repo(repo_id).owner
    if not md_dict.get('Title'):
        md_dict['Title'] = seafile_api.get_repo(repo_id).name
    if not md_dict.get('Year'):
        md_dict['Year'] = ""

    md_json = json.dumps(md_dict)
    return md_json

def get_latest_commit_root_id(repo):
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return commit.root_id

def get_commit_id(repo_id):
    repo = seafile_api.get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    return commits[0].id

def get_commit_root_id(repo_id):
    repo = seafile_api.get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return commit.root_id

def create_bloxberg_certificate(repo_id, path, transaction_id, content_type, content_name, created_time, checksum, user_email, md, md_json):
    commit_id = get_commit_id(repo_id)
    obj_id =  BCertificate.objects.add_bloxberg_certificate(transaction_id, content_type, content_name, repo_id, path, commit_id, created_time, user_email, checksum, md, md_json)
    if content_type == 'file':
        send_notification(repo_id, path, transaction_id, created_time, user_email)
    return obj_id

def update_bloxberg_certificate(repo_id, path, commit_id, checksum, pdf):
    BCertificate.objects.get_bloxberg_certificate_by_checksum(repo_id, path, commit_id, checksum)

def certified_with_keeper(repo_id, path):
    commit_id = get_commit_id(repo_id)
    return BCertificate.objects.has_bloxberg_certificate(repo_id, path, commit_id)

def send_notification(repo_id, path, transaction_id, timestamp, user_email):
    BLOXBERG_MSG=[]
    msg = 'Your data was successfully certified!'
    msg_transaction = 'Transaction ID: ' + transaction_id
    file_name = path.rsplit('/', 1)[-1]
    BLOXBERG_MSG.append(msg)
    BLOXBERG_MSG.append(msg_transaction)

    UserNotification.objects._add_user_notification(user_email, MSG_TYPE_KEEPER_BLOXBERG_MSG,
      json.dumps({
      'message':('; '.join(BLOXBERG_MSG)),
      'transaction_id': transaction_id,
      'repo_id': repo_id,
      'link_to_file': path,
      'file_name': file_name,
      'author_name': email2nickname(user_email),
    }))

    c = {
        'to_user': user_email,
        'message_type': 'bloxberg_msg',
        'message':('; '.join(BLOXBERG_MSG)),
        'transaction_id': transaction_id,
        'repo_id': repo_id,
        'link_to_file': path,
        'file_name': file_name,
        'author_name': email2nickname(user_email),
        'timestamp': timestamp,
    }

    try:
        send_html_email(_('New notice on %s') % get_site_name(),
                                'notifications/keeper_email.html', c,
                                None, [user_email])

        logger.info('Successfully sent email to %s' % user_email)
    except Exception as e:
        logger.error('Failed to send email to %s, error detail: %s' % (user_email, e))
