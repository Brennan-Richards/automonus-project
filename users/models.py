from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid
from income.models import Income, IncomeStream
from institutions.models import UserInstitution
from accounts.models import Transaction, Account
from investments.models import InvestmentTransaction
from liabilities.models import StudentLoan, CreditCard
from payments.models import MockSubscription
from expenditures.models import Housing, Car, Miscellaneous, Utilities, Food
from django.db.models import Sum
from django.conf import settings
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    if not hasattr(user, "profile"):
        Profile.objects.get_or_create(user=user)
    pass


def user_post_save(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


post_save.connect(user_post_save, sender=User)


class Profile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='profile')
    agree_to_receive_emails = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return "{}".format(self.user.username)

    def get_income(self):
        income = Income.objects.filter(user_institution__user=self.user, user_institution__is_active=True)\
            .aggregate(total=Sum("projected_yearly_minus_tax"))
        last_year_income = Income.objects.filter(user_institution__user=self.user, user_institution__is_active=True)\
            .aggregate(total=Sum("last_year_income_minus_tax"))
        print(income)
        income = income["total"] if income.get("total") else 0
        last_year_income = last_year_income["total"] if last_year_income.get("total") else 0
        return {
            "per_day": round(income/365, 2),
            "per_week": round(income/52, 2),
            "per_month": round(income/12, 2),
            "total": round(income, 2),
            "last_year_per_day": round(last_year_income/365, 2),
            "last_year_per_week": round(last_year_income/52, 2),
            "last_year_per_month": round(last_year_income/12, 2),
            "last_year": round(last_year_income, 2)
        }

    def get_user_institutions(self):
        #returns all of a user's connected items (userinstitutions) if they exist
        return self.user.userinstitution_set.filter(is_active=True)

    def get_user_products(self):
        #this method returns the available and billed products for all connected institutions
        items = self.get_user_institutions().iterator()
        products_in_use = list()
        for item in items:
            access_token = item.access_token
            response = client.Item.get(access_token)
            billed_products = response["item"]["billed_products"]
            for product in billed_products:
                if product not in products_in_use:
                    products_in_use.append(str(product))

        return products_in_use

    #The following methods check if any of the user's connected institution supports the specific product mentioned.
    def has_income(self):
        products = self.get_user_products()
        if "income" in products:
            return True
    def has_transactions(self):
        products = self.get_user_products()
        if "transactions" in products:
            return True
    def has_investments(self):
        products = self.get_user_products()
        print(products)
        if "investments" in products:
            return True
    def has_liabilities(self):
        products = self.get_user_products()
        if "liabilities" in products:
            return True

    #Methods below check for the existence of SPECIFIC pieces of data connected to the User's account.
    def has_investment_transactions(self):
        investment_transactions = InvestmentTransaction.objects.filter(account__user_institution__is_active=True, account__user_institution__user=self.user)
        if investment_transactions:
             return True

    def has_transactions_for_liabilities(self):
        account_types = ["loan"]
        liabilities_transactions = Transaction.objects.filter(account__user_institution__is_active=True, account__user_institution__user=self.user,
                                                              account__type__name__in=account_types)
        if liabilities_transactions:
            return True
    def has_student_loans_data(self):
        student_loan = StudentLoan.objects.filter(account__user_institution__is_active=True, account__user_institution__user=self.user)
        if student_loan:
            return True
    def has_credit_card_data(self):
        credit_card = CreditCard.objects.filter(account__user_institution__is_active=True, account__user_institution__user=self.user)
        if credit_card:
            return True
    def has_savings_transactions(self):
        savings_accounts = Account.objects.filter(user_institution__is_active=True, subtype__name="savings", user_institution__user=self.user)
        if savings_accounts:
            return True

    def filled_mock_subscription(self):
        model = MockSubscription.objects.filter(user=self.user)
        if model:
            return True

    #Expenditure planning
    def planned_life_expenses(self):
        housing = Housing.objects.filter(user=self.user).aggregate(annual_cost=Sum("annual_cost"))
        car = Car.objects.filter(user=self.user).aggregate(annual_cost=Sum("annual_cost"))
        miscellaneous = Miscellaneous.objects.filter(user=self.user)
        utilities = Utilities.objects.filter(user=self.user)
        food = Food.objects.filter(user=self.user)

        if len(housing) > 0 and len(car) > 0 and len(miscellaneous) > 0 and len(utilities) > 0 and len(food) > 0:
            return True
            # # print(housing["annual_cost"])
            # total = housing["annual_cost"] + car["annual_cost"] \
            #         + miscellaneous.annual_cost + utilities.annual_cost \
            #         + food.annual_cost
            # return round(total, 2)
        else:
            return False

    def added_housing(self):
        house_models = Housing.objects.filter(user=self.user)
        if len(house_models) > 0:
            return True

    def added_car(self):
        car_models = Car.objects.filter(user=self.user)
        if car_models:
            return True
