import html

from flask_appbuilder import expose, has_access
from flask_appbuilder.views import BaseView, IndexView
from flask import redirect, session, url_for, current_app
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
        currentBucket = s3.s3WebData.bucketData
        if currentBucket.isAvailable and currentBucket.isAllowed and not currentBucket.hasError and len(currentBucket.data) > 0:
            if not hasattr(s3.s3WebData.objectData,'pageSwitch') or not s3.s3WebData.objectData.pageSwitch:
                s3.resetWebdataPageSetting()
            s3.setWebdataBucketItems("")
        else:
            s3.s3WebData.objectData.isAvailable = currentBucket.isAvailable
            s3.s3WebData.objectData.isAllowed = currentBucket.isAllowed
            s3.s3WebData.objectData.hasError = currentBucket.hasError
            s3.s3WebData.objectData.message = currentBucket.message
            s3.s3WebData.objectData.commonPrefixesList = []
            s3.s3WebData.objectData.data = []
            s3.s3WebData.objectData.page = {}
            s3.s3WebData.objectData.keyCount = 0
            s3.s3WebData.objectData.dataJson = "[]"

        return self.render_template('s3Content.html',
                                    accessData=json.dumps(s3.s3WebData.accessData, default=lambda o: o.__dict__),
                                    bucketData=json.dumps(s3.s3WebData.bucketData, default=lambda o: o.__dict__),
                                    objectData=json.dumps(s3.s3WebData.objectData, default=lambda o: o.__dict__),
                                    objectDataDict=s3.s3WebData.objectData
                                    )

    @expose('/<string:prefixUrl>')
    @has_access
    def get(self, prefixUrl):
        current_app.logger.debug("S3 view with prefix %s called by user %s", prefixUrl, current_user.username)
        s3 = session[current_user.id]
        s3.s3WebData.objectData.currentKey = html.unescape(prefixUrl).replace(" ", "/")
        if not hasattr(s3.s3WebData.objectData,'pageSwitch') or not s3.s3WebData.objectData.pageSwitch:
            s3.resetWebdataPageSetting()
        s3.s3WebData.objectData.pageSwitch = False
        s3.setWebdataBucketItems(s3.s3WebData.objectData.currentKey)
        if s3.s3WebData.objectData.isFile:
            return redirect(s3.getPresignedUrl(s3.s3WebData.objectData.currentKey), code=302)
        session[current_user.id] = s3
        return self.render_template('s3Content.html',
                                    accessData=json.dumps(s3.s3WebData.accessData, default=lambda o: o.__dict__),
                                    bucketData=json.dumps(s3.s3WebData.bucketData, default=lambda o: o.__dict__),
                                    objectData=json.dumps(s3.s3WebData.objectData, default=lambda o: o.__dict__),
                                    objectDataDict=s3.s3WebData.objectData
                                    )
