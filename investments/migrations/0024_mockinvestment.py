# Generated by Django 2.2.4 on 2019-11-26 04:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investments', '0023_auto_20191008_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='MockInvestment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('initial_principal', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=14, null=True)),
                ('interest_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=14, null=True)),
                ('time_in_years', models.IntegerField(blank=True, default=0, null=True)),
                ('payment_amount_per_period', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=14, null=True)),
                ('payment_period_in_days', models.IntegerField(choices=[(1, 'Daily'), (7, 'Weekly'), (14, 'Biweekly'), (15, 'Semi-monthly'), (30, 'Monthly'), (365, 'Yearly')], default=12)),
                ('times_compounded_per_year', models.IntegerField(choices=[(365, 'Daily'), (52, 'Weekly'), (26, 'Biweekly'), (24, 'Semi-monthly'), (12, 'Monthly'), (1, 'Yearly')], default=12)),
                ('user', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
