from serious_django_permissions.permissions import Permission

from .models import RestrictedModel # TODO: Add this step to documentation?


class RestrictedModelPermission(Permission):
    model = 'RestrictedModel'
    description = 'Enables the user to write in RestrictedModel'

class GlobalPermission(Permission):
    model = None
    description = 'Enables the user to write in any model'
