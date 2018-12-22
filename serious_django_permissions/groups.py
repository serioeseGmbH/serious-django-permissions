from abc import ABC, ABCMeta

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import Group as DjangoGroup

from .helpers import camel_to_snake
from .permissions import Permission


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
