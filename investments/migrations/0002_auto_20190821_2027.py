# Generated by Django 2.2 on 2019-08-21 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investments',
            old_name='investment_value',
            new_name='total_securities_value',
        ),
    ]