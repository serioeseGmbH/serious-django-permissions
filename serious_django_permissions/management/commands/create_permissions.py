from abc import ABC
import importlib
import inspect

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from serious_django_permissions.permissions import Permission

class Command(BaseCommand):
    """
    A command to aggregate the permissions out of all our apps and create them in django models
    """
    help = "create permissions defined anywhere in the current Django project's apps"

    def handle(self, *args, **options):
        """
            This method iterates through all installed apps and searches for 
            classes that are inheriting our Permission class. 
            If it finds one it creates the permission in the django model
        """
        for app in settings.INSTALLED_APPS:
            lib = importlib.util.find_spec("{}.permissions".format(app))
            if lib:
                lib = importlib.import_module("{}.permissions".format(app))
                for name, obj in inspect.getmembers(lib):
                    if type(obj) == type(Permission) and issubclass(obj, Permission)\
                       and obj.__base__ != ABC:
                        perm, created_at = obj.get_or_create()
                
