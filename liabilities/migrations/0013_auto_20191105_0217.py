# Generated by Django 2.2.4 on 2019-11-05 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('liabilities', '0012_auto_20191008_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apr',
            name='credit_card',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='liabilities.CreditCard'),
        ),
    ]