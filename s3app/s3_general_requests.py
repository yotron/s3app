import sys
import traceback

import boto3, json

from botocore.exceptions import ClientError
from flask import current_app
from abc import abstractmethod
from .s3_general_class import S3Bucket, DataConfig


class S3Request():
    @staticmethod
    def getBoto3Client(s3AccessConfig, currentBucketName=None):
        verifyPath = None
        if s3AccessConfig.s3TrustCaBundle != "":
            verifyPath = s3AccessConfig.setCaBundleFile()
        region_name = None
        if currentBucketName is not None:
            region_name = s3AccessConfig.s3Buckets.data[currentBucketName].region
        client = boto3.client(
            's3',
            aws_access_key_id=s3AccessConfig.s3AccessKey,
            aws_secret_access_key=s3AccessConfig.s3SecretKey,
            region_name=s3AccessConfig.s3DefaultRegion if region_name is None else region_name,
            verify=verifyPath
        )
        if not s3AccessConfig.isAWS:
            client.endpointUrls = s3AccessConfig.s3DefaultEndpointUrl
        current_app.logger.debug("Boto Client defined.")
        return client


class S3RequestResult(DataConfig):
    def __init__(self, s3client, bucketName=None, **kwargs):
        try:
            self.isActive = False
            self.isAvailable = False
            self.isAllowed = False
            self.hasError = True
            response = self.call(s3client, bucketName, **kwargs)
            if self.handleResponseMetadata(response):
                del response['ResponseMetadata']
                if len(response) > 0:
                    self.isActive = True
                    if 's3app_content' in response:
                        self.data = response['s3app_content']
                    else:
                        self.data = response
                   # self.dataJson = json.dumps(self.data)
                    # self.dataJson = json.dumps(self.data, default=lambda o: o.__dict__, indent=4)
        except ClientError as e:
            if self.handleResponseMetadata(e.response) is None:
                self.hasError = False
                self.isAllowed = True
        except Exception as e:
            current_app.logger.error("An error occured: %s", print(traceback.format_exc()))

    def handleResponseMetadata(self, response):
        if 'ResponseMetadata' in response:
            if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
                self.handleStatusCode(response['ResponseMetadata']['HTTPStatusCode'])
                return False
            self.isAvailable = True
            self.isAllowed = True
            self.hasError = False
            return True
        return None

    def handleStatusCode(self, HTTPStatusCode):
        if HTTPStatusCode == 403:
            self.hasError = False
            self.isAvailable = True
            self.isActive = True
        elif HTTPStatusCode in [401]:
            self.hasError = False
        elif 404 <= HTTPStatusCode <= 499:
            self.isAvailable = True
            self.hasError = False

    def withDataToJson(self):
        self.dataJson = json.dumps(self.data, default=lambda o: o.__dict__)
        return self

    @abstractmethod
    def call(self, s3client, bucketName, **kwargs):
        pass


