import json

from flask_appbuilder import expose, has_access
from flask_appbuilder.views import BaseView
from flask import redirect, session, current_app
from flask_login import current_user
from .s3_manage_class import S3

class S3ManageView(BaseView):
    route_base = '/s3manage'

    @expose('/')
    @has_access
    def list(self):
        current_app.logger.debug("S3 Manage view called by user %s", current_user.username)
        s3Content = session[current_user.id]
        s3 = S3()
        s3.setFromS3Content(s3Content)
        return self.render_template('s3ManageList.html',
                                    accessData=json.dumps(s3.s3WebData.accessData, default=lambda o: o.__dict__),
                                    bucketData=json.dumps(s3.s3WebData.bucketData, default=lambda o: o.__dict__)
                                    )

    @expose('/bucket/<string:bucketName>')
    @has_access
    def get(self, bucketName):
        current_app.logger.debug("S3 Manage view called by user %s", current_user.username)
        s3Session = session[current_user.id]
        s3 = S3()
        s3.setFromS3Content(s3Session)
        if bucketName in s3.s3AccessConfigs[s3.s3WebData.accessData.currentName].s3Buckets.data.keys():
            s3Session.s3WebData.bucketData.currentName = bucketName
        else:
            return redirect("/s3manage")
        s3.bucketConfig.setMetadata(s3Session.s3WebData)
        s3.setBucketSetting()
        return self.render_template('s3ManageGet.html',
                                    accessData=json.dumps(s3.s3WebData.accessData, default=lambda o: o.__dict__),
                                    bucketData=json.dumps(s3.s3WebData.bucketData, default=lambda o: o.__dict__),
                                    bucketConfig=s3.bucketConfig
                                    )

