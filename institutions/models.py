from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *
import uuid
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)
from accounts.models import *
from django.utils import timezone
import datetime


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
    plaid_id = models.CharField(max_length=64, blank=True, null=True, default=None)
    institution = models.ForeignKey(Institution, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    # this is needed to retrieve API data for instances related to this institution
    access_token = models.CharField(max_length=64, default=None)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        if self.user and self.institution:
            return "{}: {}".format(self.user.username, self.institution.name)
        else:
            return "{}".format(self.id)

    def populate_transactions_loop_launch(self):
        offset = 0
        while True:
            result = self.populate_transactions(offset=offset)
            if not result:
                break
            offset += 500  # 500 is the maximum value for count so it is the maximum step value for offset
        return True

    def populate_transactions(self, start_date=None, offset=0, count=500):  # maximum
        now = timezone.now().date()
        if not start_date:
            days_nmb = 365 * 3
            start_date = now - datetime.timedelta(days=days_nmb)
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        try:
            transactions_data = client.Transactions.get(access_token=self.access_token, start_date=start_date,
                                                        end_date=end_date, offset=offset, count=count)
            print(transactions_data)
        except Exception as e:
            print(e)
            return False
        bulk_create_list = list()
        for transaction in transactions_data["transactions"]:
            kwargs = dict()
            account_id = transaction["account_id"]
            account = Account.objects.get(account_id=account_id)
            amount = transaction["amount"]
            transaction_date = transaction["date"]
            category_name = transaction["category"][0]
            category_id = transaction["category_id"]
            category, created = TransactionCategory.objects.get_or_create(name=category_name, plaid_id=category_id)
            iso_currency_code = transaction["iso_currency_code"]
            currency, created = Currency.objects.get_or_create(code=iso_currency_code)
            name = transaction["name"]
            pending = transaction["pending"]
            transaction_id = transaction["transaction_id"]
            transaction_type_name = transaction["transaction_type"]
            type, created = TransactionType.objects.get_or_create(name=transaction_type_name)
            kwargs["account"] = account
            kwargs["amount"] = amount
            kwargs["currency"] = currency
            kwargs["name"] = name
            kwargs["is_pending"] = pending
            kwargs["plaid_id"] = transaction_id
            kwargs["type"] = type
            kwargs["category"] = category
            kwargs["date"] = transaction_date
            """Such approach will increase speed for populating large volumes of data"""
            if not Transaction.objects.filter(plaid_id=transaction_id).exists():
                """In test environment, transaction_id are changed every time for some reason, but
                in production environment it should not be like this.
                At the same time filtering by other fields are not relevant, because date has only date format
                and not date time with miliseconds. Theoretically a few transactions can appear for the same
                date with same other parameters except of transaction_id."""
                bulk_create_list.append(Transaction(**kwargs))
        """create all objects at one transactions. 
        This will not trigger save method on the model, because data is inserted
        to the database directly"""
        if bulk_create_list:
            Transaction.objects.bulk_create(bulk_create_list)

        total_transactions = transactions_data["total_transactions"]
        if total_transactions < offset + count:
            return False  # so future iterating should be finished
        else:
            return True

    def populate_income_information(self):
        from income.models import Income, IncomeStream
        try:
            income_data = client.Income.get(self.access_token)
        except Exception as e:
            print(e)
            return False
        data = income_data["income"]
        income_defaults_kwargs = {
            "max_number_of_overlapping_income_streams": data["max_number_of_overlapping_income_streams"],
            "number_of_income_streams": data["number_of_income_streams"],
            "last_year_income_before_tax": data["last_year_income_before_tax"],
            "last_year_income_minus_tax": data["last_year_income"],
            "projected_yearly_income_before_tax": data["projected_yearly_income_before_tax"],
            "projected_yearly_minus_tax": data["projected_yearly_income"],
        }

        income, created = Income.objects.update_or_create(user_institution=self, defaults=income_defaults_kwargs)
        income_streams = data["income_streams"]
        for income_stream in income_streams:
            # ToDo: think about a way to define and deactivate income streams, which are not relevant anymore
            name = income_stream["name"]
            confidence = income_stream["confidence"]
            days = income_stream["days"]
            monthly_income = income_stream["monthly_income"]
            IncomeStream.objects.update_or_create(income=income, name=name,
                                                  defaults={"confidence": confidence, "days": days,
                                                            "monthly_income": monthly_income})

    def populate_accounts(self):
        """The code with getting stripe token is not needed here:
        stripe_response = client.Processor.stripeBankAccountTokenCreate(self.access_token, account_id)
        even if it is referenced in the plaid docs.
        Following information in this link https://stripe.com/docs/ach, such token is only needed in case
        of the need to make payments, using that account.
        """
        try:
            bank_accounts_data = client.Accounts.get(self.access_token)
        except Exception as e:
            print(e)
            return False
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
            bank_account_defaults_kwargs = {
                "name": account_data["name"],
                "official_name": account_data["official_name"],
                "mask": account_data["mask"],
                "type": account_type,
                "subtype": account_subtype,
                "available_balance": account_data["balances"]["available"] if account_data["balances"]["available"] else 0,
                "current_balance": account_data["balances"]["current"] if account_data["balances"]["current"] else 0,
                "limit_amount": account_data["balances"]["limit"] if account_data["balances"]["limit"] else 0,
                "currency": currency
            }
            """Account information can be updated after initial creation of the instance"""
            Account.objects.update_or_create(user_institution=self, account_id=account_id,
                                             **bank_account_defaults_kwargs)
