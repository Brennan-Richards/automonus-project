from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)
from accounts.models import *
from django.utils import timezone
import datetime
from investments.models import UserSecurity, InvestmentTransaction, InvestmentTransactionType, Security, Holding, SecurityType
from liabilities.models import StudentLoan, DisbursementDate, ServicerAddress, CreditCard, APR

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
        except Exception as e:
            print(e)
            return False
        bulk_create_list = list()
        for transaction in reversed(transactions_data["transactions"]):
            # Reverse method is used so that transactions with later dates will have larger ID #s.

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
            # print(transactions_data)
        except Exception as e:
            print(e)
            return False
        bulk_create_list = list()
        for transaction in transactions_data["investment_transactions"]:
            kwargs = dict()
            account_id = transaction["account_id"]
            account = Account.objects.get(account_id=account_id)

            user_security = UserSecurity.objects.get(user_institution=self, security__plaid_security_id=transaction["security_id"])

            amount = transaction["amount"]
            fees = transaction["fees"] if transaction["fees"] else 0
            transaction_date = transaction["date"]
            quantity = transaction["quantity"]

            iso_currency_code = transaction["iso_currency_code"]
            currency, created = Currency.objects.get_or_create(code=iso_currency_code)

            name = transaction["name"]
            investment_transaction_id = transaction["investment_transaction_id"]
            type = transaction["type"]
            type, created = InvestmentTransactionType.objects.get_or_create(name=type)
            cancel_transaction_id = transaction["cancel_transaction_id"]

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
            data = client.Holdings.get(self.access_token)  # this returns both security and holding instances
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
            security_id = item["security_id"]
            security, created = Security.objects.get_or_create(ticker_symbol=item["ticker_symbol"], name=item["name"],
                                                               isin=item["isin"], sedol=item["sedol"],
                                                               cusip=item["cusip"], plaid_security_id=security_id)
            security_type, created = SecurityType.objects.get_or_create(name=item["type"])
            currency, created = Currency.objects.get_or_create(code=item["iso_currency_code"])
            kwargs = {
                "is_cash_equivalent": item["is_cash_equivalent"],
                "type": security_type,
                "close_price": item["close_price"], "close_price_as_of": item["close_price_as_of"],
                "currency": currency
            }
            user_security, created = UserSecurity.objects.update_or_create(user_institution=self, security=security, defaults=kwargs)
            user_security.create_snapshot()
        """
        {'account_id': 'Z1l84PBBKaUzRw36
        KBqPsreoddXrk5FgLoJdb', 'cost_basis': 1, 'institution_price': 1, 'institution_price_as_of': None,
        'institution_value': 12345.67, 'iso_currency_code': 'USD', 'quantity': 12345.67, 'se
        curity_id': 'd6ePmbPxgWCWmMVv66q9iPV94n91vMtov5Are', 'unofficial_currency_code': None}
        """
        for item in holdings:
            security_id = item["security_id"]
            account = Account.objects.get(account_id=item["account_id"])
            user_security, created = UserSecurity.objects.get_or_create(security__plaid_security_id=security_id,
                                                                        user_institution=self)
            currency, created = Currency.objects.get_or_create(code=item["iso_currency_code"])
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

    def populate_or_update_accounts(self):
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
            account, created = Account.objects.update_or_create(user_institution=self,
                                                                account_id=account_id,
                                                                defaults=bank_account_defaults_kwargs)
            account.create_account_snapshot()

    def populate_liabilities_data(self):
        try:
            response = client.Liabilities.get(self.access_token)
            student_loans = response["liabilities"]["student"][0]
            account = Account.objects.get(account_id=student_loans["account_id"])
            print("populating student loan data")
        except Exception as e:
            print(e)
            return False
        student_loan_kwargs = {
            "account": account,
            "account_number": student_loans["account_number"],
            "expected_payoff_date": student_loans["expected_payoff_date"],
            "guarantor": student_loans["guarantor"],
            "interest_rate_percentage": student_loans["interest_rate_percentage"],
            "is_overdue": student_loans["is_overdue"],
            "last_payment_amount": student_loans["last_payment_amount"],
            "last_payment_date": student_loans["last_payment_date"],
            "last_statement_balance": student_loans["last_statement_balance"],
            "last_statement_issue_date": student_loans["last_statement_issue_date"],
            "loan_name": student_loans["loan_name"],
            "end_date": student_loans["loan_status"]["end_date"],
            "type": student_loans["loan_status"]["type"],
            "minimum_payment_amount": student_loans["minimum_payment_amount"],
            "next_payment_due_date": student_loans["next_payment_due_date"],
            "origination_date": student_loans["origination_date"],
            "origination_principal_amount": student_loans["origination_principal_amount"],
            "outstanding_interest_amount": student_loans["outstanding_interest_amount"],
            "payment_reference_number": student_loans["payment_reference_number"],
            "estimated_pslf_eligibility_date": student_loans["pslf_status"]["estimated_eligibility_date"],
            "payments_made": student_loans["pslf_status"]["payments_made"],
            "pslf_payments_remaining": student_loans["pslf_status"]["payments_remaining"],
            "repayment_description": student_loans["repayment_plan"]["description"],
            "repayment_type": student_loans["repayment_plan"]["type"],
            "sequence_number": student_loans["sequence_number"],
            "ytd_interest_paid": student_loans["ytd_interest_paid"],
            "ytd_principal_paid": student_loans["ytd_principal_paid"],
            }

        loan_instance, created = StudentLoan.objects.update_or_create(user_institution=self, defaults=student_loan_kwargs)

        loan_instance.create_snapshot()

        disbursement_dates = list()
        for date in student_loans["disbursement_dates"]:
            disbursement_dates.append(date)
            for date in disbursement_dates:
                DisbursementDate.objects.update_or_create(loan_instance=loan_instance, date_of_disbursement=date)

        servicer_address_kwargs = {
            "city": student_loans["servicer_address"]["city"],
            "country": student_loans["servicer_address"]["country"],
            "postal_code": student_loans["servicer_address"]["postal_code"],
            "region": student_loans["servicer_address"]["region"],
            "street": student_loans["servicer_address"]["street"]
        }

        ServicerAddress.objects.get_or_create(loan_instance=loan_instance, defaults=servicer_address_kwargs)

    def populate_credit_card_data(self):
        try:
            response = client.Liabilities.get(self.access_token)
            credit_data = response["liabilities"]["credit"][0]
            account = Account.objects.get(account_id=credit_data["account_id"])
            print("populating credit card data")
        except Exception as e:
            print(e)
            return False

        credit_card_kwargs = {
            "account":account,
            "is_overdue":credit_data["is_overdue"],
            "last_payment_amount":credit_data["last_payment_amount"],
            "last_payment_date":credit_data["last_payment_date"],
            "last_statement_balance":credit_data["last_statement_balance"],
            "last_statement_issue_date":credit_data["last_statement_issue_date"],
            # "late_fee_amount":credit_data["late_fee_amount"] if credit_data["late_fee_amount"] else 0,
            "minimum_payment_amount":credit_data["minimum_payment_amount"] if credit_data["minimum_payment_amount"] else 0,
            "next_payment_due_date":credit_data["next_payment_due_date"],
            # "credit_limit":credit_data["credit_limit"] if credit_data["credit_limit"] else 0,
        }

        credit_card, created = CreditCard.objects.update_or_create(user_institution=self, defaults=credit_card_kwargs)
        credit_card.create_snapshot()

        apr_data = credit_data["aprs"][0]
        apr_kwargs = {
            "apr_type":apr_data["apr_type"],
            "apr_percentage":apr_data["apr_percentage"],
            "balance_subject_to_apr":apr_data["balance_subject_to_apr"],
            "interest_charge_amount":apr_data["interest_charge_amount"]
        }

        APR.objects.update_or_create(credit_card=credit_card, defaults=apr_kwargs)
