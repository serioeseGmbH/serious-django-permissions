from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class GlobalPermissionManager(models.Manager):
    def get_queryset(self):
        return super(GlobalPermissionManager, self).get_queryset().filter(
            content_type=ContentType.objects.get_for_model(
                GlobalPermission,
                for_concrete_model=False
            )
        )


class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    def save(self, *args, **kwargs):
        self.content_type = ContentType.objects.get_for_model(
            GlobalPermission,
            for_concrete_model=False
        )
        return super().save(*args, **kwargs)

    class Meta:
        proxy = True
