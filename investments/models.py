from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import Currency, ModelBaseFieldsAbstract, Account

class SecurityType(ModelBaseFieldsAbstract):
    pass


class Security(models.Model):
    plaid_security_id = models.CharField(max_length=38, blank=True, null=True, default=None)
    name = models.CharField(max_length=256, blank=True, null=True, default=None)
    ticker_symbol = models.CharField(max_length=12, blank=True, null=True, default=None)
    isin = models.CharField(max_length=38, blank=True, null=True, default=None)
    sedol = models.CharField(max_length=38, blank=True, null=True, default=None)
    cusip = models.CharField(max_length=38, blank=True, null=True, default=None)

    def __str__(self):
        if self.ticker_symbol:
            return "{}".format(self.ticker_symbol)
        else:
            return "{}".format(self.id)


class UserSecurity(models.Model):
    """Security Item is needed because investment transaction can be connected for both Security or Holding
    and with security item it will be foreign key just to one object "SecurityItem" and not to two objects."""
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None,
                                         on_delete=models.SET_NULL)

    """Important: it looks like it unique only in terms of combination user_institution + plaid_id (security_id).
    But this needs to be double-checked"""


    """this should be stored in a separate model to prevent duplication of the same text data in this table for
    such fields as name and ticker_symbol"""
    security = models.ForeignKey(Security, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_cash_equivalent = models.BooleanField(default=False)
    type = models.ForeignKey(SecurityType, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    close_price = models.DecimalField(max_digits=16, decimal_places=4, default=0, blank=True, null=True)
    close_price_as_of = models.DateField(blank=True, null=True, default=None)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.security and self.security.name:
            return "{}".format(self.security.name)
        else:
            return "{}".format(self.id)

    def create_snapshot(self):
        UserSecuritySnapshot.objects.get_or_create(user_security=self,
                                                   date=timezone.now().date(),
                                                   defaults={
                                                    'user_institution': self.user_institution,
                                                    'security': self.security,
                                                    'is_cash_equivalent': self.is_cash_equivalent,
                                                    'type': self.type,
                                                    'close_price': self.close_price,
                                                    'close_price_as_of':self.close_price_as_of,
                                                    'currency': self.currency,
                                                   })

class UserSecuritySnapshot(models.Model):
    user_security = models.ForeignKey(UserSecurity, blank=True, null=True, default=None,
                                      on_delete=models.SET_NULL)
    user_institution = models.ForeignKey("institutions.UserInstitution", blank=True, null=True, default=None,
                                        on_delete=models.SET_NULL)
    security = models.ForeignKey(Security, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_cash_equivalent = models.BooleanField(default=False)
    type = models.ForeignKey(SecurityType, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    close_price = models.DecimalField(max_digits=16, decimal_places=4, default=0, blank=True, null=True)
    close_price_as_of = models.DateField(blank=True, null=True, default=None)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.security and self.security.name:
            return f"{self.security.name}"
        else:
            return f"{self.id}"


class Holding(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_security = models.ForeignKey(UserSecurity, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    institution_price = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    institution_price_as_of = models.DateField(blank=True, null=True, default=None)
    institution_value = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    cost_basis = models.DecimalField(max_digits=16, decimal_places=4, default=0, blank=True, null=True)
    quantity = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def create_snapshot(self):
        HoldingSnapshot.objects.get_or_create(holding=self,
                                              date=timezone.now().date(),
                                              defaults={
                                                'account': self.account,
                                                'user_security': self.user_security,
                                                'institution_price': self.institution_price,
                                                'institution_price_as_of': self.institution_price_as_of,
                                                'institution_value': self.institution_value,
                                                'cost_basis': self.cost_basis,
                                                'quantity': self.quantity,
                                                'currency': self.currency,
                                              })

    def get_purchase_price(self):
        purchase_price = self.cost_basis / self.quantity
        return round(purchase_price, 3)

    def get_current_price(self):
        return round(self.institution_price, 3)

    def get_profit_or_loss_current(self):
        profit_or_loss = self.institution_value - self.cost_basis
        return round(profit_or_loss, 3)

    def is_profitable(self):
        if self.get_profit_or_loss_current() < 0:
            return False
        else:
            return True

    def __str__(self):
        return "{}".format(self.id)

class HoldingSnapshot(models.Model):
    holding = models.ForeignKey(Holding, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_security = models.ForeignKey(UserSecurity, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    institution_price = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    institution_price_as_of = models.DateField(blank=True, null=True, default=None)
    institution_value = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    cost_basis = models.DecimalField(max_digits=16, decimal_places=4, default=0, blank=True, null=True)
    quantity = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return f"{self.id}"

class InvestmentTransactionType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.name:
            return "{}".format(self.name)
        else:
            return "{}".format(self.id)


class InvestmentTransaction(models.Model):
    account = models.ForeignKey(Account, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    type = models.ForeignKey(InvestmentTransactionType, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user_security = models.ForeignKey(UserSecurity, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    plaid_inv_transaction_id = models.CharField(max_length=38)
    cancel_transaction_id = models.CharField(max_length=38, blank=True, null=True, default=None)
    date = models.DateField()
    name = models.CharField(max_length=128, blank=True, null=True, default=None)
    quantity = models.DecimalField(max_digits=28, decimal_places=16, default=0)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fees = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True, null=True)
    currency = models.ForeignKey(Currency, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.plaid_inv_transaction_id:
            return "{}".format(self.plaid_inv_transaction_id)
        else:
            return "{}".format(self.id)

# Definitions for PAY_PERIOD_CHOICES below.
DAILY = 1
WEEKLY = 7
BIWEEKLY = 14
SEMIMONTHLY = 15
MONTHLY = 30
YEARLY = 365

# Choices variables for pay_period.
PAY_PERIOD_CHOICES = [
    (DAILY, 'Daily'),
    (WEEKLY, 'Weekly'),
    (BIWEEKLY, 'Biweekly'),
    (SEMIMONTHLY, 'Semi-monthly'),
    (MONTHLY, 'Monthly'),
    (YEARLY, 'Yearly'),
]

# For setting compounding period
DAILY = 365
WEEKLY = 52
BIWEEKLY = 26
SEMIMONTHLY = 24
MONTHLY = 12
YEARLY = 1

# Compounding period
COMPOUNDING_PERIOD_CHOICES = [
    (DAILY, 'Daily'),
    (WEEKLY, 'Weekly'),
    (BIWEEKLY, 'Biweekly'),
    (SEMIMONTHLY, 'Semi-monthly'),
    (MONTHLY,  'Monthly'),
    (YEARLY, 'Yearly'),
]

class MockInvestment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    user = models.OneToOneField(User, blank=True, null=True, default=None, on_delete=models.CASCADE)
    initial_principal = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True, null=True)
    time_in_years = models.IntegerField(default=0, blank=True, null=True)
    payment_amount_per_period = models.DecimalField(max_digits=14, decimal_places=2, default=0, blank=True, null=True)
    payment_period_in_days = models.IntegerField(
            choices=PAY_PERIOD_CHOICES,
            default=MONTHLY,
        )
    times_compounded_per_year = models.IntegerField(
            choices=COMPOUNDING_PERIOD_CHOICES,
            default=MONTHLY,
    )

    def calculate_return(self):
        growth_series = list()
        growth_series_dates = list()
        total_interest = 0
        sim_current_date = date.today()

        # Variables to work with in the compound interest calculation.
        A = float(self.initial_principal)
        r = self.interest_rate / 100
        # t = self.time_in_years
        t_in_days = self.time_in_years * 365
        payment = float(self.payment_amount_per_period)
        days_between_payments = round(self.payment_period_in_days)
        m = self.times_compounded_per_year
        days_between_m = round(365 / self.times_compounded_per_year)

        for i in range(0, t_in_days):
            sim_current_date += timedelta(days=1)
            if i % days_between_payments is 0:
                # Investment value increases by payment amount each time a payment is made.
                A += payment

            if i % days_between_m is 0:

                # Calculating interest earned, then setting investment value to account for interest earned.
                newA = A * float(1 + r/m)
                interest_earned = newA - A
                total_interest += interest_earned
                A = round(newA, 2)

                # Pushing data to arrays.
                growth_series.append(A)
                growth_series_dates.append(sim_current_date)

        #Reformatting growth_series_dates.
        growth_series_dates = [item.strftime("%m/%d/%Y") for item in growth_series_dates]

        return { "final_value":A, "growth_series":growth_series, "growth_series_dates":growth_series_dates,
                "total_interest_earned":round(total_interest, 2), "last_date":date}
