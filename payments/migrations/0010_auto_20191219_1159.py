# Generated by Django 2.2.4 on 2019-12-19 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_auto_20191218_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='bill_destination',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.BillDestination'),
        ),
    ]
