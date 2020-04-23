from institutions.models import Institution, UserInstitution
from accounts.models import Account, Transaction
from payments.models import PaymentOrder
from accounts.models import Currency, AccountType, AccountSubType
from investments.models import *


def get_or_create_user_accounts(accounts, user_institution):
    for account in accounts:
        # print(account)
        bank_account_defaults = {
            "account_id": account.get("account_id", ""),
            "name": account.get("name", ""),
            "official_name": account.get("official_name", ""),
            "mask": account.get("mask", ""),
            "available_balance": account["balances"].get("available", 0),
            "current_balance": account["balances"].get('current', ""),
            "limit_amount": account["balances"]["limit"] if account["balances"]["limit"] else 0,
            "currency": Currency.objects.get(code=account['balances'].get('iso_currency_code')),
            "stripe_bank_account_token": 'Not Applicable',
        }

        # [{
        #     "account_id": "vzeNDwK7KQIm4yEog683uElbp9GRLEFXGK98D",
        #     "balances": {
        #       "available": 100,
        #       "current": 110,
        #       "limit": null,
        #       "iso_currency_code": "USD",
        #       "unofficial_currency_code": null,
        #     },
        #     "mask": "0000",
        #     "name": "Plaid Checking",
        #     "official_name": "Plaid Gold Checking",
        #     "subtype": "checking",
        #     "type": "depository",
        #     "verification_status": null
        #   }, ...]

        #If an Account instance already exists, the data will be updated.
        account, created = Account.objects.update_or_create(user_institution=user_institution,
                                                            defaults=bank_account_defaults)
    pass


def get_or_create_user_holdings_securities(securities, holdings, user_institution):
        # print(securities)
        # print(holdings)

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
            #creating SecurityType model if one does not already exist
            name = item.get("type", "")
            security_type, created = SecurityType.objects.get_or_create(name=name)

            #creating Currency model if one does not already exist
            code = item.get("iso_currency_code", "")
            currency, created = Currency.objects.get_or_create(code=code)

            kwargs = {
                "is_cash_equivalent": item.get("is_cash_equivalent", ""),
                "type": security_type,
                "close_price": item.get("close_price", ""), "close_price_as_of": item.get("close_price_as_of", ""),
                "currency": currency
            }

            user_security, created = UserSecurity.objects.update_or_create(user_institution=user_institution, security=security, defaults=kwargs)
            user_security.create_snapshot()

        for item in holdings:
            account_id = item.get("account_id", "")
            account = Account.objects.get(account_id=account_id)

            security_id = item.get("security_id", "")
            user_security, created = UserSecurity.objects.get_or_create(security__plaid_security_id=security_id,
                                                                        user_institution=user_institution)

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
        pass


def populate_investment_transactions(user_institution, transactions_data):  # maximum
    #investment transactions are linked a 'Security' model instance

    bulk_create_list = list()
    for transaction in transactions_data["investment_transactions"]:
        kwargs = dict()
        account_id = transaction.get("account_id", "")
        account = Account.objects.get(account_id=account_id)

        if UserSecurity.objects.filter(user_institution=user_institution, security__plaid_security_id=transaction["security_id"]).exists():
            user_security = UserSecurity.objects.get(user_institution=user_institution, security__plaid_security_id=transaction["security_id"])

            iso_currency_code = transaction.get("iso_currency_code", "")
            currency, created = Currency.objects.get_or_create(code=iso_currency_code)
            amount = transaction.get("amount", "")
            quantity = transaction.get("quantity", "")
            fees = transaction.get("fees", "")
            transaction_date = transaction.get("date", "")
            name = transaction.get("name", "")
            investment_transaction_id = transaction.get("investment_transaction_id", "")
            type = transaction.get("type", "")
            type, created = InvestmentTransactionType.objects.get_or_create(name=type)
            cancel_transaction_id = transaction.get("cancel_transaction_id", "")

            kwargs["user_security"] = user_security
            kwargs["account"] = account
            kwargs["amount"] = amount
            kwargs["quantity"] = quantity
            kwargs["fees"] = fees
            kwargs["currency"] = currency
            kwargs["name"] = name
            kwargs["plaid_inv_transaction_id"] = investment_transaction_id
            kwargs["type"] = type
            kwargs["date"] = transaction_date
            kwargs["cancel_transaction_id"] = cancel_transaction_id

            holding = Holding.objects.get(user_security=user_security)

            # ThinkorSwim does not provide cost basis, so it can be computed here:
            if not quantity == 0 and holding.cost_basis == 0 and holding.user.security.type != "cash":
                """ Check for quantity != 0 to avoid div. by zero error. Any holding without cost
                basis and not of type cash, which behaves differently."""
                holding.cost_basis = amount / quantity
                holding.save()
            elif holding.user_security.type == 'cash' and holding.cost_basis == 0:
                # For cash holdings, cost basis equal to institution price
                holding.cost_basis = holding.institution_price
                holding.save()

            #Checks to see that transactions do not already exist in the database
            if not InvestmentTransaction.objects.filter(plaid_inv_transaction_id=investment_transaction_id).exists():
                bulk_create_list.append(InvestmentTransaction(**kwargs))
        else:
            # User sold Security, skip adding this transaction
            continue

    if bulk_create_list:
        InvestmentTransaction.objects.bulk_create(bulk_create_list)

    total_transactions = transactions_data["total_investment_transactions"]

    pass
