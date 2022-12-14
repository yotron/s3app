import os
from datetime import timedelta

# check env files
FLASK_DEBUG = 0
S3APP_DB_TYPE = "sqlite"
S3APP_PG_DB_HOST = ""
S3APP_PG_DB_NAME = "s3app"
S3APP_PG_DB_PORT = 5432
S3APP_PG_DB_USER_PW = "s3app"
S3APP_PG_DB_USER_NAME = "s3app"
S3APP_AUTH_TYPE = "database"

SECRET_KEY = "thisIsMyHiddenSecretKey"  # from S3APP_SECRET_KEY

basedir = os.path.abspath(os.path.dirname(__file__))

# The SQLAlchemy connection string.


SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "../app.db")
# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
if S3APP_DB_TYPE == "postgres":
    SQLALCHEMY_DATABASE_URI = 'postgresql://{username}:{userpw}@{dburl}:{dbport}/{dbname}'.format(
        username=S3APP_PG_DB_USER_NAME, userpw=S3APP_PG_DB_USER_PW, dburl=S3APP_PG_DB_HOST, dbport=S3APP_PG_DB_PORT,
        dbname=S3APP_PG_DB_NAME)

SESSION_TYPE = 'sqlalchemy'

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# Customizations
APP_NAME = "S3App by YOTRON"
APP_ICON = "https://www.yotron.de/img/yotron_logo.svg"

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server


# Uncomment to setup Full admin role name
AUTH_ROLE_ADMIN = 'Admin'
AUTH_USER_REGISTRATION_ROLE = "S3User"
AUTH_ROLES_SYNC_AT_LOGIN = True

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
# AUTH_USER_REGISTRATION = True

# The default user self registration role


# When using LDAP Auth, setup the ldap server
# AUTH_LDAP_SERVER = "ldap://ldapserver.new"

# Uncomment to setup OpenID providers example for OpenID authentication
# OPENID_PROVIDERS = [
#    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
# ---------------------------------------------------
# Babel config for translations
# ---------------------------------------------------
# Setup default language
# BABEL_DEFAULT_LOCALE = "en"
# Your application default translation path
# BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
# LANGUAGES = {
#    "en": {"flag": "gb", "name": "English"},
#    "pt": {"flag": "pt", "name": "Portuguese"},
#    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
#    "es": {"flag": "es", "name": "Spanish"},
#    "de": {"flag": "de", "name": "German"},
#    "zh": {"flag": "cn", "name": "Chinese"},
#    "ru": {"flag": "ru", "name": "Russian"},
#    "pl": {"flag": "pl", "name": "Polish"},
# }
# ---------------------------------------------------
# Image and file configuration
# ---------------------------------------------------
# The file upload folder, when using models with files
UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = "/static/uploads/"
# Setup image size default is (300, 200, True)
# IMG_SIZE = (300, 200, True)

# Theme configuration
# these are located on static/appbuilder/css/themes
# you can create your own and easily use them placing them on the same dir structure to override
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
# APP_THEME = "cerulean.css"
# APP_THEME = "amelia.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "readable.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "spacelab.css"
# APP_THEME = "united.css"
# APP_THEME = "yeti.css"

FAB_ROLES = {
    "S3Users": [
        ["S3View", "can_get"],
        ["S3View", "can_list"],
        ["S3UserDBModelView", "can_userinfo"],
        ["ResetMyPasswordView", "can_this_form_post"],
        ["ResetMyPasswordView", "can_this_form_get"],
        ["S3UserDBModelView", "resetmypassword"],
        ["UserInfoEditView", "can_this_form_get"],
        ["S3", "menu_access"],
        ["S3Index", "can_list"]
    ],
    "S3Manager": [
        ["S3View", "can_get"],
        ["S3View", "can_list"],
        ["S3UserDBModelView", "can_userinfo"],
        ["ResetMyPasswordView", "can_this_form_post"],
        ["ResetMyPasswordView", "can_this_form_get"],
        ["S3UserDBModelView", "resetmypassword"],
        ["UserInfoEditView", "can_this_form_get"],
        ["S3", "menu_access"],
        ["S3Index", "can_list"],
        ["Manage", "menu_access"],
        ["S3ManageView", "can_get"],
        ["S3ManageView", "can_list"]
    ]
}

SESSION_REFRESH_EACH_REQUEST = True
