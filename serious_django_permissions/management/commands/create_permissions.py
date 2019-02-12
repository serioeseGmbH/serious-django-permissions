from django.core.management.base import BaseCommand

from ... import helpers


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
        helpers.create_permissions(self, *args, **options)
