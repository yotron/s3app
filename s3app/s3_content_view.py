import html, json

from flask_appbuilder import expose, has_access
from flask_appbuilder.views import BaseView, IndexView
from flask import redirect, session, url_for, request, current_app
from flask_login import current_user


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
        s3.s3WebData.currentSearchPrefix = request.args.get('searchPrefix', default="")
        if s3.s3WebData.currentBucketName != "":
            s3.setBucketItems(s3.s3WebData.currentSearchPrefix)
        else:
            s3.s3WebData.commonPrefixes = []
            s3.s3WebData.contents = []
            s3.s3WebData.pageAmount = 0

        return self.render_template('s3Content.html',
                                    s3WebData=json.dumps(s3.s3WebData, default=lambda o: o.__dict__),
                                    accessList=json.dumps(s3.s3WebData.accessList, default=lambda o: o.__dict__),
                                    currentBucketList=json.dumps(s3.s3WebData.currentBucketList,
                                                                 default=lambda o: o.__dict__),
                                    contents=json.dumps(s3.s3WebData.contents, default=lambda o: o.__dict__),
                                    commonPrefixes=json.dumps(s3.s3WebData.commonPrefixes,
                                                              default=lambda o: o.__dict__),
                                    currentPrefixesList=[]
                                    )

    @expose('/<string:prefixUrl>')
    @has_access
    def get(self, prefixUrl):
        current_app.logger.debug("S3 view with prefix %s called by user %s", prefixUrl, current_user.username)
        s3 = session[current_user.id]
        s3.s3WebData.currentSearchPrefix = request.args.get('searchPrefix', default="")
        prefix = html.unescape(prefixUrl).replace(" ", "/") + s3.s3WebData.currentSearchPrefix
        s3.setBucketItems(prefix)
        content = s3.s3WebData.contents
        if len(content) == 1 and content[0]['Key'] == prefix and content[0]['Size'] >= 0:
            return redirect(s3.getPresignedUrl(prefix), code=302)
        return self.render_template('s3Content.html',
                                    s3WebData=json.dumps(s3.s3WebData, default=lambda o: o.__dict__),
                                    accessList=json.dumps(s3.s3WebData.accessList, default=lambda o: o.__dict__),
                                    currentBucketList=json.dumps(s3.s3WebData.currentBucketList,
                                                                 default=lambda o: o.__dict__),
                                    contents=json.dumps(s3.s3WebData.contents, default=lambda o: o.__dict__),
                                    commonPrefixes=json.dumps(s3.s3WebData.commonPrefixes,
                                                              default=lambda o: o.__dict__),
                                    currentPrefixesList=s3.s3WebData.currentPrefix.split('/')
                                    )

