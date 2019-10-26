from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
import uuid
from django.utils import timezone
from datetime import datetime, date
from django.forms.models import model_to_dict
# Create your models here.

class StudentLoan(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account_number = models.CharField(max_length=32, blank=True, null=True, default=None)
    expected_payoff_date = models.DateField(blank=True, null=True, default=None)
    guarantor = models.CharField(max_length=128, blank=True, null=True, default=None)
    interest_rate_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_overdue = models.BooleanField(default=False, blank=True, null=True)
    last_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True, default=None)
    last_statement_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_statement_issue_date = models.DateField(blank=True, null=True, default=None)
    loan_name = models.CharField(max_length=128, blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True, default=None)
    type = models.CharField(max_length=64, blank=True, null=True, default=None)
    minimum_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    next_payment_due_date = models.DateField(blank=True, null=True, default=None)
    origination_date = models.DateField(blank=True, null=True, default=None)
    origination_principal_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    outstanding_interest_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    payment_reference_number = models.CharField(max_length=64, blank=True, null=True, default=None)
    estimated_pslf_eligibility_date = models.DateField(blank=True, null=True, default=None)
    payments_made = models.IntegerField(default=0, blank=True, null=True)
    pslf_payments_remaining = models.IntegerField(default=0, blank=True, null=True)
    repayment_description = models.CharField(max_length=64, blank=True, null=True, default=None)
    repayment_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    sequence_number = models.IntegerField(default=0, blank=True, null=True)
    ytd_interest_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    ytd_principal_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user_institution.user.username, self.guarantor)

    def get_payments_per_year(self):
        if self.next_payment_due_date and self.last_statement_issue_date:
            timedelta = self.next_payment_due_date - self.last_statement_issue_date
        #print(timedelta)
        if timedelta.days >= 28: #monthly
            payments_per_year = 12
        elif timedelta.days == 14: #biweekly
            payments_per_year = 26
        elif timedelta.days == 7: #weekly
            payments_per_year = 52
        elif timedelta.days == 1: #daily
            payments_per_year = 365
        #print(period)

        return payments_per_year

    # def get_current_balance(self):
    #     #get number of months between end date and now (a.k.a number of payments)
    #     remaining_loan_term = date(self.end_date).days - date(self.last_statement_issue_date).days #returns remaining term of loan
    #     payment_period = self.get_payment_period()
    #     print(remaining_loan_term)
    #     remaining_years_loan_term = remaining_loan_term / 12
    #     print(remaining_years_loan_term)
    #     if payment_period == "month":
    #         remaining_payments = remaining_loan_term.days / 12
    #     elif payment_period == "biweek":
    #         remaining_payments = remaining_loan_term / 24


    def create_snapshot(self):
        StudentLoanSnapshot.objects.get_or_create(student_loan=self,
                                                  date=timezone.now().date(),
                                                  defaults={
                                                    'account': self.account,
                                                    'user_institution': self.user_institution,
                                                    'account_number': self.account_number,
                                                    'expected_payoff_date': self.expected_payoff_date,
                                                    'guarantor': self.guarantor,
                                                    'interest_rate_percentage': self.interest_rate_percentage,
                                                    'is_overdue': self.is_overdue,
                                                    'last_payment_amount': self.last_payment_amount,
                                                    'last_payment_date': self.last_payment_date,
                                                    'last_statement_balance': self.last_statement_balance,
                                                    'last_statement_issue_date': self.last_statement_issue_date,
                                                    'loan_name': self.loan_name,
                                                    'end_date':self.end_date,
                                                    'type': self.type,
                                                    'minimum_payment_amount': self.minimum_payment_amount,
                                                    'next_payment_due_date': self.next_payment_due_date,
                                                    'origination_date': self.origination_date,
                                                    'origination_principal_amount': self.origination_principal_amount,
                                                    'outstanding_interest_amount': self.outstanding_interest_amount,
                                                    'payment_reference_number': self.payment_reference_number,
                                                    'estimated_pslf_eligibility_date': self.estimated_pslf_eligibility_date,
                                                    'payments_made': self.payments_made,
                                                    'pslf_payments_remaining': self.pslf_payments_remaining,
                                                    'repayment_description': self.repayment_description,
                                                    'repayment_type': self.repayment_type,
                                                    'sequence_number': self.sequence_number,
                                                    'ytd_interest_paid': self.ytd_interest_paid,
                                                    'ytd_principal_paid': self.ytd_principal_paid
                                                    }
                                                )

