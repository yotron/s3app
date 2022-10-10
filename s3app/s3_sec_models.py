from datetime import date

from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Table, Text, Date
from sqlalchemy.orm import relationship, registry
from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey

mapper_registry = registry()

s3_assoc_user_s3access = Table('s3_assoc_user_s3access', Model.metadata,
                               Column('user_id', Integer, ForeignKey('ab_user.id'), primary_key=True),
                               Column('s3_access_id', Integer, ForeignKey('s3_access.id'), primary_key=True)
                               )

s3_assoc_group_s3access = Table('s3_assoc_group_s3access', Model.metadata,
                                Column('s3_group_id', Integer, ForeignKey('s3_group.id'), primary_key=True),
                                Column('s3_access_id', Integer, ForeignKey('s3_access.id'), primary_key=True)
                                )

s3_assoc_user_group = Table('s3_assoc_user_group', Model.metadata,
                            Column('user_id', Integer, ForeignKey('ab_user.id'), primary_key=True),
                            Column('s3_group_id', Integer, ForeignKey('s3_group.id'), primary_key=True)
                            )


class S3User(User):
    __tablename__ = 'ab_user'
    groups = relationship('S3Group', secondary=s3_assoc_user_group, back_populates='users')
    s3_accesses = relationship('S3Access', secondary=s3_assoc_user_s3access, back_populates='users')


class S3Endpoint(Model):
    __tablename__ = 's3_endpoint'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    url = Column(String(150), nullable=False, unique=False)
    trust_ca_bundle = Column(Text, nullable=True, unique=False)
    s3_default_region = Column(String(150), nullable=False, unique=False)
    s3_accesses = relationship("S3Access", back_populates='s3_endpoint')

    def __repr__(self):
        return self.name


class S3Group(Model):
    __tablename__ = 's3_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    users = relationship('S3User', secondary=s3_assoc_user_group, back_populates='groups')
    s3_accesses = relationship('S3Access', secondary=s3_assoc_group_s3access, back_populates='groups')
    begin_date = Column(Date, default=date.today(), nullable=False)
    end_date = Column(Date, nullable=True)

    def __repr__(self):
        return self.name


class S3Access(Model):
    __tablename__ = 's3_access'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    s3_access_key = Column(String(150), nullable=False, unique=False)
    s3_secret_key = Column(String(150), nullable=False)
    s3_endpoint_id = Column(Integer, ForeignKey('s3_endpoint.id'), nullable=False)
    s3_endpoint = relationship("S3Endpoint", back_populates='s3_accesses')
    users = relationship('S3User', secondary=s3_assoc_user_s3access, back_populates='s3_accesses')
    groups = relationship('S3Group', secondary=s3_assoc_group_s3access, back_populates='s3_accesses')
    begin_date = Column(Date, default=date.today(), nullable=False)
    end_date = Column(Date, nullable=True)

    def __repr__(self):
        return self.name


