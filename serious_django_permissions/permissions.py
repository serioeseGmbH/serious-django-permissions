import importlib
import inspect
from abc import ABC, ABCMeta

from django.apps import AppConfig
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission as DjangoPermission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from .helpers import camel_to_snake
from .models import GlobalPermission


class PermissionMetaclass(ABCMeta):
    def __iter__(mcls):
        return iter([mcls])

    def __new__(mcls, name, *args, **kwargs):
        cls = super(PermissionMetaclass, mcls).__new__(mcls, name, *args, **kwargs)
        if cls.__base__ == ABC:
            return cls

        app = cls.__module__.split('.')[0]
        lib = importlib.import_module("{}.apps".format(app))
        app_config = next(
            obj for name, obj in inspect.getmembers(lib)
            if type(obj) == type(AppConfig) and issubclass(obj, AppConfig)\
            and obj != AppConfig
        )
        cls.app_label = app_config.name

        if not hasattr(cls, 'model'):
            raise ImproperlyConfigured(
                "A Permission must contain an explicit `model` attribute. "
                "If you want to define this permission as global, set `model` "
                "to None explicitly."
            )
        if not name.endswith('Permission'):
            raise ImproperlyConfigured(
                "A Permission class's name must end with 'Permission'."
            )
        if not cls.description or not isinstance(cls.description, str):
            raise ImproperlyConfigured(
                "A Permission class must have a 'description' attribute."
            )

        if not hasattr(cls, 'codename'):
            cls.codename = camel_to_snake(name[:-10])

        if cls.model is None:
            cls.codename = '{}.{}'.format(cls.app_label, cls.codename)
            cls.__perm_str__ = 'serious_django_permissions.{}'.format(cls.codename)
        else:
            cls.__perm_str__ = '{}.{}'.format(cls.app_label, cls.codename)

        return cls


class Permission(ABC, metaclass=PermissionMetaclass):
    model = None
    description = ""

    @classmethod
    def get_or_create(cls):
        """
        Convenience method for creating and returning this permission in the
        database, or retrieving a matching instance already stored in the DB.
        """
        if cls.model is not None:
            if isinstance(cls.model, str):
                content_type = ContentType.objects.get(
                    app_label=cls.app_label,
                    model=cls.model.lower()
                )
            elif issubclass(cls.model, models.Model):
                content_type = ContentType.objects.get_for_model(
                    cls.model,
                    for_concrete_model=False
                )
            else:
                raise ValueError(
                    "{}.model is not a string or models.Model subclass!".format(cls)
                )

            return DjangoPermission.objects.get_or_create(
                codename=cls.codename,
                name=cls.description,
                content_type=content_type
            )
        else:
            return GlobalPermission.objects.get_or_create(
                codename=cls.codename,
                name=cls.description
            )

    @classmethod
    def user_has_perm(cls, user):
        return user.has_perm(cls.__perm_str__)


class PermissionModelBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if type(perm) == type(Permission) and issubclass(perm, Permission):
            perm_str = perm.__perm_str__
        else:
            perm_str = perm
        return super().has_perm(user_obj, perm_str, obj)
