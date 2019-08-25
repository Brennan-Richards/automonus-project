from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *
import uuid
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)


class ModelBaseFields(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        abstract = True


class AccountType(ModelBaseFields):
    pass


class AccountSubType(ModelBaseFields):
    pass


class Currency(models.Model):
    code = models.CharField(max_length=8)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.code)


class Institution(ModelBaseFields):
    plaid_id = models.CharField(max_length=64)
    pass


class UserInstitution(ModelBaseFields):
    institution = models.ForeignKey(Institution, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    # this is needed to retrieve API data for instances related to this institution
    access_token = models.CharField(max_length=64, default=None)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def populate_accounts(self, access_token):
        """The code with getting stripe token:
        stripe_response = client.Processor.stripeBankAccountTokenCreate(access_token, account_id)
        even if it is referenced in the plaid docs.
        Following information in this link https://stripe.com/docs/ach, such token is only needed in case
        of the need to make payments, using that account.
        """
        bank_accounts_data = client.Accounts.get(access_token)
        for account_data in bank_accounts_data["accounts"]:
            account_id = account_data["account_id"]
            type_name = account_data["type"]
            if type_name:
                account_type, created = AccountType.objects.get_or_create(name=type_name)
            else:
                account_type = None
            subtype_name = account_data["subtype"]
            if subtype_name:
                account_subtype, created = AccountSubType.objects.get_or_create(name=subtype_name)
            else:
                account_subtype = None
            currency_code = account_data["balances"]["iso_currency_code"]
            currency, created = Currency.objects.get_or_create(code=currency_code)
            bank_account_defaults_kwargs = {
                "name": account_data["name"],
                "official_name": account_data["official_name"],
                "mask": account_data["mask"],
                "type": account_type,
                "subtype": account_subtype,
                "available_balance": account_data["balances"]["available"] if account_data["balances"]["available"] else 0,
                "current_balance": account_data["balances"]["current"] if account_data["balances"]["current"] else 0,
                "limit_amount": account_data["balances"]["limit"] if account_data["balances"]["limit"] else 0,
                "currency": currency
            }
            """Account information can be updated after initial creation of the instance"""
            Account.objects.update_or_create(user_institution=self, account_id=account_id,
                                             **bank_account_defaults_kwargs)


class Account(models.Model):
    # initial information from frontend
    user_institution = models.ForeignKey(UserInstitution, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account_id = models.CharField(max_length=64, blank=True, null=True, default=None)
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
    is_active = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.user_institution and self.user_institution.user and self.name and self.type:
            return "{}: {} ({})".format(self.user_institution.user.username, self.name, self.type.name)
        else:
            return "{}".format(self.id)