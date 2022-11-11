import html, json

from flask_appbuilder import expose, has_access
from flask_appbuilder.views import BaseView, IndexView
from flask import redirect, session, url_for, request, current_app
from flask_login import current_user
from .s3_general_class import *


class S3IndexView(IndexView):
    @expose('/')
    def index(self):
        if current_user.is_anonymous:
            return redirect(url_for('AuthDBView.login'))
        else:
            return redirect(url_for('S3View.list'))


class S3View(BaseView):
    route_base = '/s3'

    @expose('/')
    @has_access
    def list(self):
        current_app.logger.debug("S3 Index view called by user %s", current_user.username)
        s3 = session[current_user.id]
        requestSearchPrefix = request.args.get('searchPrefix', default=None)
        requestKey = ""
        currentBucket = s3.s3WebData.bucketData
        if currentBucket.isActive and currentBucket.isAvailable and currentBucket.isAllowed and not currentBucket.hasError:
            s3.setBucketItems(requestKey, requestSearchPrefix)
        else:
            s3.s3WebData.objectData.isActive = currentBucket.isActive
            s3.s3WebData.objectData.isAvailable = currentBucket.isAvailable
            s3.s3WebData.objectData.isAllowed = currentBucket.isAllowed
            s3.s3WebData.objectData.hasError = currentBucket.hasError
            s3.s3WebData.objectData.commonPrefixesList = []
            s3.s3WebData.objectData.data = []
            s3.s3WebData.objectData.dataJson = "[]"

        return self.render_template('s3Content.html',
                                    accessData=json.dumps(s3.s3WebData.accessData, default=lambda o: o.__dict__),
                                    bucketData=json.dumps(s3.s3WebData.bucketData, default=lambda o: o.__dict__),
                                    objectData=json.dumps(s3.s3WebData.objectData, default=lambda o: o.__dict__)
                                    )

    @expose('/<string:prefixUrl>')
    @has_access
    def get(self, prefixUrl):
        current_app.logger.debug("S3 view with prefix %s called by user %s", prefixUrl, current_user.username)
        s3 = session[current_user.id]
        requestSearchPrefix = request.args.get('searchPrefix', default=None)
        requestKey = html.unescape(prefixUrl).replace(" ", "/")
        s3.s3WebData.objectData = DataConfig()
        s3.setBucketItems(requestKey, requestSearchPrefix)
        if s3.s3WebData.objectData.isFile:
            return redirect(s3.getPresignedUrl(requestKey), code=302)
        session[current_user.id] = s3
        return self.render_template('s3Content.html',
                                    accessData=json.dumps(s3.s3WebData.accessData, default=lambda o: o.__dict__),
                                    bucketData=json.dumps(s3.s3WebData.bucketData, default=lambda o: o.__dict__),
                                    objectData=json.dumps(s3.s3WebData.objectData, default=lambda o: o.__dict__)
                                    )
