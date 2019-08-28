from django.db import models
from django.contrib.auth.models import User
import uuid
from institutions.models import UserInstitution
from accounts.models import Currency, ModelBaseFieldsAbstract

# Create your models here.

class Investments(models.Model):

    name = "Investments"

    def __str__(self):
        return self.name

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    total_securities_value = models.DecimalField(max_digits=11, decimal_places=2, default=0)


class SecurityType(ModelBaseFieldsAbstract):
    pass


class Security(models.Model):
    user_institution = models.ForeignKey(UserInstitution, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    plaid_id = models.CharField(max_length=38)
    isin = models.CharField(max_length=38, blank=True, null=True, default=None)
    sedol = models.CharField(max_length=38, blank=True, null=True, default=None)
    cusip = models.CharField(max_length=38, blank=True, null=True, default=None)
    ticker_symbol = models.CharField(max_length=12, blank=True, null=True, default=None)
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    is_cash_equivalent = models.BooleanField(default=False)
    type = models.ForeignKey(SecurityType, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    close_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    close_price_as_of = models.DateField(blank=True, null=True, default=None)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.name:
            return "{}".format(self.name)
        else:
            return "{}".format(self.id)


class Holding(models.Model):
    user_institution = models.ForeignKey(UserInstitution, blank=True, null=True, default=None,
                                         on_delete=models.SET_NULL)
    plaid_id = models.CharField(max_length=38)
    institution_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    institution_price_as_of = models.DateField(blank=True, null=True, default=None)
    institution_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cost_basis = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.id)