# Generated by Django 2.2.4 on 2019-12-18 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_auto_20191218_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billdestination',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='paymentorder',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
    ]