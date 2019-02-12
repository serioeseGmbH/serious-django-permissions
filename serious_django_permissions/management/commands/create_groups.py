from django.core.management.base import BaseCommand

from ... import helpers


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
        helpers.create_groups(self, *args, **options)
