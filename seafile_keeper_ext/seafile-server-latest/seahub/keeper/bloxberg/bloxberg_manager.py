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
from django.utils.translation import ugettext as _, activate
from lds_merkle_proof_2019.merkle_proof_2019 import MerkleProof2019
from seahub.settings import BLOXBERG_SERVER, BLOXBERG_CERTS_STORAGE, BLOXBERG_PUBLIC_KEY
from django.db import connection
from pathlib import Path
# Get an instance of a logger
logger = logging.getLogger(__name__)

BLOXBERG_CERTIFY_URL = BLOXBERG_SERVER + "/createBloxbergCertificate"
BLOXBERG_GENERATE_CERTIFICATE_URL = BLOXBERG_SERVER + "/generatePDF"
MSG_TYPE_KEEPER_BLOXBERG_MSG = 'bloxberg_msg'

def generate_certify_payload(user_email, catalog_md, checksumArr):
    metadataJson = {
        "email": user_email,
        "catalog_md": catalog_md
    }
    data = {
        "publicKey": BLOXBERG_PUBLIC_KEY,
        "crid": checksumArr,
        "cridType": "sha2-256",
        "enableIPFS": False,
        "metadataJson": json.dumps(metadataJson)
    }
    logger.info(f"Payload generated. checksumArr length: {str(len(checksumArr))}")
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

def generate_bloxberg_certificate_pdf(metadata_json, transaction_id, repo_id, obj_id, user_email, content_type, path, language_code):
    logger.info(f'Gererate PDF {obj_id}')
    activate(language_code)
    cert_path = BLOXBERG_CERTS_STORAGE + '/' + user_email + '/' + transaction_id
    try:
        response_generate_certificate = request_generate_pdf(metadata_json)
        if response_generate_certificate is not None and response_generate_certificate.status_code == 200:
            Path(cert_path).mkdir(parents=True, exist_ok=True)
            zipname = repo_id + '_' + transaction_id + '.zip'
            with open(cert_path + '/' + zipname, 'wb') as f:
                for chunk in response_generate_certificate.iter_content(chunk_size=1024):
                    f.write(chunk)
            zipsize = os.path.getsize(cert_path + '/' + zipname)
            Content_length = response_generate_certificate.headers['Content-length']
            logger.info(f'Zip is downloaded. {obj_id} size: {zipsize}/{Content_length}')
            with zipfile.ZipFile(cert_path + '/' + zipname, 'r') as zip_ref:
                zip_ref.extractall(cert_path + '/')
            silentremove(cert_path + '/' + zipname)
            scan_certificates(cert_path)
            if content_type == 'dir':
                update_snapshot_certificate(obj_id, status="DONE", transaction_id=transaction_id)
            send_final_notification(repo_id, cert_path, transaction_id, datetime.datetime.now(), user_email, content_type)
            connection.close()
            logger.info(f'Thread ends, close db connection. {obj_id}')
        else:
            error_msg = response_generate_certificate.text if response_generate_certificate is not None else "Generate pdf request failed, response is None."
            logger.info(str(response_generate_certificate))
            logger.error(error_msg)
            update_snapshot_certificate(obj_id, status="FAILED", error_msg=error_msg, transaction_id=transaction_id)

            if content_type == 'dir':
                send_failed_notice(repo_id, transaction_id, datetime.datetime.now(), user_email)
                BCertificate.objects.get_children_bloxberg_certificates(transaction_id, repo_id).delete()
            connection.close()
            logger.error(f'Generate certificates pdf failed, close db connection. {obj_id}')

    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f'obj_id: {obj_id}')
        update_snapshot_certificate(obj_id, status='FAILED', error_msg=str(e), transaction_id=transaction_id)
        send_failed_notice(repo_id, transaction_id, datetime.datetime.now(), user_email)
        BCertificate.objects.get_children_bloxberg_certificates(transaction_id, repo_id).delete()
        connection.close()
        logger.error(f'Generate PDF failed, close db connection. {obj_id}')

def update_snapshot_certificate(obj_id, status=None, error_msg=None, certificates=None, transaction_id=None, checksum=None):
    logger.info(f'Update {obj_id}')
    snapshot_certificate = get_certificate(obj_id)
    if snapshot_certificate is not None:
        if status is not None:
            snapshot_certificate.status = status
        if transaction_id is not None:
            snapshot_certificate.transaction_id = transaction_id
        if certificates is not None:
            snapshot_certificate.certificates = certificates
        if error_msg is not None:
            snapshot_certificate.error_msg = error_msg
        if checksum is not None:
            snapshot_certificate.checksum = checksum
        snapshot_certificate.save()

def request_create_bloxberg_certificate(certify_payload):
    response = requests.post(BLOXBERG_CERTIFY_URL, json=certify_payload, timeout=(5, 600))
    return response

def request_generate_pdf(certificate_payload):
    response = requests.post(BLOXBERG_GENERATE_CERTIFICATE_URL, json=certificate_payload, stream=True, timeout=(5, 7200))
    return response

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def scan_certificates(directory):
    """
    allocate pdf and md, update certificates
    """
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
                certificate = BCertificate.objects.get_semi_bloxberg_certificate(transaction_id, fHash)
                certificate.pdf = pdfName
                certificate.md_json = fData
                certificate.status = "DONE"
                certificate.save()

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
        md_dict = {}
        logger.info('archive-metadata.md file is not filled or missing.')
    else:
        md_dict = parse_markdown_doi(file.get_content().decode())
    if not md_dict.get('Author'):
        md_dict['Author'] = seafile_api.get_repo_owner(repo_id)
    if not md_dict.get('Title'):
        md_dict['Title'] = seafile_api.get_repo(repo_id).name
    if not md_dict.get('Year'):
        md_dict['Year'] = str(datetime.date.today().year)

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

