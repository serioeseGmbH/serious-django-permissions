from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from serious_django_permissions.management.commands import create_permissions, create_groups
from serious_django_permissions.helpers import setup_permissions

from .permissions import RestrictedModelPermission, GlobalPermission,\
    ExplicitReferenceToRestrictedModelPermission
from .groups import AuthorizedGroup, AuthorizedGlobalPermissionGroup
from .views import restricted_model_view, restricted_global_view,\
    restricted_model_with_explicit_reference_view


class ManageFunctionTests(TestCase):

    def test_create_user_permissions(self):
        perm = Permission.objects.filter(codename=RestrictedModelPermission.codename)
        self.assertFalse(perm, 'The permission should not exist yet, but it does.')

        create_permissions.Command().handle()

        perm = Permission.objects.filter(codename=RestrictedModelPermission.codename)
        self.assertTrue(perm, 'The permission should exist, but it doesnt.')

    def test_create_explicit_referencing_permissions(self):
        perm = Permission.objects.filter(codename=ExplicitReferenceToRestrictedModelPermission.codename)
        self.assertFalse(perm, 'The permission should not exist yet, but it does.')

        create_permissions.Command().handle()

        perm = Permission.objects.filter(codename=ExplicitReferenceToRestrictedModelPermission.codename)
        self.assertTrue(perm, 'The permission should exist, but it doesnt.')

    def test_create_group_permissions(self):
        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertFalse(perm, 'The group should not exist yet, but it does.')

        create_groups.Command().handle()

        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertTrue(perm, 'The group should exist, but it doesnt.')

    def test_create_global_permission(self):
        perm = Permission.objects.filter(codename=GlobalPermission.codename)
        self.assertFalse(perm, 'The permission should not exist yet, but it does.')

        create_permissions.Command().handle()

        perm = Permission.objects.filter(codename=GlobalPermission.codename)
        self.assertTrue(perm, 'The permission should exist, but it doesnt.')

    def test_missing_default_group(self):
        del settings.DEFAULT_GROUPS_MODULE

        with self.assertRaises(AttributeError) as e:
            create_groups.Command().handle()
        self.assertIn("DEFAULT_GROUPS_MODULE setting is not set!",
            str(e.exception)
        )

        # Restore DEFAULT_GROUPS_MODULE setting
        settings.DEFAULT_GROUPS_MODULE = 'test_app.groups'

    def test_invalid_default_group(self):
        settings.DEFAULT_GROUPS_MODULE = None

        with self.assertRaises(AttributeError) as e:
            create_groups.Command().handle()
        self.assertIn("DEFAULT_GROUPS_MODULE setting is not set!",
            str(e.exception)
        )

        # Restore DEFAULT_GROUPS_MODULE setting
        settings.DEFAULT_GROUPS_MODULE = 'test_app.groups'

    def test_global_permission_manager(self):
        from serious_django_permissions.models import GlobalPermission
        create_permissions.Command().handle()
        query = GlobalPermission.objects.get_queryset()

        for item in query:
            self.assertTrue(isinstance(item, GlobalPermission))

    def test_setup_permissions_helper(self):
        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertFalse(perm, 'The group should not exist yet, but it does.')

        setup_permissions()

        perm = Group.objects.filter(name=AuthorizedGroup.group_name)
        self.assertTrue(perm, 'The group should exist, but it doesnt.')


class UserLevelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.authorized_user = get_user_model().objects.create(
            username='authorized_user'
        )
        cls.authorized_user_explicit = get_user_model().objects.create(
            username='authorized_user_explicit'
        )
        perm, created_at = RestrictedModelPermission.get_or_create()
        cls.authorized_user.user_permissions.add(perm)
        explicit_perm, created_at = ExplicitReferenceToRestrictedModelPermission.get_or_create()
        cls.authorized_user_explicit.user_permissions.add(explicit_perm)

        cls.unauthorized_user = get_user_model().objects.create(
            username='unauthorized_user'
        )

        cls.factory = RequestFactory()

    def test_unauthorized_user_does_not_have_permission(self):
        self.assertFalse(self.unauthorized_user.has_perm(RestrictedModelPermission))
        self.assertFalse(RestrictedModelPermission.user_has_perm(self.unauthorized_user))

    def test_authorized_users_have_permission(self):
        self.assertTrue(self.authorized_user.has_perm(RestrictedModelPermission))
        self.assertTrue(RestrictedModelPermission.user_has_perm(self.authorized_user))
        self.assertTrue(self.authorized_user_explicit.has_perm(ExplicitReferenceToRestrictedModelPermission))
        self.assertTrue(ExplicitReferenceToRestrictedModelPermission.user_has_perm(self.authorized_user_explicit))

    def test_unauthorized_user_accessing_view(self):
        request = self.factory.get('/restricted-model-view')
        request.user = self.unauthorized_user
        response = restricted_model_view(request)

        self.assertEqual(response.status_code, 302)

    def test_authorized_users_accessing_view(self):
        request = self.factory.get('/restricted-model-view')
        request.user = self.authorized_user
        response = restricted_model_view(request)

        self.assertEqual(response.status_code, 200)

    def test_authorized_users_accessing_view_with_explicit_reference(self):
        request = self.factory.get('/restricted-model-view-explicit')
        request.user = self.authorized_user_explicit
        response = restricted_model_with_explicit_reference_view(request)

        self.assertEqual(response.status_code, 200)

    def test_invalid_permission_name(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            from .permissions_invalid_name import InvalidName
        self.assertIn("must end with 'Permission'.",
            str(e.exception)
        )

    def test_missing_description(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            from .permissions_missing_description import MissingDPermission
        self.assertIn("must have a 'description' attribute.",
            str(e.exception)
        )


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
        request = self.factory.get('/restricted-model-view')
        request.user = self.unauthorized_user
        response = restricted_model_view(request)

        self.assertEqual(response.status_code, 302)

    def test_authorized_user_accessing_view(self):
        request = self.factory.get('/restricted-model-view')
        request.user = self.authorized_user
        response = restricted_model_view(request)

        self.assertEqual(response.status_code, 200)

    def test_invalid_group_name(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            from .groups_invalid_name import InvalidName
        self.assertIn("must end with 'Group'.",
            str(e.exception)
        )

    def test_missing_permissions(self):
        with self.assertRaises(ImproperlyConfigured) as e:
            from .groups_missing_permissions import MissingPermissionsGroup
        self.assertIn("A Group class must have a 'permissions' attribute",
            str(e.exception)
        )

    def test_global_permission_via_group(self):
        self.authorized_user.groups.add(AuthorizedGlobalPermissionGroup.get_or_create()[0].pk)
        self.assertTrue(self.authorized_user.has_perm(GlobalPermission))


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
        request = self.factory.get('/restricted-global-view')
        request.user = self.unauthorized_user
        response = restricted_global_view(request)

        self.assertEqual(response.status_code, 302)

    def test_authorized_user_accessing_view(self):
        request = self.factory.get('/restricted-global-view')
        request.user = self.authorized_user
        response = restricted_global_view(request)

        self.assertEqual(response.status_code, 200)


class ObjectBasedPermissionsTests(TestCase):
    @classmethod
    def setUp(self):
        self.authorized_user = get_user_model().objects.create(
            username='authorized_user'
        )
        RestrictedModelPermission.get_or_create()  # create the permission in the DB

    def test_object_based_permissions_work_as_intended(self):
        from guardian.shortcuts import assign_perm
        from .models import RestrictedModel

        model_instance_a = RestrictedModel.objects.create()
        model_instance_b = RestrictedModel.objects.create()
        assign_perm(RestrictedModelPermission, self.authorized_user, model_instance_a)

        self.assertTrue(
            self.authorized_user.has_perm(
                RestrictedModelPermission,
                obj=model_instance_a
            )
        )
        self.assertFalse(
            self.authorized_user.has_perm(
                RestrictedModelPermission,
                obj=model_instance_b
            )
        )
