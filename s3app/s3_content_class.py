import os
from urllib.parse import urlsplit

import botocore
from botocore.config import Config
import boto3, json, tempfile
from types import SimpleNamespace

from flask import current_app

class S3BucketConfig:
    name = ""
    creationDate = ""
    region = ""

    def __init__(self, name, creationdate, region):
        self.name = name
        self.creationDate = creationdate
        self.region = region


class S3AccessConfig:
    s3AccessName = ""
    s3EndpointName = ""
    s3Endpoint = ""
    s3DefaultEndpointUrl = ""
    s3DefaultRegion = ""
    s3AccessKey = ""
    s3SecretKey = ""
    s3TrustCaBundle = ""
    s3Buckets = {}
    isAWS = False

    def fromJson(self, jsonStr):
        simpleNamespaceObject = json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))
        simpleNamespaceObject.s3Buckets = simpleNamespaceObject.s3Buckets

    def setCaBundleFile(self):
        tmpCaBundle, filename = tempfile.mkstemp()
        os.write(tmpCaBundle, bytes(self.s3TrustCaBundle, 'utf-8'))
        os.close(tmpCaBundle)
        return filename

class Filter:
    s3FilterFolder: bool
    s3FilterFile: bool

    def __init__(self):
        self.s3FilterFolder = True
        self.s3FilterFile = True


class S3WebData:
    accessList = []
    currentBucketList = []
    currentAccessName = ""
    currentBucketName = ""
    currentPrefix = ""
    currentSearchPrefix = ""
    contents = []
    commonPrefixes = []
    isTruncated: bool
    pageAmount: int
    entriesAmount: int
    currentPageNumber: int = 1
    page = {}
    name: str
    maxKeys: int = 20
    keyCount: int

    def setS3ListObjects(self, s3ListObjects):
        current_app.logger.debug("Set data for web frontend.")
        self.contents = []
        if 'Contents' in s3ListObjects:
            contentList = []
            for keyData in s3ListObjects['Contents']:
                if not (keyData['Key'][-1] == '/' and keyData['Size'] == 0):
                    contentList.append(keyData)
            self.contents = json.loads(json.dumps(contentList, default=str))
        self.commonPrefixes = []
        if 'CommonPrefixes' in s3ListObjects:
            for comPrefData in s3ListObjects['CommonPrefixes']:
                self.commonPrefixes.append(comPrefData['Prefix'])
        self.isTruncated = s3ListObjects['IsTruncated']
        self.name = s3ListObjects['Name']
        self.maxKeys = s3ListObjects['MaxKeys']
        self.keyCount = s3ListObjects['KeyCount']
        current_app.logger.debug("Web frontend data is: %s", json.dumps(self.__dict__))

    def setAccessList(self, s3AccessConfigs):
        current_app.logger.debug("Set list of accesses of th user.")
        self.accessList = []
        for accessname in s3AccessConfigs.keys():
            accessItem = {}
            accessItem['id'] = accessname
            accessItem['text'] = accessname
            self.accessList.append(accessItem)
        current_app.logger.debug("Access list is: %s", json.dumps(self.accessList))
        return len(self.accessList)

    def setBucketList(self, s3Buckets):
        current_app.logger.debug("Set list of buckets of the user and access.")
        self.currentBucketList = []
        for bucketname, bucketconfig in s3Buckets.items():
            bucketItem = {}
            bucketItem['id'] = bucketname
            bucketItem['text'] = bucketname
            bucketItem['creationdate'] = bucketconfig.creationDate
            bucketItem['region'] = bucketconfig.region
            self.currentBucketList.append(bucketItem)
        current_app.logger.debug("Current bucket list is: %s", json.dumps(self.currentBucketList))
        return len(self.currentBucketList)


