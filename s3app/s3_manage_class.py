from datetime import datetime
from .s3_general_requests import *
from .s3_general_class import DataConfig

class Metrics:
    bucketAmount = 0
    bucketSize = 0
    bucketSizeHuman = ""

    def __init__(self):
        self.bucketAmount = 0
        self.bucketSize = 0
        self.bucketSizeHuman = ""

class BucketConfig:
    bucketName = ""
    bucketCreationDate = ""
    bucketOwnerId = ""
    bucketOwnerName = ""
    metrics = Metrics()
    bucketWebsite = None
    bucketLifecycle = None
    bucketNotification = None
    bucketRequestPayment = None
    bucketTagSet = None
    bucketLogging = None
    bucketMetricsConfig = None
    bucketInventoryConfiguration = None
    bucketIntelligentTieringConfig = None
    bucketAnalyticsConfig = None
    bucketPolicy = None
    bucketACL = None
    bucketCORS = None
    bucketEncryption = None
    bucketVersioning = None
    bucketReplication = None


    def __init__(self):
        self.bucketName = ""
        self.bucketCreationDate = ""
        self.bucketOwnerId = ""
        self.bucketOwnerName = ""
        self.metrics = Metrics()
        self.bucketWebsite = None
        self.bucketLifecycle = None
        self.bucketRequestPayment = None
        self.bucketTagSet = None
        self.bucketLogging = None
        self.bucketMetricsConfig = None
        self.bucketInventoryConfiguration = None
        self.bucketIntelligentTieringConfig = None
        self.bucketAnalyticsConfig = None
        self.bucketPolicy = None
        self.bucketACL = None
        self.bucketCORS = None
        self.bucketEncryption = None
        self.bucketVersioning = None
        self.bucketReplication = None

    def addAmount(self, amount):
        self.metrics.bucketAmount = self.metrics.bucketAmount + amount

    def addSize(self, size):
        self.metrics.bucketSize = self.metrics.bucketSize + size

    def resetMetrics(self):
        self.metrics.bucketAmount = 0
        self.metrics.bucketSize = 0

    def setSizeHumanReadable(self):
        self.metrics.bucketSizeHuman = statics.sizeof_fmt(self.metrics.bucketSize)

    def setMetadata(self, s3WebData):
        def condition(bucket):
            return bucket['text'] == s3WebData.bucketData.currentName

        bucket = next(filter(condition, s3WebData.bucketData.data), None)
        if bucket is not None:
            self.bucketName = bucket['text']
            self.bucketCreationDate = datetime.fromisoformat(bucket['creationdate']).strftime(
                '%a, %d %b %Y %H:%M:%S %Z')
            self.bucketOwnerId = bucket['ownerid']
            self.bucketOwnerName = bucket['owner']



class S3WebData:
    accessData = DataConfig()
    bucketData = DataConfig()


class S3:
    s3WebData = S3WebData()
    s3AccessConfigs = {}  # name: S3AccessConfig
    bucketConfig = BucketConfig()


    def setFromS3Content(self, s3SessionData):
        self.s3AccessConfigs = s3SessionData.s3AccessConfigs
        self.s3WebData.accessData = s3SessionData.s3WebData.accessData
        self.s3WebData.bucketData = s3SessionData.s3WebData.bucketData


    def setBucketMetrics(self):
        current_app.logger.debug("Begin to set metrics in current bucket.")
        s3client = S3Request.getBoto3Client(s3AccessConfig=self.s3AccessConfigs[self.s3WebData.accessData.currentName], currentBucketName=self.s3WebData.bucketData.currentName)
        paginator = s3client.get_paginator('list_objects_v2')
        operation_parameters = {"Bucket": self.s3WebData.bucketData.currentName, "MaxKeys": 100}
        current_app.logger.debug("Metrics pagination parameter are: %s", json.dumps(operation_parameters))
        page_iterator = paginator.paginate(**operation_parameters)
        self.bucketConfig.resetMetrics()
        for page in page_iterator:
            self.bucketConfig.addAmount(page['KeyCount'])
            self.bucketConfig.addSize(self.getSize(page['Contents']) if 'Contents' in page else 0)
        self.bucketConfig.setSizeHumanReadable()
        current_app.logger.debug("New Amount %s, New Size %s",
                                 self.bucketConfig.metrics.bucketAmount,
                                 self.bucketConfig.metrics.bucketSize)

    def getSize(self, contents):
        size = 0
        for content in contents:
           size = size + content['Size']
        current_app.logger.debug("Size of Page: %s ", size)
        return size

    def setBucketSetting(self):
        bucketName = self.s3WebData.bucketData.currentName
        s3client = S3Request.getBoto3Client(s3AccessConfig=self.s3AccessConfigs[self.s3WebData.accessData.currentName], currentBucketName=bucketName)
        self.bucketConfig.bucketWebsite = bucketWebsite(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketLifecycle = bucketLifecycle(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketNotification = bucketNotification(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketRequestPayment = bucketRequestPayment(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketTagSet = bucketTagSet(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketLogging = bucketLogging(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketMetricsConfig = bucketMetricsConfig(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketInventoryConfiguration = bucketInventoryConfiguration(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketIntelligentTieringConfig = bucketIntelligentTieringConfig(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketAnalyticsConfig = bucketAnalyticsConfig(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketPolicy = bucketPolicy(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketACL = bucketACL(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketCORS = bucketCORS(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketEncryption = bucketEncryption(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketVersioning = bucketVersioning(s3client, bucketName).withDataToJson()
        self.bucketConfig.bucketReplication = bucketReplication(s3client, bucketName).withDataToJson()

class statics:
    def sizeof_fmt(num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

