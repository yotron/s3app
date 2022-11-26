from flask import session, current_app
from flask_login import current_user
from flask_restful import Resource, abort


class Access(Resource):
    def post(self, accessname):
        if current_user.is_authenticated:
            current_app.logger.debug("Change access to %s for user %s", accessname, current_user.username)
            s3 = session[current_user.id]
            if not s3.s3WebData.accessData.currentName in s3.s3AccessConfigs:
                abort(404)
            s3.s3WebData.accessData.currentName = accessname
            s3.initWebdataBucketListView()
            session[current_user.id] = s3
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST Access")
            abort(401)


class Bucket(Resource):
    def post(self, accessname2, bucketname):
        if current_user.is_authenticated:
            current_app.logger.debug("Change bucket to %s for user %s", bucketname, current_user.username)
            s3 = session[current_user.id]
            s3.s3WebData.accessData.currentName = accessname2
            s3.s3WebData.bucketData.currentName = bucketname
            s3.s3WebData.objectData.currentSearchPrefix = ""
            s3.s3WebData.objectData.currentKey = ""
            s3.s3WebData.objectData.currentKeyResolvedList = []
            s3.resetWebdataPageSetting()
            session[current_user.id] = s3
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST Bucket")
            abort(401)


class MaxKeys(Resource):
    def post(self, maxkeys):
        if current_user.is_authenticated:
            current_app.logger.debug("Change MaxKeys to %s for user %s", maxkeys, current_user.username)
            s3 = session[current_user.id]
            s3.s3WebData.objectData.maxKeys = int(maxkeys)
            s3.resetWebdataPageSetting()
            session[current_user.id] = s3
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST MaxKeys")
            abort(401)


class Page(Resource):
    def post(self, page):
        if current_user.is_authenticated:
            current_app.logger.debug("Change Page to %s for user %s", page, current_user.username)
            s3 = session[current_user.id]
            s3.s3WebData.objectData.currentPageNumber = int(page)
            s3.s3WebData.objectData.pageSwitch = True
            session[current_user.id] = s3
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST Page")
            return '', 401


class SearchPrefix(Resource):
    def post(self, searchprefix):
        if current_user.is_authenticated:
            current_app.logger.debug("Search prefix to %s for user %s", searchprefix, current_user.username)
            s3 = session[current_user.id]
            s3.s3WebData.objectData.currentSearchPrefix = searchprefix
            s3.resetWebdataPageSetting()
            session[current_user.id] = s3
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST Page")
            return '', 401