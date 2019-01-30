from serious_django_permissions.groups import Group

from test_app.permissions import RestrictedModelPermission


class InvalidName(Group):
    permissions = [
        RestrictedModelPermission
    ]
