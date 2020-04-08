# Generated by Django 2.2.4 on 2020-04-07 11:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investments', '0024_mockinvestment'),
    ]

    operations = [
        migrations.CreateModel(
            name='TylersAdjustment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('is_active', models.BooleanField(default=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('adjustment', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
