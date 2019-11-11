# Generated by Django 2.2.4 on 2019-11-09 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenditures', '0003_auto_20191109_0055'),
    ]

    operations = [
        migrations.AddField(
            model_name='customexpense',
            name='annual_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='customexpense',
            name='biweekly_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='customexpense',
            name='cost_per_pay_period',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='customexpense',
            name='daily_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='customexpense',
            name='monthly_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='customexpense',
            name='semimonthly_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name='customexpense',
            name='weekly_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=18, null=True),
        ),
    ]
