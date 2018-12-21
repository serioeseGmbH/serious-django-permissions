from abc import ABC
import importlib
import inspect
import sys

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from helpers.permissions import Group

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

        try:
            groups_module = settings.DEFAULT_GROUPS_MODULE
        except AttributeError:
            print("DEFAULT_GROUPS_MODULE setting is not set!", file=sys.stderr)
            return
        
        lib = importlib.import_module(groups_module)
        for name, obj in inspect.getmembers(lib):
            if type(obj) == type(Group) and issubclass(obj, Group)\
               and obj.__base__ != ABC:
                group, created_at = obj.get_or_create()
                perm_db_objs = [
                    perm.get_or_create()[0] for perm in obj.permissions
                ]
                group.permissions.set(perm_db_objs)
