# -*- coding: utf-8 -*-
import logging
import re
import json
from seafobj import commit_mgr, fs_mgr
from seaserv import seafile_api, get_repo
from seahub.api2.utils import json_response
from seahub.settings import SERVICE_URL, SERVER_EMAIL, ARCHIVE_METADATA_TARGET
from keeper.common import parse_markdown
from keeper.cdc.cdc_manager import validate_year, validate_author, validate_institute
from seahub.notifications.models import UserNotification

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)
TEMPLATE_DESC = u"Template for creating 'My Libray' for users"
MSG_TYPE_KEEPER_DOI_MSG = "doi_msg"

def get_metadata(repo_id, user_email):
    """ Read metadata from libray root folder"""
    event = None

    repo = seafile_api.get_repo(repo_id)
    commit_id = get_lastest_commit_id(repo)

    # exit if repo encrypted
    if repo.encrypted:
        return {}

    # exit if repo is system template
    if repo.rep_desc == TEMPLATE_DESC:
        return {}

    try:
        dir = fs_mgr.load_seafdir(repo.id, repo.version, commit_id)
        file = dir.lookup(ARCHIVE_METADATA_TARGET)

        if not file:
            return {}
        LOGGER.info('Repo has creative dirents')
        owner = seafile_api.get_repo_owner(repo.id)
        LOGGER.info("Certifying repo id: %s, name: %s, owner: %s ..." % (repo.id, repo.name, owner))
        doi_dict = parse_markdown(file.get_content())
        LOGGER.info(doi_dict)

        isValidate = validate(doi_dict, user_email)
        if not isValidate:
            return {}
        return doi_dict

    except Exception as err:
        LOGGER.error(str(err))
        raise err

def generate_metadata_xml(doi_dict):
    """ DataCite Metadata Generator """
    kernelVersion = "4.0"
    kernelNamespace = "http://datacite.org/schema/kernel-4"
    kernelSchema = "http://schema.datacite.org/meta/kernel-4/metadata.xsd"
    kernelSchemaLocation = kernelNamespace + " " + kernelSchema

    title = doi_dict.get('Title')
    creator = doi_dict.get('Author')
    description = doi_dict.get('Description')
    publisher = "MPDL Keeper Service, Max-Planck-Gesellschaft zur Förderung der Wissenschaften e. V."
    year = doi_dict.get('Year')
    resource_type = doi_dict.get("Resource Type")
    ## TODO: read prev_doi from database
    prev_doi = None

    header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + br() + "<resource xmlns=\"" + kernelNamespace + "\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"" + kernelSchemaLocation + "\">" + br()
    xml = header
    # Mandatory Elements: Title(s), Creator(s), Publisher, PublicationYear, resourceType, descriptions, resource(is it optional)
    # NameIdentifier, affiliation is not used
    xml += ota("identifier", attrib("identifierType", "DOI")) + ct("identifier") +br()
    xml += ot("titles") + br() + tab(1) + ot("title") + title + ct("title") + br() + ct("titles") + br()
    xml += ot("creators") + br() + tab(1) + ot("creator") + br() + tab(2) + ot("creatorName") + creator + ct("creatorName") + br() + tab(1) + ct("creator") + br() + ct("creators") + br()
    xml += ot("publisher") + publisher + ct("publisher") + br()
    xml += ot("publicationYear") + year + ct("publicationYear") + br()
    xml += ota("resourceType", attrib("resourceTypeGeneral", "Dataset")) + resource_type + ct("resourceType") + br()
    xml += ot("descriptions") + br() + tab(1) + ota("description", attrib("descriptionType", "Abstract")) + description + ct("description") + br() + ct("descriptions") + br()
    if prev_doi is not None:
        xml += ot("relatedIdentifiers") +br() + tab(1) + ota("relatedIdentifier", attrib("relatedIdentifierType", "DOI") + " " + attrib("relationType", "IsNewVersionOf")) + prev_doi + ct("relatedIdentifierType") + br() + ct("relatedIdentifiers") + br()
    xml += ct("resource")
    return xml

def get_lastest_commit_id(repo):
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return commit.root_id

def validate(doi_dict, user_email):
    LOGGER.info("""Validate the DOI mandatory fields and content...""")

    global DOI_MSG
    DOI_MSG = []

    # 1. check mandatory fields
    # todo add more mandatory fields
    doi_headers_mandatory = ['Title', 'Author', 'Year', 'Description', 'Institute', 'Resource Type']
    s1 = set(doi_dict.keys())
    s2 = set(doi_headers_mandatory)

    mandatory_field_valid = s2.issubset(s1)
    if not mandatory_field_valid:
        missing_fields = s2.difference(s1)
        if len(missing_fields) > 1:
            msg =  'DOI:'+ ', '.join(missing_fields) + ' fields are not filled'
        elif len(missing_fields) == 1:
            msg =  'DOI:'+ missing_fields.pop() + ' field is not filled'
        DOI_MSG.append(msg)

    # 2. check content
    year_valid = validate_year(doi_dict.get('Year'))
    if not year_valid:
        msg = 'DOI year field is not valid'
        DOI_MSG.append(msg)
    author_valid = validate_author(doi_dict.get('Author'))
    if not author_valid:
        msg = 'DOI author field is not valid'
        DOI_MSG.append(msg)
    institute_valid = validate_institute(doi_dict.get('Institute'))
    if not institute_valid:
        msg = 'DOI institute field is not valid'
        DOI_MSG.append(msg)
    resource_type_valid = validate_resource_type(doi_dict.get("Resource Type"))
    if not resource_type_valid:
        msg = 'Wrong Institution string'
        DOI_MSG.append(msg)

    valid = mandatory_field_valid and year_valid and author_valid and institute_valid and resource_type_valid
    LOGGER.info('DOI metadata are {}:\n{}'.format('valid' if valid else 'not valid', '\n'.join(DOI_MSG)))
    if not valid and user_email is not None:
        send_notification(DOI_MSG, user_email)
    return valid

def validate_resource_type(txt):
    """resource_type checking, options:
    Libray, Project
    """
    valid = True
    if txt:
        pattern = re.compile("^(Library|Project)$", re.UNICODE)
        if not re.match(pattern, txt.decode('utf-8')):
            valid = False
            msg = 'Wrong Institution string: ' + txt
            LOGGER.info(msg)
    else:
        valid = False
    return valid

def br():
    return "\n"

def tab(number):
    tabs = ""
    if number is not None and number > 0:
        for i in range (1, number+1):
            tabs += "\t"
    else:
        tabs = "\t"
    return tabs

def attrib(attrib, value):
    if value:
        if attrib:
            attrib += " "
        attrib += "=\"" + value + "\""
    return attrib

def ota(tag, attr):
    if attr:
        return "<" + tag + " " + attr + ">"
    else:
        return ot(tag)

def ot(tag):
    return "<" + tag + ">"

def ct(tag):
    return "</" + tag + ">"

def send_notification(DOI_MSG, user_email):
    UserNotification.objects._add_user_notification(user_email, MSG_TYPE_KEEPER_DOI_MSG,
        json.dumps({
            'message': ('; '.join(DOI_MSG)),
    }))
