from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *

# Create your models here.


#METHOD - Computes the yearly total of any expense field regardless of the pay period.
def calc_yearly_total(expense, expense_period_choice):

    yearly_total = 0

    if expense_period_choice == 'Daily':
        yearly_total = expense * 365
    elif expense_period_choice == 'Weekly':
        yearly_total = expense * 52
    elif expense_period_choice == 'Monthly':
        yearly_total = expense * 12
    else:
        yearly_total = expense

    return round(yearly_total,2)

class Expenditures(models.Model):

    name = "Expenditures"

    def __str__(self):
        return self.name

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    housing = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    utilities = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    transportation = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    food = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    clothing = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    insurance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    other = models.DecimalField(max_digits=11, decimal_places=2, default=0)
