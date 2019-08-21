from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Income(models.Model):

    name = "Savings"

    def __str__(self):
        return self.NAME

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    total_income = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    income_after_tax = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    cost_of_tax = models.DecimalField(max_digits=11, decimal_places=2, default=0)
