from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from serious_django_permissions.management.commands import create_permissions, create_groups

from .models import RestrictedModel, UnrestrictedModel
from .permissions import RestrictedModelPermission, GlobalPermission
from .groups import AuthorizedGroup
from .views import restricted_view

class ManageFunctionTests(TestCase):

    def test_create_user_permissions(self):
        perm = Permission.objects.filter(codename=RestrictedModelPermission.codename)
        self.assertFalse(perm, 'The permission should not exist yet, but it does.')

        create_permissions.Command().handle()

        perm = Permission.objects.filter(codename=RestrictedModelPermission.codename)
        self.assertTrue(perm, 'The permission should exist, but it doesnt.')

    def test_create_group_permissions(self):
        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertFalse(perm, 'The group should not exist yet, but it does.')

        create_groups.Command().handle()

        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertTrue(perm, 'The group should not exist yet, but it does.')

    def test_create_global_permission(self):
        perm = Permission.objects.filter(codename=GlobalPermission.codename)
        self.assertFalse(perm, 'The permission should not exist yet, but it does.')

        create_permissions.Command().handle()

        perm = Permission.objects.filter(codename=GlobalPermission.codename)
        self.assertTrue(perm, 'The permission should exist, but it doesnt.')


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

        cls.factory = RequestFactory()

    def test_unauthorized_user_does_not_have_permission(self):
        self.assertFalse(self.unauthorized_user.has_perm(RestrictedModelPermission))

    def test_authorized_user_has_permission(self):
        self.assertTrue(self.authorized_user.has_perm(RestrictedModelPermission))

    def test_unauthorized_user_accessing_view(self):
        request = self.factory.get('/restricted_view')
        request.user = self.unauthorized_user
        response = restricted_view(request)

        self.assertEqual(response.status_code, 302)

    def test_authorized_user_accessing_view(self):
        request = self.factory.get('/restricted_view')
        request.user = self.authorized_user
        response = restricted_view(request)

        self.assertEqual(response.status_code, 200)

class GroupLevelTests(TestCase):

    def setUp(self):
        self.authorized_user = get_user_model().objects.create(
            username='authorized_user'
        )
        self.unauthorized_user = get_user_model().objects.create(
            username='unauthorized_user'
        )
        create_permissions.Command().handle()
        create_groups.Command().handle()

        self.authorized_user.groups.add(AuthorizedGroup.get_or_create()[0].pk)

        self.factory = RequestFactory()

    def test_authorized_user_has_permission(self):
        self.assertTrue(self.authorized_user.has_perm(RestrictedModelPermission))

    def test_unauthorized_user_does_not_have_permission(self):
        self.assertFalse(self.unauthorized_user.has_perm(RestrictedModelPermission))

    def test_unauthorized_user_accessing_view(self):
        request = self.factory.get('/restricted_view')
        request.user = self.unauthorized_user
        response = restricted_view(request)

        self.assertEqual(response.status_code, 302)

    def test_authorized_user_accessing_view(self):
        request = self.factory.get('/restricted_view')
        request.user = self.authorized_user
        response = restricted_view(request)

        self.assertEqual(response.status_code, 200)

class GlobalLevelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorized_user = get_user_model().objects.create(
            username='authorized_user'
        )
        perm, created_at = GlobalPermission.get_or_create()
        cls.authorized_user.user_permissions.add(perm)

        cls.unauthorized_user = get_user_model().objects.create(
            username='unauthorized_user'
        )

        cls.factory = RequestFactory()

    def test_unauthorized_user_does_not_have_permission(self):
        self.assertFalse(self.unauthorized_user.has_perm(GlobalPermission))

    def test_authorized_user_has_permission(self):
        self.assertTrue(self.authorized_user.has_perm(GlobalPermission))

    def test_unauthorized_user_accessing_view(self):
        request = self.factory.get('/restricted_view')
        request.user = self.unauthorized_user
        response = restricted_view(request)

        self.assertEqual(response.status_code, 302)

    def test_authorized_user_accessing_view(self):
        request = self.factory.get('/restricted_view')
        request.user = self.authorized_user
        response = restricted_view(request)

        self.assertEqual(response.status_code, 200)
