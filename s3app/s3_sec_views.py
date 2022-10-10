from flask_appbuilder.security.views import UserDBModelView
from flask_appbuilder import ModelView
from .s3_sec_models import S3Access, S3Group, S3Endpoint
from flask_appbuilder.models.sqla.interface import SQLAInterface

from flask_babel import lazy_gettext


class S3EndpointModelView(ModelView):
    route_base = '/s3endpoints'
    datamodel = SQLAInterface(S3Endpoint)
    list_columns = [
        'name',
        'url',
        's3_accesses'
    ]
    edit_columns = [
        'name',
        'url',
        's3_accesses',
        's3_default_region',
        'trust_ca_bundle'
    ]
    add_columns = [
        'name',
        'url',
        's3_accesses',
        's3_default_region',
        'trust_ca_bundle'
    ]


class S3AccessModelView(ModelView):
    route_base = '/s3access'
    datamodel = SQLAInterface(S3Access)
    list_columns = [
        'name',
        's3_access_key',
        's3_endpoint',
        'users',
        'groups'
    ]
    edit_columns = [
        'name',
        's3_access_key',
        's3_secret_key',
        's3_endpoint',
        'users',
        'groups'
    ]
    add_columns = [
        'name',
        's3_access_key',
        's3_secret_key',
        's3_endpoint',
        'users',
        'groups'
    ]


class S3GroupModelView(ModelView):
    route_base = '/s3group'
    datamodel = SQLAInterface(S3Group)
    list_columns = [
        'name',
        'users',
        's3_accesses'
    ]
    edit_columns = [
        'name',
        'users',
        's3_accesses'
    ]
    add_columns = [
        'name',
        'users',
        's3_accesses'
    ]


class S3UserDBModelView(UserDBModelView):
    """
        View that add DB specifics to User view.
        Override to implement your own custom view.
        Then override userdbmodelview property on SecurityManager
    """
    related_views = [S3GroupModelView, S3AccessModelView]

    show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'roles', 'login_count', 'extra']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
        (lazy_gettext('Audit Info'),
         {'fields': ['last_login', 'fail_login_count', 'created_on',
                     'created_by', 'changed_on', 'changed_by'], 'expanded': False}),
    ]
    user_show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'roles', 'login_count', 'extra']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
    ]
    add_columns = [
        'first_name',
        'last_name',
        'username',
        'active',
        'email',
        'roles',
        'password',
        'conf_password',
        's3_accesses',
        'groups'
    ]
    list_columns = [
        'first_name',
        'last_name',
        'username',
        'email',
        'active',
        'roles',
        's3_accesses',
        'groups'
    ]
    edit_columns = [
        'first_name',
        'last_name',
        'username',
        'active',
        'email',
        'roles',
        's3_accesses',
        'groups'
    ]