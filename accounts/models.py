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
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
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