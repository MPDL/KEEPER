SECRET_KEY = __SECRET_KEY__

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'seahub-db',
        'USER': '__DB_USER__',
        'PASSWORD': '__DB_PASSWORD__',
        'HOST': '__DB_HOST__',
        'PORT': '__DB_PORT__',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    },
    'keeper': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'keeper-db',
        'USER': '__DB_USER__',
        'PASSWORD': '__DB_PASSWORD__',
        'HOST': '__DB_HOST__',
        'PORT': '__DB_PORT__',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    }
}

DATABASE_ROUTERS = ['keeper.dbrouter.DbRouter',]

CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': '__MEMCACHED_SERVER__',
    }
}

# Logging
import os
LOG_DIR = os.environ.get('SEAHUB_LOG_DIR', '/tmp')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(funcName)s %(message)s'
        },
        'syslog-django_request': {
            'format': '__SYSLOG_IDENT__ django_request: %(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(funcName)s %(message)s'
        },
        'syslog-seahub': {
            'format': '__SYSLOG_IDENT__ seahub: %(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(funcName)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'seahub.log'),
            'maxBytes': 1024*1024*10, # 10 MB
            'backupCount': 52,
            'formatter':'standard',
        },
        'request_handler': {
                'level':'INFO',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'seahub_django_request.log'),
                'maxBytes': 1024*1024*10, # 10 MB
                'backupCount': 52,
                'formatter':'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'syslog-django_request': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': ('syslog-mpcdf.mpdl.mpg.de', 514),
            'facility': '__SYSLOG_FACILITY__',
            'formatter': 'syslog-django_request'
        },
        'syslog-seahub': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': ('syslog-mpcdf.mpdl.mpg.de', 514),
            'facility': '__SYSLOG_FACILITY__',
            'formatter': 'syslog-seahub'
        },
     },
    'loggers': {
        '': {
            'handlers': ['default', 'syslog-seahub'],
            'level': 'INFO',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler', 'mail_admins', 'syslog-django_request'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
# 'address': 'syslog-mpcdf.mpdl.mpg.de',
# 'address': '/dev/log',
AVATAR_FILE_STORAGE = 'seahub.base.database_storage.DatabaseStorage'

COMPRESS_CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'

FILE_SERVER_ROOT = '__SERVICE_URL__/seafhttp'

# Enalbe or disalbe registration on web. Default is `False`.
# ENABLE_SIGNUP = True

# PRO Options

BRANDING_CSS = 'custom/keeper.css'

LOGO_PATH = 'custom/__LOGO_IMG__'

FAVICON_PATH = 'img/favicon.png'

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

ENABLE_UPLOAD_FOLDER = True

# KEEPER specific settings
ARCHIVE_METADATA_TARGET = 'archive-metadata.md'
KEEPER_DEFAULT_LIBRARY = 'Keeper Default Library'
KEEPER_DB_NAME = 'keeper-db'

TEST_SERVER='__TEST_SERVER__'
TEST_SERVER_ADMIN='__TEST_SERVER_ADMIN__'
# TEST_SERVER_PASSWORD="__TEST_SERVER_ADMIN_PASSWORD__"

# Settings for background node
OFFICE_CONVERTOR_NODE = __IS_OFFICE_CONVERTOR_NODE__

OFFICE_CONVERTOR_ROOT = '__BACKGROUND_SERVER__'

# Enable LibreOffice Online
ENABLE_OFFICE_WEB_APP = __ENABLE_OFFICE_WEB_APP__

# Url of LibreOffice Online's discovery page
# The discovery page tells Seafile how to interact with LibreOffice Online when view file online
# You should change `https://collabora.mpdl.mpg.de/hosting/discovery` to your actual LibreOffice Online server address
#OFFICE_WEB_APP_BASE_URL = 'https://collabora.mpdl.mpg.de/hosting/discovery'
# OFFICE_WEB_APP_BASE_URL = 'https://share.mpdl.mpg.de/hosting/discovery'
OFFICE_WEB_APP_BASE_URL = '__OFFICE_WEB_APP_BASE_URL__'

# Expiration of WOPI access token
# WOPI access token is a string used by Seafile to determine the file's
# identity and permissions when use LibreOffice Online view it online
# And for security reason, this token should expire after a set time period
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60   # seconds

# List of file formats that you want to view through LibreOffice Online
# You can change this value according to your preferences
# And of course you should make sure your LibreOffice Online supports to preview
# the files with the specified extensions
OFFICE_WEB_APP_FILE_EXTENSION = ('ods', 'xls', 'xlsb', 'xlsm', 'xlsx','ppsx', 'ppt',
    'pptm', 'pptx', 'doc', 'docm', 'docx', 'odt', 'odp')

# Enable edit files through LibreOffice Online
ENABLE_OFFICE_WEB_APP_EDIT = True

# types of files should be editable through LibreOffice Online
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('ods', 'xls', 'xlsb', 'xlsm', 'xlsx','ppsx', 'ppt',
    'pptm', 'pptx', 'doc', 'docm', 'docx', 'odt', 'odp')
