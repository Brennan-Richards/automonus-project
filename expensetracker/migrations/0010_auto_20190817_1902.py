# Generated by Django 2.2.3 on 2019-08-17 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expensetracker', '0009_auto_20190817_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='tax',
            name='pay_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AddField(
            model_name='tax',
            name='periods',
            field=models.IntegerField(choices=[(365, 'Daily'), (52, 'Weekly'), (24, 'Semi-monthly'), (26, 'Biweekly'), (12, 'Monthly'), (1, 'Yearly')], default=52),
        ),
        migrations.AlterField(
            model_name='car',
            name='car_insurance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='car',
            name='car_property_tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='car',
            name='gas',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='car',
            name='maintenance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='food',
            name='groceries',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='food',
            name='restaurant_food_costs',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='housing',
            name='fire_tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='housing',
            name='home_property_tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='housing',
            name='homeowners_insurance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='housing',
            name='mortgage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='income',
            name='salary',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='miscellaneous',
            name='clothing',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='miscellaneous',
            name='health_insurance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='miscellaneous',
            name='life_insurance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='utilities',
            name='cable',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='utilities',
            name='electricity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='utilities',
            name='heating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='utilities',
            name='internet',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='utilities',
            name='phone',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
        migrations.AlterField(
            model_name='utilities',
            name='water',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=11),
        ),
    ]
