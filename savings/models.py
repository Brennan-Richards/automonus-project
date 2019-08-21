from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Savings(models.Model):

    name = "Savings"

    def __str__(self):
        return self.name

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    balance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
