# Generated by Django 2.2.4 on 2019-08-25 15:02

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0003_auto_20190825_1800'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Account',
            new_name='BankAccount',
        ),
    ]