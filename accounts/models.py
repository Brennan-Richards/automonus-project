from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *
import uuid
from django.utils import timezone
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)


class ModelBaseFieldsAbstract(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        abstract = True


class AccountType(ModelBaseFieldsAbstract):
    pass


class AccountSubType(ModelBaseFieldsAbstract):
    pass


class Currency(models.Model):
    code = models.CharField(max_length=8)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.code)


class Account(models.Model):
    # initial information from frontend
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='accounts_user_institution')
    account_id = models.CharField(max_length=64, blank=True, null=True, default=None)
    stripe_bank_account_token = models.CharField(max_length=128, blank=True, null=True, default=None)
    # additional information, which is triggered by the API for account_id
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    official_name = models.CharField(max_length=256, blank=True, null=True, default=None)
    mask = models.CharField(max_length=16, blank=True, null=True, default=None)
    type = models.ForeignKey(AccountType, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    subtype = models.ForeignKey(AccountSubType, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    available_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    limit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.user_institution and self.user_institution and self.user_institution.user and self.name and self.type:
            return "Id {}. {} {}: {} ({})".format(self.id, self.user_institution.institution.name, self.user_institution.user.username,
                                           self.name, self.type.name)
        else:
            return "{}".format(self.id)

    def create_account_snapshot(self):
        available_balance = self.available_balance
        current_balance = self.current_balance
        limit_amount = self.limit_amount
        current_date = timezone.now().date()
        AccountSnapshot.objects.get_or_create(account=self, date=current_date, defaults={"available_balance": available_balance,
                                                        "current_balance": current_balance, "limit_amount": limit_amount
                                                        })


class AccountNumber(ModelBaseFieldsAbstract):
    ACH = 'ach'

    NUMBER_TYPES = (
        (ACH, 'ACH'),
    )

    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='accounts_number_to_account')
    number_type = models.CharField(max_length=128, choices=NUMBER_TYPES, blank=True, null=True, default=None)
    number_id = models.CharField(max_length=128, blank=True, null=True, default=None)
    number_routing = models.CharField(max_length=128, blank=True, null=True, default=None)

    def __str__(self):
        return f'{self.account}'

class TransactionCategory(models.Model):
    plaid_category_id = models.CharField(max_length=38, default=None)
    group = models.CharField(max_length=32, default=None)
    sub_category_1 = models.CharField(max_length=64, default=None)
    sub_category_2 = models.CharField(max_length=64, blank=True, null=True, default=None)
    sub_category_3 = models.CharField(max_length=64, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "ID:{} - {}".format(self.plaid_category_id, self.sub_category_1)

class Transaction(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    name = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    date = models.DateField()
    category = models.ForeignKey(TransactionCategory, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    plaid_id = models.CharField(max_length=38)
    is_pending = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.name:
            return "{}: {}{}".format(self.name, self.amount, self.currency.code)
        else:
            return "{}: {}{} ".format(self.id, self.amount, self.currency.code)


class AccountSnapshot(models.Model):
    """savings, investments and debts"""
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    available_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    limit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.account:
            return "{}".format(self.account.id)
        else:
            return "{}".format(self.id)
