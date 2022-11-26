import datetime
from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Table, Text, Boolean
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


class S3AppVersion(Model):
    __tablename__ = 's3_app_version'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    mayor = Column(Integer, nullable=False, unique=False)
    minor = Column(Integer, nullable=False, unique=False)
    patch = Column(Integer, nullable=False, unique=False)
    updated_at = Column(String(150), default=datetime.datetime.now().isoformat(), nullable=False)
    is_current = Column(Boolean, nullable=False, unique=False)


class S3User(User):
    __tablename__ = 'ab_user'
    groups = relationship('S3Group', secondary=s3_assoc_user_group, back_populates='users')
    s3_accesses = relationship('S3Access', secondary=s3_assoc_user_s3access, back_populates='users')


class S3Endpoint(Model):
    __tablename__ = 's3_endpoint'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    url = Column(String(150), nullable=True, unique=False)
    trust_ca_bundle = Column(Text, nullable=True, unique=False)
    s3_default_region = Column(String(150), nullable=False, unique=False)
    s3_accesses = relationship("S3Access", back_populates='s3_endpoint')
    s3_provider_id = Column(Integer, ForeignKey('s3_provider.id'), nullable=True)
    s3_provider = relationship("S3Provider", back_populates='s3_endpoints')

    def __repr__(self):
        return self.name


class S3Provider(Model):
    __tablename__ = 's3_provider'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    full_name = Column(String(150), nullable=True, unique=False)
    endpoint_url_template = Column(String(150), nullable=True, unique=False)
    url = Column(String(150), nullable=True, unique=False)
    s3_endpoints = relationship("S3Endpoint", back_populates='s3_provider')

    def __repr__(self):
        return self.name


class S3Group(Model):
    __tablename__ = 's3_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    users = relationship('S3User', secondary=s3_assoc_user_group, back_populates='groups')
    s3_accesses = relationship('S3Access', secondary=s3_assoc_group_s3access, back_populates='groups')

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

    def __repr__(self):
        return self.name