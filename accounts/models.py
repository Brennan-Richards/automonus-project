from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *

# Create your models here.

class Item(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    token = models.CharField(max_length=200)

    def create_account_item(self, token, active_user):
        account = self.create(token=token, user=active_user)
