# Generated by Django 2.2.3 on 2019-08-17 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expensetracker', '0008_tax_filing_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='tax',
            name='annual_federal_tax',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tax',
            name='annual_state_tax',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tax',
            name='fica',
            field=models.IntegerField(default=0),
        ),
    ]