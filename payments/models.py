from django.db import models
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