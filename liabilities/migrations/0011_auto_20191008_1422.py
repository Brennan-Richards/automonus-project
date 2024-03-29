# Generated by Django 2.2.4 on 2019-10-08 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liabilities', '0010_auto_20191008_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcardsnapshot',
            name='credit_limit',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='creditcardsnapshot',
            name='late_fee_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
    ]
