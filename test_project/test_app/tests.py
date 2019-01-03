from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from serious_django_permissions.management.commands import create_permissions, create_groups

from .models import RestrictedModel, UnrestrictedModel
from .permissions import RestrictedModelPermission
from .groups import AuthorizedGroup


class ManageFunctionTests(TestCase):

    def test_create_user_permissions(self):

        perm = Permission.objects.filter(codename=RestrictedModelPermission.codename)
        self.assertFalse(perm, 'queryset is empty')

        create_permissions.Command().handle()

        perm = Permission.objects.filter(codename=RestrictedModelPermission.codename)
        self.assertTrue(perm, 'queryset is empty')

    def test_create_group_permissions(self):
        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertFalse(perm, 'queryset is not empty')

        create_groups.Command().handle()

        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertTrue(perm, 'queryset is empty')


class UserLevelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorized_user = get_user_model().objects.create(
            username='authorized_user'
        )
        perm, created_at = RestrictedModelPermission.get_or_create()
        cls.authorized_user.user_permissions.add(perm)

        cls.unauthorized_user = get_user_model().objects.create(
            username='unauthorized_user'
        )

    def test_unauthorized_user_does_not_have_permission(self):
        self.assertFalse(self.unauthorized_user.has_perm(RestrictedModelPermission))
        self.assertTrue(self.unauthorized_user.has_perm(None))

    def test_authorized_user_has_permission(self):
        self.assertTrue(self.authorized_user.has_perm(RestrictedModelPermission))
        self.assertFalse(self.authorized_user.has_perm(None))

class GroupLevelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorized_user = get_user_model().objects.create(
            username='authorized_user'
        )
        cls.unauthorized_user = get_user_model().objects.create(
            username='unauthorized_user'
        )
        create_permissions.Command().handle()
        create_groups.Command().handle()

    def test_authorize_user_via_group(self):
        self.authorized_user.groups.add(AuthorizedGroup.get_or_create()[0].pk)
        self.assertTrue(self.authorized_user.has_perm(RestrictedModelPermission))
        self.assertFalse(self.authorized_user.has_perm(None))

    def test_unauthorized_user_does_not_have_permission(self):
        self.assertFalse(self.unauthorized_user.has_perm(RestrictedModelPermission))
        self.assertTrue(self.unauthorized_user.has_perm(None))
