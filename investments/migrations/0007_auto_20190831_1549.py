# Generated by Django 2.2.4 on 2019-08-31 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0006_auto_20190831_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='Security',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('ticker_symbol', models.CharField(blank=True, default=None, max_length=12, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='usersecurity',
            name='name',
        ),
        migrations.RemoveField(
            model_name='usersecurity',
            name='ticker_symbol',
        ),
        migrations.AddField(
            model_name='usersecurity',
            name='security',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.Security'),
        ),
    ]
