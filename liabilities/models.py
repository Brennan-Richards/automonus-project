from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
import uuid

# Create your models here.

class StudentLoan(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account_number = models.CharField(max_length=32, blank=True, null=True, default=None)
    expected_payoff_date = models.DateField(blank=True, null=True, default=None)
    guarantor = models.CharField(max_length=128, blank=True, null=True, default=None)
    interest_rate_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_overdue = models.BooleanField(default=False)
    last_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_payment_date = models.DateField(blank=True, null=True, default=None)
    last_statement_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_statement_issue_date = models.DateField(blank=True, null=True, default=None)
    loan_name = models.CharField(max_length=128, blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True, default=None)
    type = models.CharField(max_length=64, blank=True, null=True, default=None)
    minimum_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    next_payment_due_date = models.DateField(blank=True, null=True, default=None)
    origination_date = models.DateField(blank=True, null=True, default=None)
    origination_principal_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    outstanding_interest_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    payment_reference_number = models.CharField(max_length=64, blank=True, null=True, default=None)
    estimated_pslf_eligibility_date = models.DateField(blank=True, null=True, default=None)
    payments_made = models.IntegerField(default=0)
    pslf_payments_remaining = models.IntegerField(default=0)
    repayment_description = models.CharField(max_length=64, blank=True, null=True, default=None)
    repayment_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    sequence_number = models.IntegerField(default=0)
    ytd_interest_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    ytd_principal_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user_institution.user.username, self.guarantor)

class DisbursementDate(models.Model):
    loan_instance = models.ForeignKey(StudentLoan, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    date_of_disbursement = models.DateField(blank=True, null=True, default=None)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.loan_instance)

class ServicerAddress(models.Model):
    loan_instance = models.ForeignKey(StudentLoan, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    city = models.CharField(max_length=64, blank=True, null=True, default=None)
    country = models.CharField(max_length=64, blank=True, null=True, default=None)
    postal_code = models.CharField(max_length=10, blank=True, null=True, default=None)
    region = models.CharField(max_length=2, blank=True, null=True, default=None)
    street = models.CharField(max_length=128, blank=True, null=True, default=None)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.loan_instance)

class CreditCard(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_overdue = models.BooleanField(default=False)
    last_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_payment_date = models.DateField(blank=True, null=True, default=None)
    last_statement_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    last_statement_issue_date = models.DateField(blank=True, null=True, default=None)
    late_fee_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    minimum_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    next_payment_due_date = models.DateField(blank=True, null=True, default=None)
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user_institution.user.username, self.user_institution.institution)

class APR(models.Model):
    credit_card = models.ForeignKey(CreditCard, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    apr_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    apr_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    balance_subject_to_apr = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    interest_charge_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.credit_card)
