# Generated by Django 2.1.2 on 2018-10-16 22:27

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalPermission',
            fields=[
            ],
            options={
                'indexes': [],
                'proxy': True,
            },
            bases=('auth.permission',),
        ),
    ]
