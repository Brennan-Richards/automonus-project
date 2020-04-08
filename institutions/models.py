from liabilities.models import StudentLoan, DisbursementDate, ServicerAddress, CreditCard, APR, LiabilityAnalysis
from investments.models import UserSecurity, InvestmentTransaction, InvestmentTransactionType, Security, Holding, SecurityType
import datetime
from django.utils import timezone
from accounts.models import *
import os
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
                secret=settings.PLAID_SECRET,
                public_key=settings.PLAID_PUBLIC_KEY,
                environment=settings.PLAID_ENV
                )

class ModelBaseFieldsAbstract(models.Model):
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        abstract = True


class Institution(ModelBaseFieldsAbstract):
    plaid_id = models.CharField(max_length=64)
    pass


class UserInstitution(ModelBaseFieldsAbstract):
    """Data object, which is stored in this model is called 'Item' in Plaid API docs:
    it represents a combination of user and institution
    """
    plaid_id = models.CharField(max_length=64, blank=True, null=True, default=None)
    institution = models.ForeignKey(Institution, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    # this is needed to retrieve API data for instances related to this institution
    access_token = models.CharField(max_length=64, default=None)
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.user and self.institution:
            return "{}: {}".format(self.user.username, self.institution.name)
        else:
            return "{}".format(self.id)

    def populate_transactions_loop_launch(self, type=None):
        offset = 0
        if not type:
            type = "account_transaction"
        while True:
            if type == "account_transaction":
                result = self.populate_transactions(offset=offset)
            else:
                result = self.populate_investment_transactions(offset=offset)
            if not result:
                break
            offset += 500  # 500 is the maximum value for count so it is the maximum step value for offset
        return True


        def populate_or_update_accounts(self, stripe_bank_account_token=''):
            try:
                bank_accounts_data = client.Auth.get(self.access_token)
            except Exception as e:
                print(e)
                return False
            # Create account Numbers
            numbers = bank_accounts_data.get("numbers", None)
            if numbers:
                arc_data = numbers.get('ach', [])
            else:
                arc_data = []
            for account_data in bank_accounts_data["accounts"]:
                account_id = account_data["account_id"]
                type_name = account_data["type"]
                if type_name:
                    account_type, created = AccountType.objects.get_or_create(name=type_name)
                else:
                    account_type = None
                subtype_name = account_data["subtype"]
                if subtype_name:
                    account_subtype, created = AccountSubType.objects.get_or_create(name=subtype_name)
                else:
                    account_subtype = None

                currency_code = account_data["balances"]["iso_currency_code"]
                currency, created = Currency.objects.get_or_create(code=currency_code)
                bank_account_defaults = {
                    "name": account_data.get("name", ""),
                    "official_name": account_data.get("official_name", ""),
                    "mask": account_data.get("mask", ""),
                    "type": account_type,
                    "subtype": account_subtype,
                    "available_balance": account_data["balances"]["available"] if account_data["balances"]["available"] else 0,
                    "current_balance": account_data["balances"].get('current', 0),
                    "limit_amount": account_data["balances"]["limit"] if account_data["balances"]["limit"] else 0,
                    "currency": currency,
                    "stripe_bank_account_token": stripe_bank_account_token,
                }

                #If an Account instance already exists, the data will be updated.
                account, created = Account.objects.update_or_create(user_institution=self,
                                                                    account_id=account_id,
                                                                    defaults=bank_account_defaults)
                for arc in arc_data:
                    if arc['account_id'] == account.account_id:
                        acc_obj = AccountNumber.objects.create(account=account,
                                                 number_type=AccountNumber.ACH,
                                                 number_id=arc.get('account', None),
                                                 number_routing=arc.get('routing', None))
                account.create_account_snapshot()


    def populate_investment_transactions(self, start_date=None, offset=0, count=500):  # maximum
        #investment transactions are linked a 'Security' model instance
        now = timezone.now().date()
        if not start_date:
            days_nmb = 365 * 3
            start_date = now - datetime.timedelta(days=days_nmb)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        try:
            transactions_data = client.InvestmentTransactions.get(access_token=self.access_token, start_date=start_date,
                                                                  end_date=end_date, offset=offset, count=count)
            print("Getting investment transactions")
        except Exception as e:
            print(e)
            return False
        bulk_create_list = list()
        for transaction in transactions_data["investment_transactions"]:
            kwargs = dict()
            account_id = transaction.get("account_id", "")
            account = Account.objects.get(account_id=account_id)

            user_security = UserSecurity.objects.get(user_institution=self, security__plaid_security_id=transaction["security_id"])

            amount = transaction.get("amount", "")
            fees = transaction.get("fees", "")
            transaction_date = transaction.get("date", "")
            quantity = transaction.get("quantity", "")

            iso_currency_code = transaction.get("iso_currency_code", "")
            currency, created = Currency.objects.get_or_create(code=iso_currency_code)

            name = transaction.get("name", "")
            investment_transaction_id = transaction.get("investment_transaction_id", "")
            type = transaction.get("type", "")
            type, created = InvestmentTransactionType.objects.get_or_create(name=type)
            cancel_transaction_id = transaction.get("cancel_transaction_id", "")

            kwargs["user_security"] = user_security
            kwargs["account"] = account  #
            kwargs["amount"] = amount  #
            kwargs["quantity"] = quantity
            kwargs["fees"] = fees
            kwargs["currency"] = currency #
            kwargs["name"] = name  #
            kwargs["plaid_inv_transaction_id"] = investment_transaction_id  #
            kwargs["type"] = type  #
            kwargs["date"] = transaction_date  #
            kwargs["cancel_transaction_id"] = cancel_transaction_id  #
            """Such approach will increase speed for populating large volumes of data"""
            if not InvestmentTransaction.objects.filter(plaid_inv_transaction_id=investment_transaction_id).exists():
                """In test environment, transaction_id are changed every time for some reason, but
                in production environment it should not be like this.
                At the same time filtering by other fields are not relevant, because date has only date format
                and not date time with miliseconds. Theoretically a few transactions can appear for the same
                date with same other parameters except of transaction_id."""
                bulk_create_list.append(InvestmentTransaction(**kwargs))
        """create all objects at one transactions.
        This will not trigger save method on the model, because data is inserted
        to the database directly"""
        if bulk_create_list:
            InvestmentTransaction.objects.bulk_create(bulk_create_list)

        total_transactions = transactions_data["total_investment_transactions"]
        if total_transactions < offset + count:
            return False  # so future iterating should be finished
        else:
            return True


    def populate_securities_and_holdings(self):
        try:
            # this returns both security and holding instances
            data = client.Holdings.get(self.access_token)
        except Exception as e:
            return False
        securities = data["securities"]
        holdings = data["holdings"]
        """
        [{'close_price': 0.011, 'close_price_as_of': None, 'cusip': None
        , 'institution_id': None, 'institution_security_id': None, 'is_cash_equivalent': False, 'isin': None,
        'iso_currency_code': 'USD', 'name': "Nflx Feb 01'18 $355 Call", 'proxy_security_
        id': None, 'security_id': '8E4L9XLl6MudjEpwPAAgivmdZRdBPJuvMPlPb', 'sedol': None,
        'ticker_symbol': 'NFLX180201C00355000', 'type': 'derivative', 'unofficial_currency_code': None},
        """
        for item in securities:
            #creating Security model if one does not already exist
            security_id = item.get("security_id", "")
            ticker_symbol = item.get("ticker_symbol", "")
            name = item.get("name", "")
            isin = item.get("isin", "")
            sedol = item.get("sedol", "")
            cusip = item.get("cusip", "")
            plaid_security_id = item.get("plaid_security_id", "")
            security, created = Security.objects.get_or_create(ticker_symbol=ticker_symbol, name=name,
                                                               isin=isin, sedol=sedol,
                                                               cusip=cusip, plaid_security_id=security_id)
            #creating SecurityType model " " " " " "
            name = item.get("type", "")
            security_type, created = SecurityType.objects.get_or_create(name=name)
            #creating Currency model " " " " " "
            code = item.get("iso_currency_code", "")
            currency, created = Currency.objects.get_or_create(code=code)

            kwargs = {
                "is_cash_equivalent": item.get("is_cash_equivalent", ""),
                "type": security_type,
                "close_price": item.get("close_price", ""), "close_price_as_of": item.get("close_price_as_of", ""),
                "currency": currency
            }

            user_security, created = UserSecurity.objects.update_or_create(user_institution=self, security=security, defaults=kwargs)
            user_security.create_snapshot()

        for item in holdings:
            account_id = item.get("account_id", "")
            account = Account.objects.get(account_id=account_id)

            security_id = item.get("security_id", "")
            user_security, created = UserSecurity.objects.get_or_create(security__plaid_security_id=security_id,
                                                                        user_institution=self)

            code = item.get("iso_currency_code", "")
            currency, created = Currency.objects.get_or_create(code=code)

            kwargs = {
                "institution_value": item["institution_value"],
                "institution_price": item["institution_price"],
                "institution_price_as_of": item["institution_price_as_of"],
                "cost_basis": item["cost_basis"],
                "currency": currency,
                "quantity": item["quantity"]
            }
            holding, created = Holding.objects.update_or_create(account=account,
                                                                user_security=user_security,
                                                                defaults=kwargs)
            holding.create_snapshot()

    def check_client(self):
        return client