class StudentLoanSnapshot(models.Model):
    student_loan = models.ForeignKey(StudentLoan, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account_number = models.CharField(max_length=32, blank=True, null=True, default=None)
    expected_payoff_date = models.DateField(blank=True, null=True, default=None)
    guarantor = models.CharField(max_length=128, blank=True, null=True, default=None)
    interest_rate_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_overdue = models.BooleanField(default=False, blank=True, null=True)
    last_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True, default=None)
    last_statement_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_statement_issue_date = models.DateField(blank=True, null=True, default=None)
    loan_name = models.CharField(max_length=128, blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True, default=None)
    type = models.CharField(max_length=64, blank=True, null=True, default=None)
    minimum_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    next_payment_due_date = models.DateField(blank=True, null=True, default=None)
    origination_date = models.DateField(blank=True, null=True, default=None)
    origination_principal_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    outstanding_interest_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    payment_reference_number = models.CharField(max_length=64, blank=True, null=True, default=None)
    estimated_pslf_eligibility_date = models.DateField(blank=True, null=True, default=None)
    payments_made = models.IntegerField(default=0, blank=True, null=True)
    pslf_payments_remaining = models.IntegerField(default=0, blank=True, null=True)
    repayment_description = models.CharField(max_length=64, blank=True, null=True, default=None)
    repayment_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    sequence_number = models.IntegerField(default=0, blank=True, null=True)
    ytd_interest_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    ytd_principal_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(blank=True, null=True, default=None)
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
    last_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True, default=None)
    last_statement_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_statement_issue_date = models.DateField(blank=True, null=True, default=None)
    late_fee_amount = models.DecimalField(max_digits=18, decimal_places=2, default=None, blank=True, null=True)
    minimum_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    next_payment_due_date = models.DateField(blank=True, null=True, default=None)
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, default=None, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user_institution.user.username, self.user_institution.institution)

    def create_snapshot(self):
        CreditCardSnapshot.objects.get_or_create(credit_card=self,
                                                  date=timezone.now().date(),
                                                  defaults={
                                                      'account': self.account,
                                                      'user_institution': self.user_institution,
                                                      'is_overdue': self.is_overdue,
                                                      'last_payment_amount': self.last_payment_amount,
                                                      'last_payment_date': self.last_payment_date,
                                                      'last_statement_balance': self.last_statement_balance,
                                                      'last_statement_issue_date': self.last_statement_issue_date,
                                                      'late_fee_amount': self.late_fee_amount,
                                                      'minimum_payment_amount': self.minimum_payment_amount,
                                                      'next_payment_due_date': self.next_payment_due_date,
                                                      'credit_limit': self.credit_limit
                                                  })

class CreditCardSnapshot(models.Model):
    credit_card = models.ForeignKey(CreditCard, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_overdue = models.BooleanField(default=False)
    last_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True, default=None)
    last_statement_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    last_statement_issue_date = models.DateField(blank=True, null=True, default=None)
    late_fee_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    minimum_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    next_payment_due_date = models.DateField(blank=True, null=True, default=None)
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}: {}".format(self.user_institution.user.username, self.user_institution.institution)

class APR(models.Model):
    credit_card = models.ForeignKey(CreditCard, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    apr_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    apr_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0, null=True, blank=True)
    balance_subject_to_apr = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True, blank=True)
    interest_charge_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.credit_card)