class S3:
    s3AccessConfigs = {}  # name: S3AccessConfig
    s3WebData = {}
    access = None
    pages = {}

    def __init__(self):
        self.s3WebData = S3WebData()


    def initAccesses(self):
        self.s3WebData.currentAccessName = list(self.s3AccessConfigs.keys())[0]
        self.setInitialBucketname()
        current_app.logger.debug("Current access name is %s", self.s3WebData.currentAccessName)

    def setInitialBucketname(self):
        buckKeys = self.s3AccessConfigs[self.s3WebData.currentAccessName].s3Buckets.keys()
        if len(buckKeys) > 0:
            self.s3WebData.currentBucketName = list(buckKeys)[0]
        else:
            self.s3WebData.currentBucketName = None
        current_app.logger.debug("Current bucket name is %s", self.s3WebData.currentBucketName)

    def getBoto3Client(self, region_name=None):
        verifyPath=None
        s3AccessConfig = self.s3AccessConfigs[self.s3WebData.currentAccessName]
        if s3AccessConfig.s3TrustCaBundle != "":
            verifyPath = s3AccessConfig.setCaBundleFile()
        client = {}
        if region_name is None:
            client = boto3.client(
                's3',
                aws_access_key_id=self.s3AccessConfigs[self.s3WebData.currentAccessName].s3AccessKey,
                aws_secret_access_key=self.s3AccessConfigs[self.s3WebData.currentAccessName].s3SecretKey,
                verify=verifyPath
            )
        else:
            client = boto3.client(
                's3',
                aws_access_key_id=self.s3AccessConfigs[self.s3WebData.currentAccessName].s3AccessKey,
                aws_secret_access_key=self.s3AccessConfigs[self.s3WebData.currentAccessName].s3SecretKey,
                region_name=region_name,
                verify=verifyPath
            )
        if not self.s3AccessConfigs[self.s3WebData.currentAccessName].isAWS:
            client.endpointUrls = self.s3AccessConfigs[self.s3WebData.currentAccessName].s3DefaultEndpointUrl
        current_app.logger.debug("Boto Client defined.")
        return client

    def getBuckets(self):
        s3client = self.getBoto3Client()
        return s3client.list_buckets()

    def setBucketItems(self, prefix):
        current_app.logger.debug("Begin to list objects in current bucket.")
        if self.s3WebData.currentPrefix != prefix:
            self.setPages(prefix)
        self.s3WebData.currentPrefix = prefix
        s3client = self.getBoto3Client()
        try:
            if self.s3WebData.currentPageNumber > 1:
                s3listobjects = s3client.list_objects_v2(Bucket=self.s3WebData.currentBucketName, Prefix=prefix,
                                                         Delimiter="/", MaxKeys=self.s3WebData.maxKeys,
                                                         StartAfter=self.pages[self.s3WebData.currentPageNumber])
            else:
                s3listobjects = s3client.list_objects_v2(Bucket=self.s3WebData.currentBucketName, Prefix=prefix,
                                                         Delimiter="/", MaxKeys=self.s3WebData.maxKeys)
        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'InternalError':  # Generic error
                # We grab the message, request ID, and HTTP code to give to customer support
                print('Error Message: {}'.format(err.response['Error']['Message']))
                print('Request ID: {}'.format(err.response['ResponseMetadata']['RequestId']))
                print('Http code: {}'.format(err.response['ResponseMetadata']['HTTPStatusCode']))
            else:
                raise err
        current_app.logger.debug("Objects in listing to visualize: %s", s3listobjects)
        self.s3WebData.setS3ListObjects(s3listobjects)

    def getPresignedUrl(self, key):
        current_app.logger.debug("Define presigned URL for key: %s and bucket: %s", key, self.s3WebData.currentBucketName)
        s3client = self.getBoto3Client(self.s3AccessConfigs[self.s3WebData.currentAccessName].s3Buckets[self.s3WebData.currentBucketName].region)
        preSignedURL = s3client.generate_presigned_url('get_object', Params={'Bucket': self.s3WebData.currentBucketName,
                                                                              'Key': key}, ExpiresIn=3600)
        return preSignedURL

    def setPages(self, prefix):
        current_app.logger.debug("Define pages for prefix: %s", prefix)
        self.s3WebData.currentPageNumber = 1
        self.s3WebData.pageAmount = 0
        self.s3WebData.entriesAmount = 0
        s3client = self.getBoto3Client()
        paginator = s3client.get_paginator('list_objects_v2')
        operation_parameters = {"Bucket": self.s3WebData.currentBucketName, "Prefix": prefix,
                                "Delimiter": "/", "MaxKeys": self.s3WebData.maxKeys}
        current_app.logger.debug("Pagination parameter are: %s", json.dumps(operation_parameters))
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            self.s3WebData.pageAmount = self.s3WebData.pageAmount + 1
            self.s3WebData.entriesAmount = self.s3WebData.entriesAmount + page['KeyCount']
            if "ContinuationToken" in page:
                self.pages[self.s3WebData.pageAmount] = page["ContinuationToken"]
            else:
                self.pages[self.s3WebData.pageAmount] = ""
        current_app.logger.debug("Page setting is: %s", json.dumps(self.pages))
        if self.s3WebData.pageAmount == 1 and prefix != "" and self.s3WebData.currentSearchPrefix == "":  # bug in IONOS Cloud S3?
            self.s3WebData.entriesAmount = self.s3WebData.entriesAmount - 1


