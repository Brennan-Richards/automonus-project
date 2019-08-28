from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Debts(models.Model):

    name = "Debts"

    def __str__(self):
        return self.name

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    outstanding_amount_principle = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    outstanding_amount_interest = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    minimum_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    last_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)


class DebtAverages(models.Model):

    average_payment_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
