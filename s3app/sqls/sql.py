import os

from flask import current_app
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from s3app.s3_sec_models import S3Endpoint, S3Provider, S3Group, S3Access, S3AppVersion


class Sqls:
    engine = None
    session = None
    folderPath = ""


    def __init__(self, app=None):
        if app is None:
            self.engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        else:
            self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))
        self.folderPath = os.path.dirname(os.path.abspath(__file__))

    def update_1_0_0(self):
        ma, mi, pa = 1, 0, 0
        if self.session.query(S3AppVersion).count() == 0:
            self.setNewVersion(ma, mi, pa)
            self.setDefaultProvider()
            self.setDefaultEndpoints()

    def update_1_2_0(self):
        ma, mi, pa = 1, 2, 0
        if self.upgradeNeeded(ma, mi, pa):
            self.setNewVersion(ma, mi, pa)
            self.executeSQLScript(self.folderPath + "/1_2_0.sql")

    def executeSQLScript(self, file_path):
        with self.engine.connect() as con:
            with open(file_path) as file:
                query = text(file.read())
                con.execute(query)

    def upgradeNeeded(self, mayor, minor, patch):
        curr_mayor, curr_minor, curr_patch = self.getCurrentVersion()
        if curr_mayor < mayor or curr_minor < minor or curr_patch < patch:
            return True
        return False

    def getCurrentVersion(self):
        current_version = self.session.query(S3AppVersion).filter_by(is_current=True).first()
        return current_version.mayor, current_version.minor, current_version.patch

    def setNewVersion(self, mayor, minor, patch):
        curr_vers = self.session.query(S3AppVersion).filter_by(is_current=True).all()
        for curr_ver in curr_vers:
            curr_ver.is_current = False
            self.session.commit()
        newVersion = S3AppVersion(
            name="{}.{}.{}".format(mayor, minor, patch),
            mayor=mayor,
            minor=minor,
            patch=patch,
            is_current=True
        )
        self.session.add(newVersion)
        self.session.commit()

    def getEndpointForRegion(self, region):
        return self.session.query(S3Endpoint).filter_by(s3_default_region=region).first()

    def setDefaultProvider(self):
        amount = self.session.query(S3Provider).count()
        provider = {
            "AWS": {
                'id': 1,
                'full_name': "Amazon Web Services",
                'endpoint_url_template': "s3.<region>.amazonaws.com",
                'url': "https://aws.amazon.com/de/s3/"
            },
            "Oracle": {
                'id': 2,
                'full_name': "Oracle Cloud Object Storage",
                'endpoint_url_template': "example.compat.objectstorage.<region>.oraclecloud.com",
                'url': "https://docs.oracle.com/en-us/iaas/Content/Object/"
            },
            "Alibaba": {
                'id': 3,
                'full_name': "Alibaba Cloud OSS",
                'endpoint_url_template': "oss-<region>.aliyuncs.com",
                'url': "https://www.alibabacloud.com/help/en/object-storage-service"
            },
            "Backblaze": {
                'id': 4,
                'full_name': "Backblaze B2",
                'endpoint_url_template': "s3.<region>.backblazeb2.com",
                'url': "https://www.backblaze.com/"
            },
            "Digitalocean": {
                'id': 5,
                'full_name': "DigitalOcean Spaces",
                'endpoint_url_template': "<region>.digitaloceanspaces.com",
                'url': "https://docs.digitalocean.com/products/spaces/"
            },
            "IBM": {
                'id': 6,
                'full_name': "IBM Cloud Object Storage",
                'endpoint_url_template': "s3.<region>.cloud-object-storage.appdomain.cloud",
                'url': "https://cloud.ibm.com/docs/cloud-object-storage"
            },
            "Linode": {
                'id': 7,
                'full_name': "Linode Object Storage",
                'endpoint_url_template': "<region>.linodeobjects.com",
                'url': "https://www.linode.com/products/object-storage/"
            },
            "IONOS": {
                'id': 8,
                'full_name': "IONOS Cloud S3 Object Storage",
                'endpoint_url_template': "S3-<region>.ionoscloud.com",
                'url': "https://cloud.ionos.de/storage/object-storage"
            }
        }
        if amount < len(provider):
            for name, param in provider.items():
                provider = S3Provider(name=name, id=param['id'],
                                      full_name=param['full_name'],
                                      endpoint_url_template=param['endpoint_url_template'],
                                      url=param['url'])
                self.session.add(provider)
            self.session.commit()

    def setDefaultEndpoints(self):
        amount = self.session.query(S3Endpoint).count()
        enpoints = {
            "aws_us_east_1": {
                "s3_provider_id": 1,
                "region": "us-east-1"
            },
            "aws_eu_central_1": {
                "s3_provider_id": 1,
                "region": "eu-central-1"
            },
            "oracle_cn_beijing": {
                "s3_provider_id": 2,
                "region": "us-east-1"
            },
            "alibaba_cn_beijing": {
                "s3_provider_id": 3,
                "region": "cn-beijing"
            },
            "backblaze_us_west_002": {
                "s3_provider_id": 4,
                "region": "us-west-002"
            },
            "digitalocean_us_east_1": {
                "s3_provider_id": 5,
                "region": "us-east-1"
            },
            "ibm_eu_de": {
                "s3_provider_id": 6,
                "region": "eu-de"
            },
            "ibm_eu_west": {
                "s3_provider_id": 7,
                "region": "eu-west"
            },
            "ionos_eu_central_1": {
                "s3_provider_id": 8,
                "region": "eu-central-1"
            },
        }
        if amount < len(enpoints):
            for name, param in enpoints.items():
                endpoint = S3Endpoint(name=name, s3_default_region=param['region'],
                                      s3_provider_id=param['s3_provider_id'],
                                      url="",
                                      trust_ca_bundle="")
                self.session.add(endpoint)
            self.session.commit()
