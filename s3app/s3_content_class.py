import html
import os
from copy import deepcopy
from urllib.parse import urlsplit

import botocore
from botocore.config import Config
import boto3, json, tempfile
from types import SimpleNamespace

from flask import current_app
from flask_login import current_user
from .s3_general_requests import *
from .s3_general_class import DataConfig


class Filter:
    s3FilterFolder: bool
    s3FilterFile: bool

    def __init__(self):
        self.s3FilterFolder = True
        self.s3FilterFile = True

class S3WebData:
    accessData = DataConfig()
    bucketData = DataConfig()
    objectData = DataConfig()

class S3:
    s3AccessConfigs = {}  # name: S3AccessConfig
    s3WebData = {}
    access = None
    pages = {}

    def __init__(self):
        self.s3WebData = S3WebData()

    def setWebdataCurrentAccessName(self):
        self.s3WebData.accessData.currentName = list(self.s3AccessConfigs.keys())[0]
        current_app.logger.debug("Current access name is %s", self.s3WebData.accessData.currentName)

    def initWebdataBucketObjectsView(self):
        self.s3WebData.objectData = DataConfig()
        self.s3WebData.objectData.currentSearchPrefix = ""
        self.s3WebData.objectData.currentKey = ""
        self.s3WebData.objectData.maxKeys = 20
        listBucketsOfCurrentAccess = self.s3AccessConfigs[self.s3WebData.accessData.currentName].s3Buckets
        self.s3WebData.bucketData = deepcopy(listBucketsOfCurrentAccess)
        self.s3WebData.bucketData.data = []
        self.s3WebData.bucketData.dataJson = ""
        if listBucketsOfCurrentAccess.isActive and listBucketsOfCurrentAccess.isAvailable and listBucketsOfCurrentAccess.isAllowed and not listBucketsOfCurrentAccess.hasError:
            self.setWebdataBucketList(listBucketsOfCurrentAccess)
            self.s3WebData.bucketData.currentName = list(listBucketsOfCurrentAccess.data.keys())[0]
            self.setPages("")
            current_app.logger.debug("Current bucket name is %s", self.s3WebData.bucketData.currentName)

    def setWebdataCurrentBucketList(self):
        buckKeys = self.s3AccessConfigs[self.s3WebData.accessData.currentName].s3Buckets.data.keys()
        self.s3WebData.bucketData.currentName = list(buckKeys)[0]
        current_app.logger.debug("Current bucket name is %s", self.s3WebData.bucketData.currentName)

    def setBucketItems(self, requestKey, requestSearchPrefix):
        current_app.logger.debug("Begin to list objects in current bucket.")

        completeSearchKey = requestKey
        requestSearchPrefixCompare = requestSearchPrefix
        if requestSearchPrefix is not None:
            completeSearchKey = requestKey + requestSearchPrefix
        else:
            requestSearchPrefixCompare = ""

        if requestKey != self.s3WebData.objectData.currentKey or requestSearchPrefixCompare != self.s3WebData.objectData.currentSearchPrefix:
            self.s3WebData.objectData.currentKey = requestKey
            self.s3WebData.objectData.currentKeyResolvedList = requestKey.split('/')
            self.setPages(completeSearchKey)

