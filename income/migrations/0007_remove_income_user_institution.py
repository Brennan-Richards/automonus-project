# Generated by Django 2.2.4 on 2019-08-27 08:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0006_auto_20190825_2217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='income',
            name='user_institution',
        ),
    ]