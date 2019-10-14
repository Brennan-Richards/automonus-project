
from django.test import TestCase
import importlib
import os
import json
import institutions.models as test_model
from django.conf import settings
# from institutions.models import client
# Create your tests here.
from django.contrib.auth.models import User
from income.models import Income, IncomeStream
from accounts.models import Transaction, TransactionCategory, Currency, Account
from investments.models import Security, UserSecurity, SecurityType, Holding
from decimal import Decimal

# import json
# path = os.path.join(settings.BASE_DIR,
#                     './institutions/tests/mock_jsons/holdings_securities.json')
# with open(path, "w") as out:
#     out.write(json.dumps(data))


class HoldingsMock():
    def __init__(self):
        path = os.path.join(settings.BASE_DIR,
                            './institutions/tests/mock_jsons/holdings_securities.json')
        with open(path) as reading_tx:
            self.tx_data = json.load(reading_tx)

    def get(self, *args, **kwargs):
        return self.tx_data


class MockPlaidClient():

    def __init__(self, *args, **kwargs):
        self.Holdings = HoldingsMock()


class PopulateHoldingSecuritiesTest(TestCase):
    # institutions.tests.test_populate_securities_and_holdings.PopulateHoldingSecuritiesTest
    fixtures = ['users_data', 'data_for_hodling_securities']

    def setUp(self):
        self.first_user = User.objects.first()
        self.test_model = test_model
        self.test_model.client = MockPlaidClient()
        # last because Wells Fargo that saved mock json
        self.last_user_institution = test_model.UserInstitution.objects.last()

    def test_base(self):
        resonse_data = MockPlaidClient().Holdings.get()
        securities = resonse_data["securities"]
        holdings = resonse_data["holdings"]
        #  check that all services was created and user servises
        self.last_user_institution.populate_securities_and_holdings()
        for item in securities:
            security_id = item["security_id"]
            security = Security.objects.get(ticker_symbol=item["ticker_symbol"],
                                            name=item["name"],
                                            isin=item["isin"],
                                            sedol=item["sedol"],
                                            cusip=item["cusip"],
                                            plaid_security_id=security_id)
            security_type = SecurityType.objects.get(name=item["type"])
            currency = Currency.objects.get(code=item["iso_currency_code"])
            close_price = item.get('close_price', 0)
            close_price_as_of = item.get('close_price_as_of', 0)
            sec_data_kwargs = {
                "is_cash_equivalent": item["is_cash_equivalent"],
                "type": security_type,
                "close_price": round(Decimal(close_price if close_price else 0), 4),
                "close_price_as_of": close_price_as_of,
                "currency": currency
            }
            user_security = UserSecurity.objects.get(user_institution=self.last_user_institution,
                                                     security=security)

            # check fields values
            for key in sec_data_kwargs.keys():
                self.assertEqual(sec_data_kwargs[key],
                                 getattr(user_security, key),
                                 f'check tx {user_security} field {key}')
            #  check that all services was created and user servises
        for item in holdings:
            security_id = item["security_id"]
            account = Account.objects.get(account_id=item["account_id"])
            user_security = UserSecurity.objects.get(security__plaid_security_id=security_id,
                                                     user_institution=self.last_user_institution)
            currency = Currency.objects.get(code=item["iso_currency_code"])
            cost_basis = item.get('cost_basis', 0)
            institution_value = item.get('institution_value', 0)
            institution_price = item.get('institution_price', 0)
            institution_price_as_of = item.get('institution_price_as_of', 0)
            quantity = item.get('quantity', 0)
            kwargs = {
                "institution_value": round(Decimal(institution_value), 4) if institution_value else None,
                "institution_price": round(Decimal(institution_price), 4) if institution_price else None,
                "institution_price_as_of": round(Decimal(institution_price_as_of), 4) if institution_price_as_of else None,
                "cost_basis": round(Decimal(cost_basis), 4) if cost_basis else None,
                "currency": currency,
                "quantity": round(Decimal(quantity), 4) if quantity else None,
            }
            holding = Holding.objects.get(account=account,
                                          user_security=user_security)
            # check fields values
            for key in kwargs.keys():
                self.assertEqual(kwargs[key],
                                 getattr(holding, key),
                                 f'check tx {holding} field {key}')
