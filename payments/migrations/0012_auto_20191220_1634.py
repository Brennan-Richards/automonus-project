# Generated by Django 2.2.4 on 2019-12-20 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0011_auto_20191219_2114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billdestination',
            name='user',
        ),
        migrations.DeleteModel(
            name='Bill',
        ),
        migrations.DeleteModel(
            name='BillDestination',
        ),
    ]
