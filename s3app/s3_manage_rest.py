import json

from flask import session, current_app
from flask_login import current_user
from flask_restful import Resource, abort
from .s3_manage_class import S3

class Metrics(Resource):
    def get(self, bucketname):
        if current_user.is_authenticated:
            current_app.logger.debug("Set Metrics from %s inittiated by user %s", bucketname, current_user.username)
            s3Session = session[current_user.id]
            s3 = S3()
            s3.s3WebData.bucketData.currentName = bucketname
            s3.setFromS3Content(s3Session)
            s3.setBucketMetrics()
            response = current_app.response_class(
                response=json.dumps(s3.bucketConfig.metrics, default=lambda o: o.__dict__),
                status=200,
                mimetype='application/json')
            return response
        else:
            current_app.logger.info("Anonymous access to GET Access")
            abort(401)

