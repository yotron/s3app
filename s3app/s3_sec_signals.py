import boto3
from flask import session, flash, current_app
from sqlalchemy import MetaData, create_engine
from .s3_content_class import S3, S3AccessConfig, S3BucketConfig

def userloggedin(app, user):
    current_app.logger.info(user.username + " logged in.")
    meta = MetaData(create_engine(app.config['SQLALCHEMY_DATABASE_URI']))
    meta.reflect(views=True)
    accmodel = meta.tables['s3_user_access']
    s3AccessConfigs = {}
    s3 = S3()
    for result in app.appbuilder.session.query(accmodel).filter_by(user_id=user.id).all():
        s3AccessConfig = S3AccessConfig()
        s3AccessConfig.s3AccessName = result['s3_access_name']
        s3AccessConfig.s3AccessKey = result['s3_access_key']
        s3AccessConfig.s3SecretKey = result['s3_secret_key']
        s3AccessConfig.s3DefaultEndpointUrl = "https://" + result['url']
        s3AccessConfig.s3DefaultRegion = result['s3_default_region']
        s3AccessConfig.s3Endpoint = result['url']
        s3AccessConfig.s3EndpointName = result['name']
        s3AccessConfig.s3TrustCaBundle = result['trust_ca_bundle']
        verifyPath = None
        if result['url'].endswith("amazonaws.com"):
            s3AccessConfig.isAWS = True
        if s3AccessConfig.s3TrustCaBundle != "":
            verifyPath = s3AccessConfig.setCaBundleFile()
        s3conn = boto3.client('s3',
                              aws_access_key_id=s3AccessConfig.s3AccessKey,
                              aws_secret_access_key=s3AccessConfig.s3SecretKey,
                              endpoint_url=s3AccessConfig.s3DefaultEndpointUrl,
                              region_name=s3AccessConfig.s3DefaultRegion,
                              verify=verifyPath
                              )
        response = s3conn.list_buckets()
        buckets = {}
        for bucket in response['Buckets']:
            bucketLocation = s3conn.get_bucket_location(Bucket=bucket['Name'])
            bucketLocName = ""
            if bucketLocation['LocationConstraint'] is not None:
                bucketLocName = bucketLocation['LocationConstraint']
            buckets[bucket['Name']] = S3BucketConfig(bucket['Name'], bucket['CreationDate'].utcnow().isoformat(),
                                                     bucketLocName)
        s3AccessConfig.s3Buckets = buckets
        s3AccessConfigs[s3AccessConfig.s3AccessName] = s3AccessConfig
    if len(s3AccessConfigs.keys()) > 0:
        s3.s3AccessConfigs = s3AccessConfigs
        s3.initAccesses()
        s3.s3WebData.setBucketList(s3.s3AccessConfigs[s3.s3WebData.currentAccessName].s3Buckets)
        s3.s3WebData.setAccessList(s3.s3AccessConfigs)
        if s3.s3WebData.currentBucketName != "":
            s3.setPages("")
    else:
        current_app.logger.info(user.username + " das no access configured.")
    session[user.id] = s3


def userloggedout(app, user):
    flash("You are logged out", 'info')
