SECRET_KEY = "__SECRET_KEY__"

DATABASES = {
    'defaul': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'seahub-db',
        'USER': '__DB_USER__',
        'PASSWORD': '__DB_PASSWORD__',
        'HOST': '__DB_HOST__',
        'PORT': '__DB_PORT__',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
FILE_SERVER_ROOT = '__SERVICE_URL__/seafhttp'

# Enalbe or disalbe registration on web. Default is `False`.
# ENABLE_SIGNUP = True

# PRO Options

BRANDING_CSS = 'custom/keeper.css'


# Whether to show the used traffic in user's profile popup dialog. Default is True
SHOW_TRAFFIC = True

# Allow administrator to view user's file in UNENCRYPTED libraries
# through Libraries page in System Admin. Default is False.
ENABLE_SYS_ADMIN_VIEW_REPO = False

DESKTOP_CUSTOM_LOGO = 'custom/keeper-client-logo.png'
DESKTOP_CUSTOM_BRAND = 'KEEPER'

# MPDL EMAIL settings
EMAIL_USE_TLS = True
EMAIL_HOST = '__EMAIL_HOST__'        # smpt server
EMAIL_HOST_USER = '__EMAIL_HOST_USER__'    # username and domain
EMAIL_HOST_PASSWORD = '__EMAIL_HOST_PASSWORD__'    # password
EMAIL_PORT = '__EMAIL_PORT__'
###### DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = '__DEFAULT_FROM_EMAIL__'
SERVER_EMAIL = '__SERVER_EMAIL__'

# Whether to send email when a system admin adding a new member. Default is `True`.
SEND_EMAIL_ON_ADDING_SYSTEM_MEMBER = True

# Whether to send email when a system admin resetting a user's password. Default is `True`.
SEND_EMAIL_ON_RESETTING_USER_PASSWD = True

# Multiple Organization/Institution User Management, see http://manual.seafile.com/deploy_pro/multi_institutions.html
MULTI_INSTITUTION = True

EXTRA_MIDDLEWARE_CLASSES = (
    'seahub.institutions.middleware.InstitutionMiddleware',
)

ENABLE_SETTINGS_VIA_WEB = True

# KEEPER specific settings
ARCHIVE_METADATA_TARGET = 'archive-metadata.md'
ARCHIVE_METADATA_TEMPLATE = 'archive_metadata_template.md'

import logging

def repo_created_callback(sender, **kwargs):
    try:
        import os
        from seaserv import seafile_api
        import keeper.cdc.cdc_manager
    except ImportError:
        return 
    creator = kwargs['creator']
    repo_id = kwargs['repo_id']
    repo_name = kwargs['repo_name']
    logging.info("Add %s to the repo %s..." % (ARCHIVE_METADATA_TARGET, repo_id))
    try:
        seafile_api.post_file(repo_id, os.path.dirname(os.path.abspath(keeper.cdc.cdc_manager.__file__)) + '/' + ARCHIVE_METADATA_TEMPLATE, "/", ARCHIVE_METADATA_TARGET, SERVER_EMAIL)
        logging.info("Sucessfully added")
    except:
        pass

def file_modified_callback(sender, **kwargs):
    try:
        from keeper.cdc.cdc_manager import generate_certificate
    except ImportError:
        return 
    repo = kwargs['repo']
    filename = kwargs['filename']
    parent_dir = kwargs['parent_dir']
    if filename == ARCHIVE_METADATA_TARGET and parent_dir == "/":
        try:
            logging.info("Changed %s, certifying repo: %s ..." % (filename, repo.id))
            generate_certificate(repo)
        except:
            pass