def create_bloxberg_certificate(repo_id, path, transaction_id, content_type, content_name, created_time, checksum, user_email, md, md_json, status):
    commit_id = get_commit_id(repo_id)
    obj_id =  BCertificate.objects.add_bloxberg_certificate(transaction_id, content_type, content_name, repo_id, path, commit_id, created_time, user_email, checksum, md, md_json, status)
    return obj_id

def get_latest_snapshot_certificate(repo_id, path):
    commit_id = get_commit_id(repo_id)
    return BCertificate.objects.get_latest_snapshot_certificate(repo_id, commit_id, path)

def get_certificate(obj_id):
    return BCertificate.objects.get_certificate_by_obj_id(obj_id)

def send_final_notification(repo_id, path, transaction_id, timestamp, user_email, content_type):
    BLOXBERG_MSG=[]
    msg = _('Your data was successfully certified!')
    msg_transaction = 'Transaction ID: ' + transaction_id
    file_name = path.rsplit('/', 1)[-1]
    repo_name = get_repo(repo_id).repo_name
    BLOXBERG_MSG.append(msg)
    BLOXBERG_MSG.append(msg_transaction)

    UserNotification.objects._add_user_notification(user_email, MSG_TYPE_KEEPER_BLOXBERG_MSG,
      json.dumps({
      'message':('; '.join(BLOXBERG_MSG)),
      'content_type': content_type,
      'transaction_id': transaction_id,
      'repo_id': repo_id,
      'repo_name': repo_name,
      'link_to_file': path,
      'file_name': file_name,
      'author_name': email2nickname(user_email),
    }))

    c = {
        'to_user': user_email,
        'notice_count': 1,
        'message_type': 'bloxberg_msg',
        'content_type': content_type,
        'message':('; '.join(BLOXBERG_MSG)),
        'transaction_id': transaction_id,
        'repo_id': repo_id,
        'repo_name': repo_name,
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

def send_failed_notice(repo_id, transaction_id, timestamp, user_email):
    BLOXBERG_MSG=[]
    msg = _('The certification has failed, please try again in a few minutes. In case it keeps failing, please contact the Keeper Support.')
    BLOXBERG_MSG.append(msg)

    UserNotification.objects._add_user_notification(user_email, MSG_TYPE_KEEPER_BLOXBERG_MSG,
      json.dumps({
      'message':('; '.join(BLOXBERG_MSG)),
      'repo_id': repo_id,
      'author_name': email2nickname(user_email),
    }))

    c1 = {
        'to_user': user_email,
        'notice_count': 1,
        'message_type': 'certify_snapshot_failed_msg', #message_type for email
        'message':('; '.join(BLOXBERG_MSG)),
        'repo_id': repo_id,
        'author_name': email2nickname(user_email),
        'timestamp': timestamp,
    }

    try:
        send_html_email(_('New notice on %s') % get_site_name(),
                                'notifications/keeper_email.html', c1,
                                None, [user_email])

        logger.info('Successfully sent email to %s' % user_email)
    except Exception as e:
        logger.error('Failed to send email to %s, error detail: %s' % (user_email, e))

    admin_email = 'keeper@mpdl.mpg.de'
    BLOXBERG_MSG.append(f'repo_id: {repo_id}')
    BLOXBERG_MSG.append(f'transaction_id: {transaction_id}')
    c2 = {
        'to_user': admin_email,
        'notice_count': 1,
        'message_type': 'certify_snapshot_failed_msg', #message_type for email
        'message':('; '.join(BLOXBERG_MSG)),
        'repo_id': repo_id,
        'author_name': 'Keeper Admins',
        'timestamp': timestamp,
    }

    try:
        send_html_email(_('New notice on %s') % get_site_name(),
                                'notifications/keeper_email.html', c2,
                                None, [admin_email])

        logger.info('Successfully sent email to %s' % admin_email)
    except Exception as e:
        logger.error('Failed to send email to %s, error detail: %s' % (admin_email, e))

def send_start_snapshot_notification(repo_id, timestamp, user_email):
    BLOXBERG_MSG=[]
    repo_name = get_repo(repo_id).repo_name
    msg = _('Your files with the library %(name)s are currently being certified. We will inform you once the task has successfully finished. This may take a while.') % { 'name':  repo_name}
    BLOXBERG_MSG.append(msg)

    UserNotification.objects._add_user_notification(user_email, MSG_TYPE_KEEPER_BLOXBERG_MSG,
      json.dumps({
      'message':('; '.join(BLOXBERG_MSG)),
      'repo_id': repo_id,
      'author_name': email2nickname(user_email),
    }))

    c = {
        'to_user': user_email,
        'notice_count': 1,
        'message_type': 'start_snapshot_msg', #message_type for email
        'message':('; '.join(BLOXBERG_MSG)),
        'repo_id': repo_id,
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
