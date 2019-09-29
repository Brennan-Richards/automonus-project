# Generated by Django 2.2.4 on 2019-09-29 13:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0002_userinstitution_plaid_id'),
        ('accounts', '0022_accountsnapshot_date'),
        ('investments', '0018_auto_20190831_2044'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSecuritySnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_cash_equivalent', models.BooleanField(default=False)),
                ('close_price', models.DecimalField(decimal_places=4, default=0, max_digits=16)),
                ('close_price_as_of', models.DateField(blank=True, default=None, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('currency', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Currency')),
                ('security', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.Security')),
                ('type', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.SecurityType')),
                ('user_institution', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='institutions.UserInstitution')),
            ],
        ),
    ]
