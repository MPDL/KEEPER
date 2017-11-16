SECRET_KEY = "__SECRET_KEY__"

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
        'LOCATION': ['__MEMCACHED_SERVER_1__', '__MEMCACHED_SERVER_2__', '__MEMCACHED_SERVER_3__'],
        'OPTIONS': {
            'ketama': True,
            'remove_failed': 1,
            'retry_timeout': 3600,
            'dead_timeout': 3600
        }
    }
}

AVATAR_FILE_STORAGE = 'seahub.base.database_storage.DatabaseStorage'

COMPRESS_CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'

FILE_SERVER_ROOT = '__SERVICE_URL__/seafhttp'

# Enalbe or disalbe registration on web. Default is `False`.
# ENABLE_SIGNUP = True

# PRO Options

BRANDING_CSS = 'custom/keeper.css'

LOGO_PATH = 'custom/__LOGO_IMG__'

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

TEST_SERVER="__TEST_SERVER__"
TEST_SERVER_ADMIN="__TEST_SERVER_ADMIN__"
TEST_SERVER_PASSWORD="__TEST_SERVER_ADMIN_PASSWORD__"


# Enable LibreOffice Online
ENABLE_OFFICE_WEB_APP = False

# Url of LibreOffice Online's discovery page
# The discovery page tells Seafile how to interact with LibreOffice Online when view file online
# You should change `https://collabora.mpdl.mpg.de/hosting/discovery` to your actual LibreOffice Online server address
#OFFICE_WEB_APP_BASE_URL = 'https://collabora.mpdl.mpg.de/hosting/discovery'
OFFICE_WEB_APP_BASE_URL = 'https://share.mpdl.mpg.de/hosting/discovery'

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
