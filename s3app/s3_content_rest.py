from flask import session, current_app
from flask_login import current_user
from flask_restful import Resource, abort


class Access(Resource):
    def post(self, accessname):
        if current_user.is_authenticated:
            current_app.logger.debug("Change access to %s for user %s", accessname, current_user.username)
            s3 = session[current_user.id]
            s3.s3WebData.currentAccessName = accessname
            s3.s3WebData.currentSearchPrefix = ""
            s3.s3WebData.setBucketList(s3.s3AccessConfigs[s3.s3WebData.currentAccessName].s3Buckets)
            s3.setInitialBucketname()
            if s3.s3WebData.currentBucketName is not None:
                s3.setPages("")
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
            s3.s3WebData.currentAccessName = accessname2
            s3.s3WebData.currentBucketName = bucketname
            s3.s3WebData.currentSearchPrefix = ""
            s3.setPages("")
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
            s3.s3WebData.maxKeys = int(maxkeys)
            session[current_user.id] = s3
            s3.setPages("")
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST MaxKeys")
            abort(401)


class Page(Resource):
    def post(self, page):
        if current_user.is_authenticated:
            current_app.logger.debug("Change Page to %s for user %s", page, current_user.username)
            s3 = session[current_user.id]
            s3.s3WebData.currentPageNumber = int(page)
            session[current_user.id] = s3
            return "", 200
        else:
            current_app.logger.info("Anonymous access to POST Page")
            return '', 401