# bug in IONOS Cloud S3?       if self.s3WebData.objectData.pageAmount == 1 and completeSearchKey != "" and requestSearchPrefix == "":
#            self.s3WebData.objectData.entriesAmount = self.s3WebData.objectData.entriesAmount - 1

        if requestSearchPrefix is not None:
            self.s3WebData.objectData.currentSearchPrefix = requestSearchPrefix

        s3Client = S3Request.getBoto3Client(s3AccessConfig=self.s3AccessConfigs[self.s3WebData.accessData.currentName])
        if self.s3WebData.objectData.currentPageNumber > 1:
            s3listobjects = objectsList(s3Client, bucketName=self.s3WebData.bucketData.currentName, Prefix=completeSearchKey,
                                                     Delimiter="/", MaxKeys=self.s3WebData.objectData.maxKeys,
                                                     ContinuationToken=self.pages[self.s3WebData.objectData.currentPageNumber])
        else:
            s3listobjects = objectsList(s3Client, bucketName=self.s3WebData.bucketData.currentName, Prefix=completeSearchKey,
                                                     Delimiter="/", MaxKeys=self.s3WebData.objectData.maxKeys)

        current_app.logger.debug("Objects in listing to visualize: %s", s3listobjects)
        # self.setWebdataObjectList(s3listobjects)
        # content = self.s3WebData.objectData.data
        s3listobjects.isFile = False
        if len(s3listobjects.data) == 1 and s3listobjects.data[0]['Key'] == completeSearchKey and s3listobjects.data[0]['Size'] >= 0:
            s3listobjects.isFile = True
        self.s3WebData.objectData.__dict__.update(s3listobjects.__dict__)

    def getPresignedUrl(self, key):
        current_app.logger.debug("Define presigned URL for key: %s and bucket: %s", key,
                                 self.s3WebData.bucketData.currentName)
        s3Client = S3Request.getBoto3Client(self.s3AccessConfigs[self.s3WebData.accessData.currentName],
                                            self.s3WebData.bucketData.currentName)
        preSignedURL = s3Client.generate_presigned_url('get_object', Params={'Bucket': self.s3WebData.bucketData.currentName,
                                                                             'Key': key}, ExpiresIn=3600)
        return preSignedURL

    def setPages(self, prefix):
        current_app.logger.debug("Define pages for prefix: %s", prefix)
        self.s3WebData.objectData.currentPageNumber = 1
        self.s3WebData.objectData.pageAmount = 0
        self.s3WebData.objectData.entriesAmount = 0
        s3Client = S3Request.getBoto3Client(s3AccessConfig=self.s3AccessConfigs[self.s3WebData.accessData.currentName])
        paginator = s3Client.get_paginator('list_objects_v2')
        operation_parameters = {"Bucket": self.s3WebData.bucketData.currentName, "Prefix": prefix,
                                "Delimiter": "/", "MaxKeys": self.s3WebData.objectData.maxKeys}
        current_app.logger.debug("Pagination parameter are: %s", json.dumps(operation_parameters))
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            self.s3WebData.objectData.pageAmount = self.s3WebData.objectData.pageAmount + 1
            self.s3WebData.objectData.entriesAmount = self.s3WebData.objectData.entriesAmount + page['KeyCount']
            if "ContinuationToken" in page:
                self.pages[self.s3WebData.objectData.pageAmount] = page["ContinuationToken"]
            else:
                self.pages[self.s3WebData.objectData.pageAmount] = ""
        current_app.logger.debug("Page setting is: %s", json.dumps(self.pages))

    def setWebdataAccessList(self, s3AccessConfigs):
        current_app.logger.debug("Set list of accesses of th user.")
        self.s3WebData.accessData.data = []
        for accessname in s3AccessConfigs.keys():
            accessItem = {}
            accessItem['id'] = accessname
            accessItem['text'] = accessname
            self.s3WebData.accessData.data.append(accessItem)
        current_app.logger.debug("Access list is: %s", json.dumps(self.s3WebData.accessData.data))
        return len(self.s3WebData.accessData.data)

    def setWebdataBucketList(self, dataConfigCurrentBucket):
        current_app.logger.debug("Set list of buckets of the user and access.")
        isBucketManager = False
        for role in current_user.roles:
            if "S3Manager" == role.name:
                isBucketManager = True
        for bucketname, bucketconfig in dataConfigCurrentBucket.data.items():
            bucketItem = {}
            bucketItem['id'] = bucketname
            bucketItem['text'] = bucketname
            bucketItem['creationdate'] = bucketconfig.creationDate
            bucketItem['region'] = bucketconfig.region
            if isBucketManager:
                bucketItem['owner'] = bucketconfig.owner
                bucketItem['ownerid'] = bucketconfig.ownerId
            self.s3WebData.bucketData.data.append(bucketItem)
        current_app.logger.debug("Current bucket list is: %s", self.s3WebData.bucketData.data)
        return len(self.s3WebData.bucketData.data)

    def setWebdataObjectList(self, s3ListObjects):
        current_app.logger.debug("Set data for web frontend.")
        self.s3WebData.objectData = s3ListObjects
        if 'Contents' in s3ListObjects.data:
            contentList = []
            for keyData in s3ListObjects.data['Contents']:
                if not (keyData['Key'][-1] == '/' and keyData['Size'] == 0):
                    contentList.append(keyData)
            self.s3WebData.objectData.data = contentList
        self.s3WebData.objectData.commonPrefixesList = []
        if 'CommonPrefixes' in s3ListObjects.data:
            for comPrefData in s3ListObjects.data['CommonPrefixes']:
                self.s3WebData.objectData.commonPrefixesList.append(comPrefData['Prefix'])
        current_app.logger.debug("Web frontend data is: %s", self.s3WebData.objectData)
