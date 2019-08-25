from django.db import models
from django.contrib.auth.models import User
import uuid
from accounts.models import UserInstitution


class Income(models.Model):
    user_institution = models.ForeignKey(UserInstitution, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    max_number_of_overlapping_income_streams = models.IntegerField(default=0)
    number_of_income_streams = models.IntegerField(default=0)

    last_year_income_before_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_year_income_minus_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    last_year_taxes = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    projected_yearly_income_before_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    projected_yearly_minus_tax = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    projected_yearly_taxes = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.id)

    def save(self, *args, **kwargs):
        self.last_year_taxes = round(self.last_year_income_before_tax - self.last_year_income_minus_tax, 2)
        self.projected_yearly_taxes = round(self.projected_yearly_income_before_tax - self.projected_yearly_minus_tax, 2)
        super(Income, self).save(*args, **kwargs)


class IncomeStream(models.Model):
    income = models.ForeignKey(Income, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    confidence = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    days = models.IntegerField(default=0)
    monthly_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.income.user_institution and self.income.user_institution.user and self.name:
            return "{}: {}".format(self.income.user_institution.user.username, self.name)
        elif self.name:
            return "{}".format(self.name)
        else:
            return "{}".format(self.id)
