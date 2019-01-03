from serious_django_permissions.permissions import Permission

from .models import RestrictedModel # TODO: Add this step to documentation?


"""
class GlobalPermission(Permission):
    model = '' # model not defined for global permissions.
    description = 'Enables the user to write in any model'
"""
# TODO: How to set a GlobalPermission?

class RestrictedModelPermission(Permission):
    model = 'RestrictedModel' # should be a model inside myapp.models, or not defined for global permissions.
    description = 'Enables the user to write in RestrictedModel'
