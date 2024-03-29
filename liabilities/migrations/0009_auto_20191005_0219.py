# Generated by Django 2.2.4 on 2019-10-05 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liabilities', '0008_creditcardsnapshot_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcard',
            name='credit_limit',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=18),
        ),
        migrations.AlterField(
            model_name='creditcard',
            name='late_fee_amount',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=18),
        ),
    ]
