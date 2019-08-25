from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *

# Create your models here.

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


class ExpenseAverages(models.Model):
    monthly_average_housing = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    monthly_average_utilities = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    monthly_average_transportation = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    monthly_average_food = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    monthly_average_clothing = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    monthly_average_insurance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    monthly_average_other = models.DecimalField(max_digits=11, decimal_places=2, default=0)
