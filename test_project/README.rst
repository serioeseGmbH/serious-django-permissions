===========================
test_project
===========================

This is an example project to test the serious-django-permissions app.

Run the tests locally
---------------------
1. Install serious-django-permissions from the above directory: Run `pip install -e .` while you are in the `serious-django-permissions` directory.
2. Run the tests via `python test_project/manage.py test test_project`

Run tests locally and create a coverage report
----------------------------------------------
1. `pip install coverage <https://pypi.org/project/coverage/>`_
2. coverage run --source='.' test_project/manage.py test test_project
3. coverage report -m
