from flask_appbuilder.security.sqla.manager import SecurityManager
from .s3_sec_models import S3User
from .s3_sec_views import S3UserDBModelView


class S3SecurityManager(SecurityManager):
    user_model = S3User
    userdbmodelview = S3UserDBModelView
