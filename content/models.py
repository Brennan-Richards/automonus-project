from django.db import models

from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
import uuid
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.forms.models import model_to_dict
from decimal import Decimal

# Create your models here.

class AbstractStudentLoan(models.Model):
    interest_rate_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    payment_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    payments_per_year = models.IntegerField(default=12, blank=True, null=True)

    def payments_reduces_balance(self, payment_amount):
        balance = self.current_balance
        interest_rate_percentage = self.interest_rate_percentage / 100
        payments_per_year = self.payments_per_year
        
        if payment_amount > (balance * interest_rate_percentage / payments_per_year): #Checks if the loan will decrease with payments, returns False if not.
            return True
        else:
            return False

    def amortize_to_zero(self):
        amortization_series = []
        dates_as_categories = []

        interest_rate_percentage = self.interest_rate_percentage / 100
        payment = self.payment_amount
        payments_per_year = self.payments_per_year
        days_between_payments = 30
        balance = self.current_balance

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
