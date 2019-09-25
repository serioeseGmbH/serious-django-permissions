import re
from abc import ABC
import importlib
import inspect

from django.core.management.base import BaseCommand
from django.conf import settings


# https://stackoverflow.com/a/1176023/3090225
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def camel_to_snake(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def create_permissions(*args, **options):
    from .permissions import Permission

    for app in settings.INSTALLED_APPS:
            lib = importlib.util.find_spec("{}.permissions".format(app))
            if lib:
                lib = importlib.import_module("{}.permissions".format(app))
                for name, obj in inspect.getmembers(lib):
                    if type(obj) == type(Permission) and issubclass(obj, Permission)\
                       and obj.__base__ != ABC:
                        perm, created_at = obj._update_or_create()

def create_groups(*args, **options):
    from .groups import Group

    create_permissions()

    if not getattr(settings, 'DEFAULT_GROUPS_MODULE', None):
        raise AttributeError("DEFAULT_GROUPS_MODULE setting is not set!")

    else:
        groups_module = settings.DEFAULT_GROUPS_MODULE

    lib = importlib.import_module(groups_module)
    for name, obj in inspect.getmembers(lib):
        if type(obj) == type(Group) and issubclass(obj, Group)\
           and obj.__base__ != ABC:
            group, created_at = obj._update_or_create()
            perm_db_objs = [
                perm.get() for perm in obj.permissions
            ]
            group.permissions.set(perm_db_objs)

def setup_permissions():
    create_groups()
