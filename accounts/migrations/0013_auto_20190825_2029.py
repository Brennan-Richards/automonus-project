# Generated by Django 2.2.4 on 2019-08-25 17:29

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0012_auto_20190825_2027'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='InstitutionUser',
            new_name='UserInstitution',
        ),
        migrations.RenameField(
            model_name='account',
            old_name='institution',
            new_name='user_institution',
        ),
    ]
