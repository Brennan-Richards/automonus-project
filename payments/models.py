from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Account
import uuid
# Create your models here.
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

class PaymentOrder(ModelBaseFieldsAbstract):
    from_account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='payment_order_from_account')
    to_account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='payment_order_to_account')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tx_id = models.CharField(max_length=64, blank=True, null=True, default=None)
    customer = models.CharField(max_length=64, blank=True, null=True, default=None)
    destination = models.CharField(max_length=64, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    status = models.CharField(max_length=64, blank=True, null=True, default=None)

    def __str__(self):
        return "{}".format(self.amount)

class MockSubscription(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    # accounts_for_payments = models.IntegerField(default=0, blank=True, null=True)
    institutions_for_investments = models.IntegerField(default=0, blank=True, null=True)
    institutions_for_liabilities = models.IntegerField(default=0, blank=True, null=True)

    def calculate_subscription_cost(self):
        """ My cost per product:
            Investments, transactions: $0.35 (per user/month),
            Liabilities: $0.20 (per user/month),
            Auth: $1.25/account
        """
        institutions_for_investments = self.institutions_for_investments
        institutions_for_liabilities = self.institutions_for_liabilities #Credit Cards or Student Loans

        auth_cost = 1.25
        investments_cost = 0.35 * institutions_for_investments
        liabilities_cost = 0.30 * institutions_for_liabilities

        monthly_operational_cost = auth_cost + investments_cost + liabilities_cost

        return monthly_operational_cost

    # def get_absolute_url(self):
    #     return reverse('subscription-cost-view', kwargs={'user': self.user})

class Subscription(ModelBaseFieldsAbstract):
    user = models.OneToOneField(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    auto_renew = models.BooleanField(default=False)
