from serious_django_permissions.groups import Group

from test_app.permissions import RestrictedModelPermission

class AuthorizedGroup(Group):
    permissions = [
        RestrictedModelPermission
    ]

class UnauthorizedGroup(Group):
    permissions = [
            ]
