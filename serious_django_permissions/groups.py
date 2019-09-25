from abc import ABC, ABCMeta

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import Group as DjangoGroup

from .permissions import Permission
from .helpers import camel_to_snake


class GroupMetaclass(ABCMeta):
    def __int__(cls):
        return cls.get().pk

    def __str__(cls):
        return cls.__name__

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
    def get(cls):
        """
        Returns the DB instance representing this group.
        """
        return DjangoGroup.objects.get(
            name=cls.group_name,
        )

    @classmethod
    def _update_or_create(cls):
        """
        !!! This method is private and is intended to only be called from the
        create_permissions management command. Do not call it from your code.

        Creates and returns this group, or updates and returns it based on a
        matching instance.
        """

        return DjangoGroup.objects.update_or_create(
            name=cls.group_name,
        )
