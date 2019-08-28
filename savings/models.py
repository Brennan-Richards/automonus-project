from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Savings(models.Model):

    name = "Savings"

    def __str__(self):
        return self.name

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    total_current_funds = models.DecimalField(max_digits=11, decimal_places=2, default=0) #total += savings.accounts.account_total

class Accounts(models.Model):

    account_total = models.DecimalField(max_digits=11, decimal_places=2, default=0)
