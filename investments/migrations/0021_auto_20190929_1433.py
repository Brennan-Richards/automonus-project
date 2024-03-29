# Generated by Django 2.2.4 on 2019-09-29 14:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_accountsnapshot_date'),
        ('investments', '0020_usersecuritysnapshot_user_security'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersecuritysnapshot',
            name='date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='usersecuritysnapshot',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='HoldingSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_price', models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ('institution_price_as_of', models.DateField(blank=True, default=None, null=True)),
                ('institution_value', models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ('cost_basis', models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ('quantity', models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('date', models.DateField(default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Account')),
                ('currency', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Currency')),
                ('holding', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.Holding')),
                ('user_security', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.UserSecurity')),
            ],
        ),
    ]
