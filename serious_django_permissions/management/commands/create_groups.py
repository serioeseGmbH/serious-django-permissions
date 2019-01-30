from abc import ABC
import importlib
import inspect
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from serious_django_permissions.groups import Group

class Command(BaseCommand):
    """
    A command to aggregate the groups and permissions out of all our apps and create them in django models
    """
    help = 'create groups defined in a module referenced by the DEFAULT_GROUPS_MODULE setting.'

    def handle(self, *args, **options):
        """
            This method looks at the module set in DEFAULT_GROUPS_FILE and
            searches for classes that are inheriting our Group class.
            It creates a Django Group with associated permissions for each found.
        """
        from .create_permissions import Command as CreatePermissionsCommand
        CreatePermissionsCommand().handle()

        if not getattr(settings, 'DEFAULT_GROUPS_MODULE', None):
            raise AttributeError("DEFAULT_GROUPS_MODULE setting is not set!")

        else:
            groups_module = settings.DEFAULT_GROUPS_MODULE

        lib = importlib.import_module(groups_module)
        for name, obj in inspect.getmembers(lib):
            if type(obj) == type(Group) and issubclass(obj, Group)\
               and obj.__base__ != ABC:
                group, created_at = obj.get_or_create()
                perm_db_objs = [
                    perm.get_or_create()[0] for perm in obj.permissions
                ]
                group.permissions.set(perm_db_objs)
