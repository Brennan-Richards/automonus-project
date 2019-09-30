from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid
from income.models import Income
from institutions.models import UserInstitution
from accounts.models import Transaction, Account
from investments.models import InvestmentTransaction
from django.db.models import Sum
from django.conf import settings


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    if not hasattr(user, "profile"):
        Profile.objects.get_or_create(user=user)
    pass


def user_post_save(sender, instance, created, **kwargs):
    print("user post save")
    if created:
        Profile.objects.get_or_create(user=instance)


post_save.connect(user_post_save, sender=User)


class Profile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    agree_to_receive_emails = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return "{}".format(self.user.username)

    def get_income(self):
        income = Income.objects.filter(user_institution__user=self.user, user_institution__is_active=True)\
            .aggregate(total=Sum("projected_yearly_minus_tax"))
        print(income)
        income = income["total"] if income.get("total") else 0
        return {
            "per_day": round(income/365, 2),
            "per_week": round(income/52, 2),
            "per_month": round(income/12, 2),
            "total": round(income, 2)
        }

    def get_user_institutions(self):
        return self.user.userinstitution_set.filter(is_active=True)

    def get_user_products(self):
        """ This method returns true when the product in question is either
        used or available to be used based on connected UserInstitutions(Items). """
        from plaid import Client
        client = Client(client_id=settings.PLAID_CLIENT_ID,
            secret=settings.PLAID_SECRET,
            public_key=settings.PLAID_PUBLIC_KEY,
            environment=settings.PLAID_ENV
        )
        #below will retrieve the available and billed products for all connected institutions
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

    def has_investment_transactions(self):
        investment_transactions = InvestmentTransaction.objects.filter(account__user_institution__user=self.user)
        if investment_transactions:
             return True

    def has_transactions_for_liabilities(self):
        account_types = ["loan"]
        liabilities_transactions = Transaction.objects.filter(account__user_institution__user=self.user,
                                                              account__type__name__in=account_types)
        if liabilities_transactions:
            return True

    def has_savings(self):
        account_subtypes = ["savings"]
        return Account.objects.filter(subtype__name__in=account_subtypes, user_institution__user=self.user)
