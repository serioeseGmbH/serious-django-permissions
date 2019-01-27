from django.db import models
from django.contrib.auth.models import Permission


class GlobalPermissionManager(models.Manager):
    def get_query_set(self):
        return super(GlobalPermissionManager, self).\
            get_query_set().filter(content_type__name='global_permission')


class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True
