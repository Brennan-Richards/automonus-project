from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Income(models.Model):

    name = "Savings"

    def __str__(self):
        return self.NAME

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projected_yearly_income = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    projected_yearly_minus_tax = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    # cost_of_taxes_paid = cost_of_taxes(self)

    def cost_of_taxes(self):

        return round(self.projected_yearly_income - self.projected_yearly_minus_tax, 2)
