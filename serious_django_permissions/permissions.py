import importlib
import inspect
from abc import ABC, ABCMeta

from django.apps import AppConfig
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission as DjangoPermission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from guardian.backends import ObjectPermissionChecker

from .models import GlobalPermission
from .helpers import camel_to_snake


class PermissionMetaclass(ABCMeta):
    def __iter__(cls):
        # Adding this method enables a Permission subclass to be treated
        # as a list of permissions, which makes checks more idiomatic
        return iter([cls])

    def split(cls, *args, **kwargs):
        # Adding this method is a hacky way of enabling usage of
        # guardian.shortcuts.assign_perm, which expects either a Django
        # Permission object or a string, and for the latter just expects
        # that `.split()` is present on the object. We pretend to be a
        # string in the eyes of `assign_perm` by adding this method.
        return cls.codename.split(*args, **kwargs)

    def __str__(cls):
        return cls.__name__

    def __new__(mcls, name, *args, **kwargs):
        cls = super(PermissionMetaclass, mcls).__new__(mcls, name, *args, **kwargs)
        if cls.__base__ == ABC:
            return cls

        app = cls.__module__.split('.')[0]
        lib = importlib.import_module("{}.apps".format(app))
        app_config = next(
            obj for name, obj in inspect.getmembers(lib)
            if type(obj) == type(AppConfig) and issubclass(obj, AppConfig) \
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
    def _update_or_create(cls):
        """
        !!! This method is private and is intended to only be called from the
        create_permissions management command. Do not call it from your code.

        Creates and returns this permission, or updates and returns it based on a
        matching instance (wrt. codename and content type).
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

            return DjangoPermission.objects.update_or_create(
                codename=cls.codename,
                content_type=content_type,
                defaults={'name': cls.description},
            )
        else:
            return GlobalPermission.objects.update_or_create(
                codename=cls.codename,
                name=cls.description
            )

    @classmethod
    def get(cls):
        """
        Returns the DB instance representing this permission.
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

            return DjangoPermission.objects.get(
                codename=cls.codename,
                content_type=content_type,
            )
        else:
            return GlobalPermission.objects.get(
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

        if obj is not None:  # use django-guardian check if obj is passed
            if "has_object_permission" in dir(perm): # do programmatic checks…
                return perm.has_object_permission(user_obj, obj)
            check = ObjectPermissionChecker(user_obj)
            return check.has_perm(perm_str, obj)

        return super().has_perm(user_obj, perm_str, obj)
