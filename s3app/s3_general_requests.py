import sys
import traceback

import boto3, json
from botocore.config import Config

from botocore.exceptions import ClientError
from flask import current_app
from abc import abstractmethod

from flask_login import current_user

from .s3_general_class import S3Bucket, DataConfig


class S3Request():

    @staticmethod
    def getBoto3Client(s3AccessConfig, currentBucketName=None, retries=3, connectTimeout=2, readTimeout=5):
        verifyPath = False
        if s3AccessConfig.s3TrustCaBundle != "":
            verifyPath = s3AccessConfig.setCaBundleFile()
        region_name = s3AccessConfig.s3DefaultRegion
        endpoint_url = None if s3AccessConfig.s3ProviderName == "AWS" else "https://" + s3AccessConfig.s3Endpoint
        if currentBucketName is not None:
            region_name = s3AccessConfig.s3Buckets.data[currentBucketName].region
            if region_name != s3AccessConfig.s3DefaultRegion and endpoint_url is None and s3AccessConfig.s3EndpointTemplate != "" and s3AccessConfig.s3EndpointTemplate is not None:
                endpoint_url = "https://" + s3AccessConfig.s3EndpointTemplate.replace("<region>", region_name)

        client = boto3.client(
            's3',
            aws_access_key_id=s3AccessConfig.s3AccessKey,
            aws_secret_access_key=s3AccessConfig.s3SecretKey,
            endpoint_url=endpoint_url,
            region_name=s3AccessConfig.s3DefaultRegion if region_name is None else region_name,
            verify=verifyPath,
            config=Config(
                retries={
                    'max_attempts': retries,
                    'mode': 'standard'
                },
                connect_timeout=connectTimeout,
                read_timeout=readTimeout
            )
        )
        current_app.logger.debug("Boto Client defined.")
        return client


class S3RequestResult(DataConfig):
    def __init__(self, s3client, bucketName=None, **kwargs):
        try:
            self.message = ""
            self.hasError = True
            self.isAllowed = False
            self.isAvailable = False
            response = self.call(s3client, bucketName, **kwargs)
            if self.handleResponseMetadata(response):
                del response['ResponseMetadata']
                if len(response) > 0:
                    # self.isAvailable = True
                    if 's3app_content' in response:
                        self.data = response['s3app_content']
                    else:
                        self.data = response
                    if len(self.data) == 0:
                        self.message = "No data available."
                else:
                    self.isAvailable = False
                    self.message = "The function is not active for this Bucket ..."
        except ClientError as e:
            if self.handleResponseMetadata(e.response) is None:
                self.hasError = False
                self.isAllowed = True
        except Exception as e:
            self.message = "No content due to an error."
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
        if HTTPStatusCode == 403:  # forbidden
            self.hasError = False
            self.isAvailable = True
            self.message = "You are not allowed ..."
        elif HTTPStatusCode == 401:  # unauthorized
            self.hasError = False
            self.message = "You are not authorized ..."
        elif HTTPStatusCode == 404:  # not found
            self.hasError = False
            self.message = "The function is not active for this Bucket ..."
        elif HTTPStatusCode in [405, 501]:  # method not allowed 501 for Cloudian, 405 Ceph
            self.hasError = False
            self.message = "This function is not available for that S3-provider ..."
        else:
            self.message = "An internal error occured ..."

    def withDataToJson(self):
        self.dataJson = json.dumps(self.data, default=lambda o: o.__dict__)
        return self

    @abstractmethod
    def call(self, s3client, bucketName, **kwargs):
        pass


class objectsList(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        retResponse = s3client.list_objects_v2(Bucket=bucketName, **kwargs)
        self.name = retResponse['Name']
        self.isTruncated = retResponse['IsTruncated']
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
        self.message = "No data" if len(self.commonPrefixesList) + len(retResponse['s3app_content']) == 0 else None
        current_app.logger.debug("Web frontend data is: %s", self)
        return retResponse


class pageList(S3RequestResult):
    def call(self, s3client, bucketName, **kwargs):
        self.currentKey = kwargs['currentKey']
        self.currentSearchPrefix = kwargs['currentSearchPrefix']
        self.maxKeys = kwargs['maxKeys']
        prefix = self.currentKey + self.currentSearchPrefix
        current_app.logger.debug("Define pages for prefix: %s", prefix)
        self.currentPageNumber = 1
        self.pageAmount = 0
        self.entriesAmount = 0
        paginator = s3client.get_paginator('list_objects_v2')
        operation_parameters = {"Bucket": bucketName, "Prefix": prefix,
                                "Delimiter": "/", "MaxKeys": self.maxKeys}
        current_app.logger.debug("Pagination parameter are: %s", json.dumps(operation_parameters))
        page_iterator = paginator.paginate(**operation_parameters)
        s3app_content = {}
        retResponse = {}
        for page in page_iterator:
            retResponse['ResponseMetadata'] = page['ResponseMetadata']
            self.pageAmount = self.pageAmount + 1
            self.entriesAmount = self.entriesAmount + page['KeyCount']
            if "ContinuationToken" in page:
                s3app_content[self.pageAmount] = page["ContinuationToken"]
            else:
                s3app_content[self.pageAmount] = ""
        retResponse['s3app_content'] = s3app_content
        current_app.logger.debug("Page setting is: %s", json.dumps(self.data))
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
            if location.isAvailable and not location.hasError and location.isAllowed:
                listBucketsEnriched[bucket['Name']] = S3Bucket(bucket['Name'], bucket['CreationDate'],
                                                               location.data, owner, ownerid)
                i += 1
            else:
                current_app.logger.info("User with id {} has not full access to bucket {}. Cant get location. Ignore Bucket.".format(current_user.id, bucket['Name']))
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
