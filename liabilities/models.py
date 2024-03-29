from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
import uuid
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.forms.models import model_to_dict
from decimal import Decimal
# Create your models here.

class ModelBaseFieldsAbstract(models.Model):
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True

class StudentLoan(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account_number = models.CharField(max_length=32, blank=True, null=True, default=None)
    expected_payoff_date = models.DateField(blank=True, null=True, default=None)
    guarantor_name = models.CharField(max_length=128, blank=True, null=True, default=None)
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
        return "{}: {}".format(self.user_institution.user.username, self.guarantor_name)

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

    def amortize(self, steps, payment_amount):
        amortization_series = []
        dates_as_categories = []
        interest_rate_percentage = self.interest_rate_percentage / 100
        if payment_amount is not None:
            payment_amount = payment_amount
        else:
            payment_amount = self.minimum_payment_amount
        payments_per_year = self.get_payments_per_year()
        days_between_payments = 365 / payments_per_year
        balance = self.account.current_balance
        payment_date = date.today()
        for i in range(0, steps):
            #Date increases by one full payment period
            payment_date += timedelta(days=days_between_payments)

            #Calculate interest paid this period
            interest_paid = balance * (interest_rate_percentage / payments_per_year)

            #Calculate principal paid this period
            principal_paid = payment_amount - interest_paid

            #Add current balance to amortization_series
            amortization_series.append(round(float(balance), 2))
            #Add dates to categories for X-Axis of frontend chart
            dates_as_categories.append(payment_date)

            #Balance decreases by principal amount paid
            balance -= principal_paid

        return amortization_series, dates_as_categories

    def amortize_to_zero(self, payment_amount=None):
        amortization_series = []
        dates_as_categories = []
        interest_rate_percentage = self.interest_rate_percentage / 100
        if payment_amount is not None:
            payment = payment_amount
        else:
            payment = self.minimum_payment_amount
        payments_per_year = self.get_payments_per_year()
        days_between_payments = 365 / payments_per_year
        balance = self.account.current_balance
        amortization_series.append(float(balance)) #Setting original balance as first balance
        payment_date = date.today()
        dates_as_categories.append(payment_date) #Setting date of payment 0 as today

        total_interest = 0
        total_principal = 0
        if self.payments_reduces_balance(payment):
            while balance > 0:
                    #Date increases by the numbers of days until the next payment is due
                    payment_date += timedelta(days=days_between_payments)

                    #Calculate interest paid this period and add to total interest paid
                    interest_paid = balance * (interest_rate_percentage / payments_per_year)

                    #Calculate principal paid this period and add to total principal paid
                    principal_paid = payment - interest_paid

                    if balance > payment:
                        balance -= principal_paid
                        total_interest += interest_paid
                        total_principal += principal_paid

                    else:
                        total_principal += balance
                        balance = 0

                    #Add current balance to amortization_series
                    amortization_series.append(round(float(balance), 2))
                    #Add dates to categories for X-Axis of frontend chart
                    dates_as_categories.append(payment_date)


            total_cost_of_loan = total_interest + total_principal
            dates_as_categories = [item.strftime("%m/%d/%Y") for item in dates_as_categories]

            return {"payoff_date":payment_date, "total_principal":round(total_principal, 2), "total_interest":round(total_interest, 2),
                    "amortization_series":amortization_series, "dates_as_categories":dates_as_categories,
                    "total_cost_of_loan":round(total_cost_of_loan, 2)}
        else:
            return round((balance * interest_rate_percentage / payments_per_year), 2)

    def payments_reduces_balance(self, payment_amount):
        balance = self.account.current_balance
        interest_rate_percentage = self.interest_rate_percentage / 100
        payments_per_year = self.get_payments_per_year()

        if payment_amount > (balance * interest_rate_percentage / payments_per_year): #Checks if the loan will decrease with payments, returns False if not.
            return True
        else:
            return False

    def create_snapshot(self):
        StudentLoanSnapshot.objects.get_or_create(student_loan=self,
                                                  date=timezone.now().date(),
                                                  defaults={
                                                    'account': self.account,
                                                    'user_institution': self.user_institution,
                                                    'account_number': self.account_number,
                                                    'expected_payoff_date': self.expected_payoff_date,
                                                    'guarantor_name': self.guarantor_name,
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
    guarantor_name = models.CharField(max_length=128, blank=True, null=True, default=None)
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
        return "{}: {}".format(self.user_institution.user.username, self.guarantor_name)

class Guarantor(models.Model):
    # Object with guarantor data to be used for creating loan payments.
    student_loan = models.OneToOneField(StudentLoan, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    guarantor_name = models.CharField(max_length=128, blank=False, null=False, default=None)
    mailing_address = models.CharField(max_length=256, blank=False, null=False, default=None)
    home_address = models.CharField(max_length=256, blank=False, null=False, default=None)
    ach_account_number = models.CharField(max_length=32, blank=False, null=False)
    def __str__(self):
        return self.guarantor_name

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
    credit_card = models.OneToOneField(CreditCard, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    apr_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    apr_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0, null=True, blank=True)
    balance_subject_to_apr = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True, blank=True)
    interest_charge_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.credit_card)

class LiabilityAnalysis(models.Model):
    student_loan = models.OneToOneField(StudentLoan, on_delete=models.CASCADE, default=False)
    mock_payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
