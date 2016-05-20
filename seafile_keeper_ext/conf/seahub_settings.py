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
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
FILE_SERVER_ROOT = 'http://keeper.mpdl.mpg.de/seafhttp'

# Enalbe or disalbe registration on web. Default is `False`.
# ENABLE_SIGNUP = True

# PRO Options

BRANDING_CSS = 'custom/keeper.css'


# Whether to show the used traffic in user's profile popup dialog. Default is True
SHOW_TRAFFIC = True

# Allow administrator to view user's file in UNENCRYPTED libraries
# through Libraries page in System Admin. Default is False.
ENABLE_SYS_ADMIN_VIEW_REPO = True

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
SEND_EMAIL_ON_ADDING_SYSTEM_MEMBER = False

# Whether to send email when a system admin resetting a user's password. Default is `True`.
SEND_EMAIL_ON_RESETTING_USER_PASSWD = False
