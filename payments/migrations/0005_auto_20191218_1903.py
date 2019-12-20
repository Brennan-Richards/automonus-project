# Generated by Django 2.2.4 on 2019-12-18 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_remove_bill_pay_to_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='billdestination',
            name='biller_name',
            field=models.CharField(default=None, max_length=128),
        ),
        migrations.AlterField(
            model_name='bill',
            name='bill_destination',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to='payments.BillDestination'),
        ),
        migrations.AlterField(
            model_name='billdestination',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
