import flask
import flask_login
from flask import redirect, url_for, session, current_app, Blueprint
from flask_login import current_user
from sqlalchemy import MetaData, create_engine

base = Blueprint("base", __name__)


@base.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'), 308)


@base.route('/logout/', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        current_app.logger.info(current_user.username + " logged out.")
        session[current_user.id] = None
        flask_login.logout_user()
    return flask.redirect("/login/")

@base.route('/s3app/liveness', methods=['GET'])
def liveness():
    return '', 200

@base.route('/s3app/readiness', methods=['GET'])
def readiness():
    meta = MetaData(create_engine(current_app.config['SQLALCHEMY_DATABASE_URI']))
    meta.reflect(views=True)
    if 's3_user_access' in meta.tables:
        return '', 200
    return '', 503
