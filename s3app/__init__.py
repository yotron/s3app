import argparse
import os, logging
import sys
from os.path import join, dirname
from pathlib import Path
from waitress import serve
import yaml
from dotenv import dotenv_values
import flask_login
from flask import Flask, flash
from flask_appbuilder import SQLA, AppBuilder
from flask_session import Session
from flask_appbuilder.menu import Menu
from werkzeug.exceptions import InternalServerError
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import MetaData, create_engine

from s3app.s3_server import S3ServerAroParser
from s3app.s3_sec import S3SecurityManager
from s3app.s3_base import base
from s3app.s3_error import logout_user, handle_500
from s3app.s3_sec_models import Sqls
from s3app.s3_sec_views import S3AccessModelView, S3GroupModelView, S3EndpointModelView
from s3app.s3_content_view import S3View, S3IndexView
from s3app.s3_sec_signals import userloggedin, userloggedout
from s3app.s3_content_rest import Access, Bucket, Page, MaxKeys
from flask_restful import Api

basedir = os.path.abspath(os.path.dirname(__file__))
# init Flask
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

app.config.from_pyfile(basedir + "/config.py")
log_level = logging.INFO
if os.getenv("S3APP_CONF_FILE") is not None:
    dotenv_path = os.getenv("S3APP_CONF_FILE")
    if not os.path.isfile(dotenv_path):
        print("ERROR: Cannot find .env File in {path}. Cannot start.".format(path=dotenv_path))
        sys.exit(1)
    app.config.update(dotenv_values(dotenv_path))
    app.config['SECRET_KEY'] = app.config['S3APP_SECRET_KEY'] if 'S3APP_SECRET_KEY' in app.config else app.config[
        'SECRET_KEY']
    log_level = logging.DEBUG if app.config['S3APP_LOG_LEVEL'].upper() == "DEBUG" else log_level
    log_level = logging.WARNING if app.config['S3APP_LOG_LEVEL'].upper() == "WARNING" else log_level
    log_level = logging.FATAL if app.config['S3APP_LOG_LEVEL'].upper() == "FATAL" else log_level
    log_level = logging.INFO if app.config['S3APP_LOG_LEVEL'].upper() == "INFO" else log_level
    log_level = logging.ERROR if app.config['S3APP_LOG_LEVEL'].upper() == "ERROR" else log_level

logging.getLogger().setLevel(log_level)
log_format = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"

if 'S3APP_LOG_FILE' in app.config:
    try:
        with open(app.config['S3APP_LOG_FILE'], 'w') as f:
            f.write('S3App Logfile')
        logging.basicConfig(filename=app.config['S3APP_LOG_FILE'], format=log_format)
    except FileNotFoundError as e:
        print("Cannot create log file. Stop processing. Error: {error}".format(error=e))
        sys.exit(1)
else:
    logging.basicConfig(format=log_format)

app.logger.info("The APP is running in {LOGLEVEL} mode.".format(LOGLEVEL=logging.getLevelName(log_level)))

if "S3APP_APP_NAME" in app.config:
    app.config["APP_NAME"] = app.config["S3APP_APP_NAME"]
app.logger.info("Starting S3App with name {APP_NAME}.".format(APP_NAME=app.config["APP_NAME"]))

if "S3APP_APP_ICON" in app.config:
    app.config["APP_ICON"] = app.config["S3APP_APP_ICON"]
app.logger.info("Adding {APP_ICON} as App icon.".format(APP_ICON=app.config["APP_ICON"]))

# Init Database
server_session = Session(app)
server_session.app.session_interface.db.create_all()
db = SQLA(app)

# Register Flask Blueprints
app.register_blueprint(base)

# Register Flask error handler
app.register_error_handler(InternalServerError, handle_500)
app.register_error_handler(401, logout_user)

# Init Appbuilder Authentication and Authorization
appbuilder = AppBuilder(app, db.session, base_template='appbuilder/baselayout.html',
                        security_manager_class=S3SecurityManager, indexview=S3View, menu=Menu(reverse=False))
appbuilder.add_view(S3AccessModelView, "List S3Access", category="Security")
appbuilder.add_view(S3GroupModelView, "List Groups", category="Security")
appbuilder.add_view(S3EndpointModelView, "List S3Endpoints", category="Security")
appbuilder.add_view_no_menu(S3View())
appbuilder.add_view_no_menu(S3IndexView())

# init Flask RESTApi
api = Api(app)
api.add_resource(Access, '/s3config/access/<string:accessname>')
api.add_resource(Bucket, '/s3config/access/<string:accessname2>/bucket/<string:bucketname>')
api.add_resource(MaxKeys, '/s3config/maxkeys/<string:maxkeys>')
api.add_resource(Page, '/s3config/page/<string:page>')

admin = appbuilder.sm.find_user(username="admin")

# Setup default Database
if admin == None:
    role_admin = appbuilder.sm.find_role(
        appbuilder.sm.auth_role_admin
    )
    admin = appbuilder.sm.add_user(
        username="admin",
        first_name="admin",
        last_name="admin",
        email="admin@example.com",
        role=role_admin,
        password="admin"
    )
    db.session.add(admin)
    db.session.commit()

# Init signal triggers
flask_login.user_logged_in.connect(userloggedin)
flask_login.user_logged_out.connect(userloggedout)

# Init access views

sqls = Sqls(db)

sqls.setDefaultEndpoints()
if os.environ.get('WITH_TESTDATA') == "true":
    sqls.setTestData(appbuilder)

meta = MetaData(create_engine(app.config['SQLALCHEMY_DATABASE_URI']))
meta.reflect(views=True)
if not 's3_user_access' in meta.tables:
    sqls.setUserAccessView()


def run():
    argParser = S3ServerAroParser()
    args = argParser.parser.parse_args()
    serve(app, **argParser.getKw(args))
