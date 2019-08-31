# Generated by Django 2.2.4 on 2019-08-31 14:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_transactioncategory_plaid_id'),
        ('institutions', '0002_userinstitution_plaid_id'),
        ('investments', '0007_auto_20190831_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution_price', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('institution_price_as_of', models.DateField(blank=True, default=None, null=True)),
                ('institution_value', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('cost_basis', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('currency', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.Currency')),
            ],
        ),
        migrations.RemoveField(
            model_name='userholding',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='userholding',
            name='security_item',
        ),
        migrations.RemoveField(
            model_name='investmenttransaction',
            name='security_item',
        ),
        migrations.RemoveField(
            model_name='usersecurity',
            name='security_item',
        ),
        migrations.AddField(
            model_name='investmenttransaction',
            name='user_security',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.UserSecurity'),
        ),
        migrations.AddField(
            model_name='usersecurity',
            name='plaid_id',
            field=models.CharField(blank=True, default=None, max_length=38, null=True),
        ),
        migrations.AddField(
            model_name='usersecurity',
            name='user_institution',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='institutions.UserInstitution'),
        ),
        migrations.DeleteModel(
            name='SecurityItem',
        ),
        migrations.DeleteModel(
            name='UserHolding',
        ),
        migrations.AddField(
            model_name='holding',
            name='user_security',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='investments.UserSecurity'),
        ),
    ]