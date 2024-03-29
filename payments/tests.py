from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from institutions.models import UserInstitution
from accounts.models import Account
from payments.stripe_manager import StripleManager

# Create your tests here.


class PopulateAccountTest(TestCase):
    # python manage.py test payments.tests.PopulateAccountTest.test_base_direct_deposits
    fixtures = ["two_test_users_by_1_institution_per_each"]

    def setUp(self):
        self.first_user = User.objects.first()
        self.second_user = User.objects.last()

    def test_base_users(self):
        self.assertEqual(1, 1)

    def test_calculate_application_fee(self):
        fee = StripleManager.calculate_application_fee(23)
        self.assertEqual(23, fee)

    def test_base_direct_deposits(self):
        available_subtypes = ["savings", "checking"]
        user_institution = UserInstitution.objects.filter(user=self.first_user)
        user_accounts = Account.objects.filter(
            user_institution__in=user_institution, subtype__name__in=available_subtypes
        ).first()
        # params
        currency = "usd"
        amount = int(Decimal(1.11) * 100)
        account_uuid = user_accounts.uuid
        # init manager
        sm = StripleManager(account_uuid=account_uuid)
        # call deposit method
        resp = sm.deposit_payment(currency=currency, amount=amount)
        print("==============")
        print(resp)
        print("==============")

    def test_deposit_between_few_users(self):
        available_subtypes = ["savings", "checking"]
        src_user_institution = UserInstitution.objects.filter(user=self.first_user)
        src_user_accounts = Account.objects.filter(
            user_institution__in=src_user_institution,
            subtype__name__in=available_subtypes,
        ).first()

        dest_user_institution = UserInstitution.objects.filter(user=self.second_user)
        dest_user_accounts = Account.objects.filter(
            user_institution__in=dest_user_institution,
            subtype__name__in=available_subtypes,
        ).first()
        # params
        currency = "usd"
        amount = int(Decimal(10) * 100)
        app_fee = int(Decimal(10) * Decimal(0.01) * 100)
        account_uuid = src_user_accounts.uuid
        dest_account_uuid = dest_user_accounts.uuid
        # init manager
        sm = StripleManager(account_uuid=account_uuid)
        # call deposit method
        resp = sm.transfer_between_accounts(
            dest_account_uuid=dest_account_uuid,
            currency=currency,
            amount=amount,
            app_fee=app_fee,
        )
        print("==============")
        print(resp)
        print("==============")

