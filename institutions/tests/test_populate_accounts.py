
from django.test import TestCase
import importlib
import os
from django.conf import settings
import institutions.models as test_model
# from institutions.models import client
# Create your tests here.
from django.contrib.auth.models import User
from income.models import Income, IncomeStream

BASE_GOOD_ACCOUNT = "BASE_GOOD_ACCOUNT"
ACCOUNT_RESPONSE = {
    BASE_GOOD_ACCOUNT : {
        {'accounts': [
            {'account_id': 'JXQG7MBRXGUW5bwlbgonUlp4BZ4BQ6cdEkN6M',
                'balances': {'available': 100, 'current': 110, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '0000', 'name': 'Plaid Checking', 'official_name': 'Plaid Gold Standard 0% Interest Checking', 'subtype': 'checking', 'type': 'depository'},
            {'account_id': 'kBpe87zjBeUR1n4MnlNJFDE5bw5b31FWBoR66',
                'balances': {'available': 200, 'current': 210, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '1111', 'name': 'Plaid Saving', 'official_name': 'Plaid Silver Standard 0.1% Interest Saving', 'subtype': 'savings', 'type': 'depository'},
            {'account_id': 'l3JXyeB53XhylrnDrkPJhgM3rw3rNDFZyRAo3',
                'balances': {'available': None, 'current': 1000, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '2222', 'name': 'Plaid CD', 'official_name': 'Plaid Bronze Standard 0.2% Interest CD', 'subtype': 'cd', 'type': 'depository'},
            {'account_id': 'qkqm8L4pkmfynpGop3rKhP6KqVKq5GidaRXrz',
                'balances': {'available': None, 'current': 410, 'iso_currency_code': 'USD', 'limit': 2000, 'unofficial_currency_code': None},
                'mask': '3333', 'name': 'Plaid Credit Card', 'official_name': 'Plaid Diamond 12.5% APR Interest Credit Card', 'subtype': 'credit card', 'type': 'credit'},
            {'account_id': 'KXyel139XeUm5wdqwAD3SpkZWaZWEeiVP13pv',
                'balances': {'available': 43200, 'current': 43200, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '4444', 'name': 'Plaid Money Market', 'official_name': 'Plaid Platinum Standard 1.85% Interest Money Market', 'subtype': 'money market', 'type': 'depository'},
            {'account_id': 'NXMeroabXeUK5R3zR8DXIepEDlXnyxiWvQN6D',
                'balances': {'available': None, 'current': 320.76, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '5555', 'name': 'Plaid IRA', 'official_name': None, 'subtype': 'ira', 'type': 'investment'},
            {'account_id': 'PVjyB8NXVyUJ5QA3QLDzC1pRj3XKNwU7DAm6D',
                'balances': {'available': None, 'current': 23631.9805, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '6666', 'name': 'Plaid 401k', 'official_name': None, 'subtype': '401k', 'type': 'investment'},
            {'account_id': 'jzke8jrXzeI5Ao67oR4Ls6AZPKjNwbt15abWE',
                'balances': {'available': None, 'current': 65262, 'iso_currency_code': 'USD', 'limit': None, 'unofficial_currency_code': None},
                'mask': '7777', 'name': 'Plaid Student Loan', 'official_name': None, 'subtype': 'student', 'type': 'loan'}
        ],
        'item': {
            'available_products': ['assets', 'auth', 'balance', 'credit_details', 'identity', 'liabilities'],
            'billed_products': ['income', 'transactions'],
            'error': None,
            'institution_id': 'ins_1',
            'item_id': 'Qy7e3EPgyeUd5mkxmPLoC1xMmeAr9bipeb7kA',
            'webhook': 'https://8e96a454.ngrok.io'},
            'request_id': '40DLdGqZpcwnGPq'
        }
    },
}

class AccountMock():

    def __init__(self, *args, **kwargs):
       pass

    def get(self, access_token):
        return INCOME_RESPONSE[access_token]

class MockPlaidClient():

    def __init__(self, *args, **kwargs):
        self.Account = AccountMock()


class PopulateAccountTest(TestCase):
    # institutions.tests.test_populate_income.PopulateIncomeTest.test_empty_stream
    fixtures = ['users_data']

    def setUp(self):
        self.first_user = User.objects.first()
        self.test_model = test_model
        self.test_model.client = MockPlaidClient()

    