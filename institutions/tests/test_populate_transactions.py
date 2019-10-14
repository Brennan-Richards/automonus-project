
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
from accounts.models import Transaction, TransactionCategory, Currency
from decimal import Decimal


# import json
# import os
# from django.conf import settings
# path = os.path.join(settings.BASE_DIR,
#                     './institutions/tests/mock_jsons/inc_tx.json')
# with open(path, "w") as out:
#     out.write(json.dumps(transactions_data))

class InvestmentTransactionsMock():
    def __init__(self):
        path = os.path.join(settings.BASE_DIR,
                            './institutions/tests/mock_jsons/investment_transactions.json')
        with open(path) as reading_tx:
            self.tx_data = json.load(reading_tx)

    def get(self, *args, **kwargs):
        return self.tx_data


class TransactionsMock():
    def __init__(self):
        path = os.path.join(settings.BASE_DIR,
                            './institutions/tests/mock_jsons/transactions.json')
        with open(path) as reading_tx:
            self.tx_data = json.load(reading_tx)

    def get(self, *args, **kwargs):
        return self.tx_data


class MockPlaidClient():

    def __init__(self, *args, **kwargs):
        self.Transactions = TransactionsMock()
        self.InvestmentTransactions = InvestmentTransactionsMock()


class PopulateTxTest(TestCase):
    # institutions.tests.test_populate_transactions.PopulateTxTest
    fixtures = ['users_data', 'data_for_populate_tx']

    def setUp(self):
        self.first_user = User.objects.first()
        self.test_model = test_model
        self.test_model.client = MockPlaidClient()
        self.first_user_institution = test_model.UserInstitution.objects.first()

    def test_base_populate_tx(self):
        self.first_user_institution.populate_transactions_loop_launch()
        transactions_data = MockPlaidClient().Transactions.get()
        count_mock_tx = 0
        for transaction in transactions_data["transactions"]:
            count_mock_tx += 1
            # check category and currency crating by "get"
            transaction_id = transaction["transaction_id"]
            code = transaction.get("iso_currency_code", None)
            group = transaction.get("transaction_type", None)
            category_id = transaction.get("category_id", None)
            tx_data_kwargs = {
                "name": transaction["name"],
                # just get
                "currency": Currency.objects.get(code=transaction["iso_currency_code"]) if code else None,
                "category": TransactionCategory.objects.get(plaid_category_id=category_id,
                                                            group=group) if group and category_id else None,
                "plaid_id": transaction["transaction_id"],
            }
            # check if create transaction
            tx = Transaction.objects.get(plaid_id=transaction_id)
            # check fields values
            for key in tx_data_kwargs.keys():
                self.assertEqual(tx_data_kwargs[key],
                                 getattr(tx, key),
                                 f'check tx {transaction_id} field {key}')