class Sqls:
    def __init__(self, db):
        self.db = db
        self.session = db.session

    def getEndpointForRegion(self, region):
        return self.db.session.query(S3Endpoint).filter_by(s3_default_region=region).first()

    def setUserAccessView(self):
        print("Info: Create view s3_user_access")
        sql = """CREATE VIEW s3_user_access
        AS SELECT distinct acc.user_id,
            acc.s3_access_name,
            acc.s3_access_key,
            acc.s3_secret_key,
            endp.s3_default_region,
            endp.url,
            endp.name,
            endp.trust_ca_bundle
           FROM ( SELECT ug.user_id,
                    s3a.name AS s3_access_name,
                    s3a.s3_access_key,
                    s3a.s3_secret_key,
                    s3a.s3_endpoint_id
                   FROM s3_assoc_user_group ug
                     JOIN s3_group gr ON gr.id = ug.s3_group_id
                     JOIN s3_assoc_group_s3access gs3a ON gr.id = gs3a.s3_group_id
                     JOIN s3_access s3a ON gs3a.s3_access_id = s3a.id
                UNION
                 SELECT us3a.user_id,
                    s3a.name AS s3_access_name,
                    s3a.s3_access_key,
                    s3a.s3_secret_key,
                    s3a.s3_endpoint_id
                   FROM s3_assoc_user_s3access us3a
                     JOIN s3_access s3a ON us3a.s3_access_id = s3a.id) acc
             JOIN s3_endpoint endp ON endp.id = acc.s3_endpoint_id;"""
        self.db.engine.execute(sql)

    def setDefaultEndpoints(self):
        amount = self.session.query(S3Endpoint).count()
        enpoints = {
            "aws_us_east_1": {
                "url": "s3.us-east-1.amazonaws.com",
                "region": "us-east-1"
            },
            "aws_us_west_1": {
                "url": "s3.us-west-1.amazonaws.com",
                "region": "us-west-1"
            },
            "aws_af_south_1": {
                "url": "s3.af-south-1.amazonaws.com",
                "region": "af-south-1"
            },
            "aws_ap_southeast_1": {
                "url": "s3.ap-southeast-1.amazonaws.com",
                "region": "ap-southeast-1"
            },
            "aws_ap_south_1": {
                "url": "s3.ap-south-1.amazonaws.com",
                "region": "ap-south-1"
            },
            "aws_eu_central_1": {
                "url": "s3.eu-central-1.amazonaws.com",
                "region": "eu-central-1"
            },
            "aws_eu_west_1": {
                "url": "s3.eu-west-1.amazonaws.com",
                "region": "eu-west-1"
            },
            "aws_sa_east_1": {
                "url": "s3.sa-east-1.amazonaws.com",
                "region": "sa-east-1"
            },
            "aws_me_south_1": {
                "url": "s3.me-south-1.amazonaws.com",
                "region": "me-south-1"
            },
            "aws_region": {
                "url": "s3.region.amazonaws.com",
                "region": "region"
            },
            "ionos_cloud_eu_central_1": {
                "url": "S3-eu-central-1.ionoscloud.com",
                "region": "eu-central-1"
            },
            "ionos_cloud_eu_central_2": {
                "url": "S3-eu-central-2.ionoscloud.com",
                "region": "eu-central-2"
            }
        }
        if amount < len(enpoints):
            for name, param in enpoints.items():
                endpoint = S3Endpoint(name=name, url=param['url'], s3_default_region=param['region'],
                                      trust_ca_bundle="")
                self.session.add(endpoint)
            self.session.commit()

    def setTestData(self, appbuilder):
        amount = self.session.query(User).count()
        accesses = {
            "S3Cloud1": {
                "accesskey": "00e11fd15cbc81b24ac1",
                "secretKey": "NBP7v6E7QYPRrpDlVYmg7p+uZeeAoCLK4pfGOJHc",
                "endpoint": "ionos_cloud_eu_central_2"
            },
            "S3Cloud2": {
                "accesskey": "00e11fd15cbc81b24ac1",
                "secretKey": "NBP7v6E7QYPRrpDlVYmg7p+uZeeAoCLK4pfGOJHc",
                "endpoint": "ionos_cloud_eu_central_2"
            },
            "S3Cloud3": {
                "accesskey": "00e11fd15cbc81b24ac1",
                "secretKey": "NBP7v6E7QYPRrpDlVYmg7p+uZeeAoCLK4pfGOJHc",
                "endpoint": "ionos_cloud_eu_central_1"
            }
        }
        sets = {
            "user1": {
                "Group1": "S3Cloud1"
            },
            "user2": {
                "Group1": "S3Cloud2"
            },
            "user3": {
                "Group1": "S3Cloud2"
            }
        }
        role_admin = appbuilder.sm.find_role(
            appbuilder.sm.auth_role_admin
        )
        for username, groupdict in sets.items():
            user = appbuilder.sm.add_user(
                username=username,
                first_name=username,
                last_name=username,
                email=username + "n@example.com",
                role=role_admin,
                password=username
            )
            for groupname in list(groupdict.keys()):
                group = self.session.query(S3Group).filter_by(name=groupname).first()
                if group == None:
                    group = S3Group(name=groupname)
                access = self.session.query(S3Access).filter_by(name=groupdict[groupname]).first()
                if access == None:
                    accessdict = accesses[groupdict[groupname]]
                    endpointid = self.session.query(S3Endpoint.id).filter_by(
                        name=accessdict['endpoint']).scalar_subquery()
                    access = S3Access(name=groupdict[groupname], s3_access_key=accessdict['accesskey'],
                                      s3_secret_key=accessdict['secretKey'], s3_endpoint_id=endpointid)
                group.s3_accesses.append(access)
                user.groups.append(group)
            self.session.add(user)
        self.session.commit()
