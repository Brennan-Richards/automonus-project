# Generated by Django 2.2.4 on 2019-08-21 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expensetracker', '0002_auto_20190820_0351'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expenditures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('housing', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('utilities', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('transportation', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('food', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('clothing', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('insurance', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='display',
            name='user',
        ),
        migrations.RemoveField(
            model_name='food',
            name='user',
        ),
        migrations.RemoveField(
            model_name='housing',
            name='user',
        ),
        migrations.RemoveField(
            model_name='income',
            name='user',
        ),
        migrations.RemoveField(
            model_name='miscellaneous',
            name='user',
        ),
        migrations.RemoveField(
            model_name='tax',
            name='user',
        ),
        migrations.RemoveField(
            model_name='utilities',
            name='user',
        ),
        migrations.DeleteModel(
            name='Car',
        ),
        migrations.DeleteModel(
            name='Display',
        ),
        migrations.DeleteModel(
            name='Food',
        ),
        migrations.DeleteModel(
            name='Housing',
        ),
        migrations.DeleteModel(
            name='Income',
        ),
        migrations.DeleteModel(
            name='Miscellaneous',
        ),
        migrations.DeleteModel(
            name='Tax',
        ),
        migrations.DeleteModel(
            name='Utilities',
        ),
    ]
