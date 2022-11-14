import datetime
import json
import os
import tempfile
from types import SimpleNamespace


class S3Bucket:
    name = ""
    creationDate = ""
    region = ""
    owner = ""
    ownerId = ""

    def __init__(self, name, creationdate, region, owner, ownerId):
        self.name = name
        self.creationDate = creationdate
        self.region = region
        self.owner = owner
        self.ownerId = ownerId


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


class DataConfig:
    data = []
    dataJson: str
    currentName: str
    placeholder: str
    isAvailable: bool
    isAllowed: bool
    hasError: bool
    message: str
    commonPrefixesList = []
    currentKey: str
    currentKeyResolvedList = []
    currentSearchPrefix: str
    isFile: bool
    isTruncated: bool
    pageAmount: int
    entriesAmount: int
    currentPageNumber: int = 1
    page = {}
    name: str
    maxKeys: int
    keyCount: int

    def __init__(self):
        self.isAvailable = False
        self.isAllowed = False
        self.hasError = True

