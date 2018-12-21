===========================
Serious Django: Permissions
===========================

https://github.com/serioeseGmbH/serious-django-permissions

serious-django-permissions is a Django extension that makes it possible to define Permissions in each app,
and Groups in a central place. It makes these Permissions ``import``-able and checkable via ``user.has_perm``::

    from some_app.permissions import ChangeSomethingPermission

    def change_something(something, user):
        if not user.has_perm(ChangeSomethingPermission):
            raise PermissionDenied("You can't change this something.)
        else:
	    return something.change()

Both permissions and groups can then be created in the database with a single ``manage.py`` call (see Quick start below).


Quick start
-----------

1. Install the package with pip::

    pip install serious-django-permissions

2. Add "serious_django_permissions" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'serious_django_permissions',
    ]

3. Add ``serious_django_permissions.PermissionModelBackend`` to your ``AUTHENTICATION_BACKENDS`` setting. This enables you to do permission checks like ``user.has_perm(SomePermission)``::

    AUTHENTICATION_BACKENDS = [
        ...
        'serious_django_permissions.PermissionModelBackend',
    ]

4. In each app that should define a permission, import ``serious_django_permissions.Permission`` and create subclasses of it.

   The name of your subclasses must end in ``Permission``, and each subclass must define a ``description`` attribute. For instance, let's say you have the file ``myapp/permissions.py``::

     from serious_django_permissions import Permission

     class MyPermission(Permission):
         model = 'MyModel' # should be a model inside myapp.models, or not defined for global permissions.
	 description = 'A description for this permission'

5. Run ``python manage.py create_permissions`` to create all defined permissions on the database level.

6. If you'd like to use the Groups feature as well:

   1. Create a file named something like ``some_app/groups.py`` inside one of your apps, or in the folder where your settings live. An example::

	from serious_django_permissions import Group

	from app_one.permissions import\
	    AppOnePermissionA, AppOnePermissionB
	from app_two.permissions import\
	    AppTwoPermission

	class GroupA(Group):
	    permissions = [
		AppOnePermissionA,
		AppTwoPermission
	    ]

	class GroupB(Group):
	    permissions = [
	        AppOnePermissionB,
		AppTwoPermission
	    ]

   2. Reference the defined groups file in your settings::

	DEFAULT_GROUPS_MODULE = 'some_app.groups'

   3. Run ``python manage.py create_groups`` to create all permissions and assign them to the groups.