class objectsList(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        retResponse = s3client.list_objects_v2(Bucket=bucketName, **kwargs)
        self.isTruncated = retResponse['IsTruncated']
        self.name = retResponse['Name']
        self.maxKeys = retResponse['MaxKeys']
        self.keyCount = retResponse['KeyCount']
        current_app.logger.debug("Set data for web frontend.")
        retResponse['s3app_content'] = []
        if 'Contents' in retResponse:
            contentList = []
            for keyData in retResponse['Contents']:
                keyData['LastModified'] = keyData['LastModified'].isoformat()
                if not (keyData['Key'][-1] == '/' and keyData['Size'] == 0):
                    contentList.append(keyData)
            retResponse['s3app_content'] = contentList  # with datetime resolving
        self.commonPrefixesList = []
        if 'CommonPrefixes' in retResponse:
            for comPrefData in retResponse['CommonPrefixes']:
                self.commonPrefixesList.append(comPrefData['Prefix'])
        current_app.logger.debug("Web frontend data is: %s", self)
        return retResponse


class bucketListEnriched(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        listBuckets = s3client.list_buckets()
        retResponse = {}
        listBucketsEnriched = {}
        i = 0
        owner = ""
        ownerid = ""
        if "Owner" in listBuckets:
            if "DisplayName" in listBuckets['Owner']:
                owner = listBuckets['Owner']['DisplayName']
            if "ID" in listBuckets['Owner']:
                ownerid = listBuckets['Owner']['ID']
        for bucket in listBuckets['Buckets']:
            bucket['CreationDate'] = bucket['CreationDate'].isoformat()
            location = bucketLocation(s3client, bucketName=bucket['Name'], **kwargs)
            listBucketsEnriched[bucket['Name']] = S3Bucket(bucket['Name'], bucket['CreationDate'],
                                                           location.data, owner, ownerid)
            i += 1

        retResponse['s3app_content'] = listBucketsEnriched
        retResponse['ResponseMetadata'] = listBuckets["ResponseMetadata"]
        return retResponse


class bucketLocation(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        response = s3client.get_bucket_location(Bucket=bucketName)
        retResponse = {}
        retResponse['ResponseMetadata'] = response["ResponseMetadata"]
        if response['LocationConstraint'] is not None:
            retResponse['s3app_content'] = response['LocationConstraint']
        else:
            retResponse['s3app_content'] = kwargs['defaultRegion']
        return retResponse


class bucketWebsite(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_website(Bucket=bucketName)


class bucketLifecycle(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_lifecycle_configuration(Bucket=bucketName)


class bucketNotification(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_notification_configuration(Bucket=bucketName)


class bucketRequestPayment(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_request_payment(Bucket=bucketName)


class bucketTagSet(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_tagging(Bucket=bucketName)


class bucketLogging(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_logging(Bucket=bucketName)


class bucketMetricsConfig(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        response = s3client.list_bucket_metrics_configurations(Bucket=bucketName)
        retResponse = {}
        retResponse['ResponseMetadata'] = response["ResponseMetadata"]
        if "MetricsConfigurationList" in response:
            retResponse['s3app_content'] = response["MetricsConfigurationList"]
        return retResponse


class bucketInventoryConfiguration(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        response = s3client.list_bucket_inventory_configurations(Bucket=bucketName)
        retResponse = {}
        retResponse['ResponseMetadata'] = response["ResponseMetadata"]
        if "InventoryConfigurationList" in response:
            retResponse['s3app_content'] = response["InventoryConfigurationList"]
        return retResponse


class bucketIntelligentTieringConfig(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        response = s3client.list_bucket_intelligent_tiering_configurations(Bucket=bucketName)
        retResponse = {}
        retResponse['ResponseMetadata'] = response["ResponseMetadata"]
        if "IntelligentTieringConfigurationList" in response:
            retResponse['s3app_content'] = response["IntelligentTieringConfigurationList"]
        return retResponse


class bucketAnalyticsConfig(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        response = s3client.list_bucket_analytics_configurations(Bucket=bucketName)
        retResponse = {}
        retResponse['ResponseMetadata'] = response["ResponseMetadata"]
        if "AnalyticsConfigurationList" in response:
            retResponse['s3app_content'] = response["AnalyticsConfigurationList"]
        return retResponse


class bucketPolicy(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        response = s3client.get_bucket_policy(Bucket=bucketName)
        retResponse = {}
        retResponse['ResponseMetadata'] = response["ResponseMetadata"]
        if "Policy" in response:
            retResponse['s3app_content'] = json.loads(response['Policy'])
        return retResponse


class bucketACL(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_acl(Bucket=bucketName)


class bucketCORS(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_cors(Bucket=bucketName)


class bucketEncryption(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_encryption(Bucket=bucketName)


class bucketVersioning(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_versioning(Bucket=bucketName)


class bucketReplication(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        return s3client.get_bucket_replication(Bucket=bucketName)
