from serious_django_permissions.permissions import Permission


class MissingDPermission(Permission):
    model = 'RestrictedModel'
