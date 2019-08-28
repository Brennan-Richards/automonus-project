# Generated by Django 2.2 on 2019-08-27 13:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Utilities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('electricity', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('heating', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('phone', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('cable', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('internet', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('water', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('annual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('electricity_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('heating_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('phone_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('cable_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('internet_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('water_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dependents', models.IntegerField()),
                ('state', models.CharField(max_length=2)),
                ('pay_rate', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('fica', models.IntegerField(default=0)),
                ('annual_state_tax', models.IntegerField(default=0)),
                ('annual_federal_tax', models.IntegerField(default=0)),
                ('filing_status', models.CharField(choices=[('single', 'Single'), ('married', 'Married'), ('married_separately', 'Married Separately'), ('head_of_household', 'Head of Household')], default='single', max_length=20)),
                ('periods', models.IntegerField(choices=[(365, 'Daily'), (52, 'Weekly'), (24, 'Semi-monthly'), (26, 'Biweekly'), (12, 'Monthly'), (1, 'Yearly')], default=52)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Miscellaneous',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('health_insurance', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('life_insurance', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('clothing', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('annual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('healthinsurance_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Weekly', max_length=7)),
                ('lifeinsurance_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Weekly', max_length=7)),
                ('clothing_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Weekly', max_length=7)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('paycheck_period', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Biweekly', 'Biweekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Weekly', max_length=7)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Housing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mortgage', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('home_property_tax', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('fire_tax', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('homeowners_insurance', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('annual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('mortgage_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Monthly', max_length=7)),
                ('homeproptax_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('firetax_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('homeinsurance_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Monthly', max_length=7)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groceries', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('restaurant_food_costs', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('annual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('groceries_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Weekly', max_length=7)),
                ('restaurant_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Weekly', max_length=7)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Display',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display', models.CharField(choices=[('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year')], default='year', max_length=5)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gas', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('car_mpg', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('maintenance', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('car_insurance', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('car_property_tax', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('miles_driven', models.IntegerField(default=0)),
                ('annual_cost', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('miles_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('maintenance_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('carinsurance_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Monthly', max_length=7)),
                ('carproptax_pay_per', models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Yearly', max_length=7)),
                ('user', models.OneToOneField(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]