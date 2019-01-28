from serious_django_permissions.permissions import Permission


class InvalidName(Permission):
    model = 'RestrictedModel'
    description = 'Enables the user to write in RestrictedModel'
