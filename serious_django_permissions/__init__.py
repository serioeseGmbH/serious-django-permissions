import importlib
import inspect
import re
from abc import ABC, ABCMeta

from django.apps import AppConfig
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import\
    Permission as DjangoPermission, Group as DjangoGroup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured

from .models import GlobalPermission

# https://stackoverflow.com/a/1176023/3090225
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def camel_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class PermissionMetaclass(ABCMeta):
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

        if not name.endswith('Permission'):
            raise ImproperlyConfigured(
                "A Permission class's name must end with 'Permission'."
            )
        if not hasattr(cls, 'description') or not isinstance(cls.description, str):
            raise ImproperlyConfigured(
                "A Permission class must have a 'description' attribute."
            )

        if not hasattr(cls, 'codename'):
            cls.codename = camel_to_snake(name[:-10])

        cls.__perm_str__ = '{}.{}'.format(cls.app_label, cls.codename)

        return cls


class Permission(ABC, metaclass=PermissionMetaclass):
    @classmethod
    def get_or_create(cls):
        """
        Convenience method for creating and returning this permission in the
        database, or retrieving a matching instance already stored in the DB.
        """
        content_type = None
        if cls.model is not None:
            content_type = ContentType.objects.get(
                app_label=cls.app_label,
                model=cls.model.lower()
            )
        else:
            content_type = ContentType.objects.get_for_model(GlobalPermission)

        return DjangoPermission.objects.get_or_create(
            codename=cls.codename,
            name=cls.description,
            content_type=content_type
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


### Groups

class GroupMetaclass(ABCMeta):
    def __new__(mcls, name, *args, **kwargs):
        cls = super(GroupMetaclass, mcls).__new__(mcls, name, *args, **kwargs)
        if cls.__base__ == ABC:
            return cls

        if not name.endswith('Group'):
            raise ImproperlyConfigured(
                "A Group class's name must end with 'Group'."
            )
        if not hasattr(cls, 'permissions') or\
           not isinstance(cls.permissions, (list, tuple)) or\
           not all(\
                   type(x) == type(Permission) and\
                   issubclass(x, Permission) and\
                   not x is Permission\
                   for x in cls.permissions
           ):
            raise ImproperlyConfigured(
                "A Group class must have a 'permissions' attribute, which must "
                "be a list of Permission classes (except the Permission "
                "base class)."
            )

        if not hasattr(cls, 'group_name'):
            cls.group_name = camel_to_snake(name[:-5])

        return cls


class Group(ABC, metaclass=GroupMetaclass):
    @classmethod
    def get_or_create(cls):
        """
        Convenience method for creating and returning this group in the
        database, or retrieving a matching instance already stored in the DB.
        """
        return DjangoGroup.objects.get_or_create(
            name=cls.group_name,
        )
