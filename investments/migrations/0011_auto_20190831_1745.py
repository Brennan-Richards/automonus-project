# Generated by Django 2.2.4 on 2019-08-31 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0010_auto_20190831_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersecurity',
            name='close_price',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=16),
        ),
    ]
