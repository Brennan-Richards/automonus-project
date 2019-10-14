
from django.test import TestCase
import importlib
import os
from django.conf import settings
import institutions.models as test_model
# from institutions.models import client
# Create your tests here.
from django.contrib.auth.models import User
from income.models import Income, IncomeStream

from decimal import Decimal

CORRECT_ACCOUNT = "CORRECT_ACCOUNT"
# DATA FROM PLAID RESPONSE
ACCOUNT_RESPONSE = {
    CORRECT_ACCOUNT: {
        'accounts': [
            {'account_id': '45p4ogwK57C8dK19vpGECeMM5xjGo8Cd1apby',
                'balances': {'available': 100, 'current': 110, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '0000', 'name': 'Plaid Checking', 'official_name': 'Plaid Gold Standard 0% Interest Checking', 'subtype': 'checking', 'type': 'depository'},
            {'account_id': 'NDMd53VGDzfoEJ96dWn5C3yyjzrwWLfWDM864',
                'balances': {'available': 200, 'current': 210, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '1111', 'name': 'Plaid Saving', 'official_name': 'Plaid Silver Standard 0.1% Interest Saving', 'subtype': 'savings', 'type': 'depository'},
            {'account_id': 'PDj45dRqD3fnpm6VRle5IZNNknzgMWf7MzL64',
                'balances': {'available': None, 'current': 1000, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '2222', 'name': 'Plaid CD', 'official_name': 'Plaid Bronze Standard 0.2% Interest CD', 'subtype': 'cd', 'type': 'depository'},
            {'account_id': 'jnkdlK3AnyCb1nQPWydAi9wwrLdD1zC1XJKWX',
                'balances': {'available': None, 'current': 410, 'iso_currency_code': 'USD', 'limit': 2000, 'unofficial_currency_code': None},
                'mask': '3333', 'name': 'Plaid Credit Card', 'official_name': 'Plaid Diamond 12.5% APR Interest Credit Card', 'subtype': 'credit card', 'type': 'credit'},
            {'account_id': '7DLjEWvBDZf8onKdJX5ECW77lLVyEeFg9XbJW',
                'balances': {'available': 43200, 'curršnt': 43200, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '4444', 'name': 'Plaid Money Market', 'official_name': 'Plaid Platinum Standard 1.85% Interest Money Market', 'subtype': 'money market', 'type': 'depository'},
            {'account_id': 'eWyr584oWAiolDNaE5njCmKKg8QZeWiLjWv9g',
                'balances': {'available': None, 'current': 320.76, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '5555', 'name': 'Plaid IRA', 'official_name': None, 'subtype': 'ira', 'type': 'investment'},
            {'account_id': 'QD7N5aQKDxfnr6BlVqg5IVPPMWR7LJup8KPmg',
                'balances': {'available': None, 'current': 23631.9805, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '6666', 'name': 'Plaid 401k', 'official_name': None, 'subtype': '401k', 'type': 'investment'},
            {'account_id': 'ZWpL5GwNWQinpZlPB4EKIaKK7EqJQWtgK7aqR',
                'balances': {'available': None, 'current': 65262, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '7777', 'name': 'Plaid Student Loan', 'official_name': None, 'subtype': 'student', 'type': 'loan'}
        ],
        'item': {'available_products': ['assets', 'auth', 'balance', 'credit_details', 'identity', 'liabilities'],
                 'billed_products': ['income', 'transactions'],
                 'error': None, 'institution_id': 'ins_9', 'item_id': 'ynDgeZ9jnNCp7AbqKEWjfdp3mMJgRQiyGj9y8',
                 'webhook': 'https://099d8552.ngrok.io'}, 'request_id': 'rOBGivGN1tni2oL'
    }
}


class AccountMock():
    def __init__(self):
        pass

    def get(self, access_token):
        return ACCOUNT_RESPONSE[access_token]


class MockPlaidClient():

    def __init__(self, *args, **kwargs):
        self.Accounts = AccountMock()


class PopulateAccountTest(TestCase):
    # institutions.tests.test_populate_accounts.PopulateAccountTest
    fixtures = ['users_data']

    def setUp(self):
        self.first_user = User.objects.first()
        self.test_model = test_model
        self.test_model.client = MockPlaidClient()

    def __check_count_type(self, accounts_response, type_key):
        names = []
        not_empty_count = 0
        for account in accounts_response:
            account_type = account.get(type_key, None)
            if account_type and not account_type in names:
                not_empty_count += 1
                names.append(account_type)
        return names, not_empty_count

    def __check_count_nested(self, accounts_response, nested_type_key, type_key):
        names = []
        not_empty_count = 0
        for account in accounts_response:
            nested_data = account.get(nested_type_key, None)
            if nested_data:
                data_type = nested_data.get(type_key, None)
                if data_type and not data_type in names:
                    not_empty_count += 1
                    names.append(data_type)
        return names, not_empty_count

    def test_base(self):
        institution = test_model.Institution.objects.create(name="Wells Fargo TEST",
                                                            plaid_id=CORRECT_ACCOUNT)
        first_user_institution, created = test_model.UserInstitution.objects.update_or_create(plaid_id='FIRST',
                                                                                              user=self.first_user,
                                                                                              institution=institution,
                                                                                              is_active=True,
                                                                                              defaults={"access_token": CORRECT_ACCOUNT})
        first_user_institution.populate_or_update_accounts()
        # -------------------
        # check tah all account was created
        # -------------------
        accounts_names, accounts_not_empty_count = self.__check_count_type(
            accounts_response=ACCOUNT_RESPONSE[CORRECT_ACCOUNT]['accounts'],
            type_key='type'
        )
        accounts_types = test_model.AccountType.objects.filter(
            name__in=accounts_names)
        self.assertEqual(accounts_not_empty_count,
                         accounts_types.count(),
                         msg="test_base Count created accounts type")
        # -------------------
        # check accounts subtypes was created
        # -------------------
        subtypes_names, subtypes_not_empty_count = self.__check_count_type(
            accounts_response=ACCOUNT_RESPONSE[CORRECT_ACCOUNT]['accounts'],
            type_key='subtype'
        )
        accounts_subtypes = test_model.AccountSubType.objects.filter(
            name__in=subtypes_names)
        self.assertEqual(subtypes_not_empty_count,
                         accounts_subtypes.count(),
                         msg="test_base Count created accounts subtype")
        # -------------------
        # check Currency was created
        # -------------------
        currency_codes, subtypes_not_empty_count = self.__check_count_nested(
            accounts_response=ACCOUNT_RESPONSE[CORRECT_ACCOUNT]['accounts'],
            nested_type_key='balances',
            type_key='iso_currency_code'
        )
        currency_codes_list = test_model.Currency.objects.filter(
            code__in=currency_codes)
        self.assertEqual(subtypes_not_empty_count,
                         currency_codes_list.count(),
                         msg=f'Count created currency codes currency_codes_list: {currency_codes_list} in {currency_codes}')
        # -------------------
        # check how create accounts data
        # -------------------
        for account_data in ACCOUNT_RESPONSE[CORRECT_ACCOUNT]['accounts']:
            account_id = account_data.get('account_id', None)
            account_data_kwargs = {
                "name": account_data["name"],
                "official_name": account_data["official_name"],
                "mask": account_data["mask"],
                "available_balance": round(Decimal(account_data["balances"]["available"] if account_data["balances"]["available"] else 0), 2),
                "current_balance": round(Decimal(account_data["balances"].get('current', 0)), 2),
                "limit_amount": round(Decimal(account_data["balances"]["limit"] if account_data["balances"]["limit"] else 0), 2),
            }
            if account_id:
                account = test_model.Account.objects.get(user_institution=first_user_institution,
                                                         account_id=account_id)
                for key in account_data_kwargs.keys():
                    self.assertEqual(account_data_kwargs[key],
                                     getattr(account, key),
                                     f'check account {account_id} field {key}')
