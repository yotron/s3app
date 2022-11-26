from flask import session, flash
from sqlalchemy import MetaData, create_engine
from .s3_content_class import S3
from .s3_general_class import S3AccessConfig
from .s3_general_requests import *


def userloggedin(app, user):
    current_app.logger.info(user.username + " logged in.")
    s3AccessConfigs = {}
    s3 = S3()
    meta = MetaData(create_engine(app.config['SQLALCHEMY_DATABASE_URI']))
    meta.reflect(views=True)
    accmodel = meta.tables['s3_user_access']
    statement = app.appbuilder.session.query(accmodel).filter_by(user_id=user.id).filter(
        accmodel.c.url != "")
    current_app.logger.debug(str(statement))
    for result in statement.all():
        s3AccessConfig = S3AccessConfig()
        s3AccessConfig.s3AccessName = result['s3_access_name']
        s3AccessConfig.s3AccessKey = result['s3_access_key']
        s3AccessConfig.s3SecretKey = result['s3_secret_key']
        s3AccessConfig.s3Endpoint = result['url']
        s3AccessConfig.s3EndpointName = result['endpoint_name']
        s3AccessConfig.s3EndpointTemplate = result['endpoint_url_template']
        s3AccessConfig.s3ProviderName = result['provider_name']
        s3AccessConfig.s3DefaultRegion = result['s3_default_region']
        s3AccessConfig.s3TrustCaBundle = result['trust_ca_bundle']
        s3Client = S3Request.getBoto3Client(s3AccessConfig, retries=0, readTimeout=1)
        s3AccessConfig.s3Buckets = bucketListEnriched(s3Client, defaultRegion=s3AccessConfig.s3DefaultRegion, accessConfig=s3AccessConfig)
        s3AccessConfigs[s3AccessConfig.s3AccessName] = s3AccessConfig
    if len(s3AccessConfigs.keys()) > 0:
        s3.s3AccessConfigs = s3AccessConfigs
        s3.setWebdataAccessList(s3.s3AccessConfigs)
        s3.setWebdataCurrentAccessName()
        s3.initWebdataBucketListView()
    else:
        s3.s3WebData.accessData.message = "No Access available."
        s3.s3WebData.bucketData.message = "No Access available."
        current_app.logger.info(user.username + " has no access configured.")
    session[user.id] = s3


def userloggedout(app, user):
    flash("You are logged out", 'info')
