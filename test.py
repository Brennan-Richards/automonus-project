import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'automonus.settings.development'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import django
django.setup()
from django.conf import settings
from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)
from investments.models import Security, UserSecurity, Holding, InvestmentTransactionType, \
    InvestmentTransaction, SecurityType
from institutions.models import UserInstitution
from accounts.models import Currency
from django.utils import timezone
import datetime
from accounts.models import Account


access_token = "access-sandbox-de8b021a-22e3-438e-a9f6-5f2d8d38f2f1"  # Wealth Fargo
user_institution = UserInstitution.objects.get(access_token=access_token)
data = client.Holdings.get(access_token)  # this returns both security and holding instances
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
                                                       isin=item["isin"], sedol=item["sedol"], cusip=item["cusip"],)
    security_type, created = SecurityType.objects.get_or_create(name=item["type"])
    currency, created = Currency.objects.get_or_create(code=item["iso_currency_code"])
    kwargs = {
        "plaid_id": security_id,
        "user_institution": user_institution,
        "security": security,
        "is_cash_equivalent": item["is_cash_equivalent"],
        "type": security_type,
        "close_price": item["close_price"], "close_price_as_of": item["close_price_as_of"],
        "currency": currency
    }
    print(kwargs)
    us, created = UserSecurity.objects.get_or_create(**kwargs)
    print(created)

print(holdings)
"""
{'account_id': 'Z1l84PBBKaUzRw36
KBqPsreoddXrk5FgLoJdb', 'cost_basis': 1, 'institution_price': 1, 'institution_price_as_of': None, 
'institution_value': 12345.67, 'iso_currency_code': 'USD', 'quantity': 12345.67, 'se
curity_id': 'd6ePmbPxgWCWmMVv66q9iPV94n91vMtov5Are', 'unofficial_currency_code': None}
"""
for item in holdings:
    security_id = item["security_id"]
    account = Account.objects.get(account_id=item["account_id"])
    user_security, created = UserSecurity.objects.get_or_create(plaid_id=security_id,
                                                                user_institution=user_institution)
    currency, created = Currency.objects.get_or_create(code=item["iso_currency_code"])
    kwargs = {
        "account": account,
        "user_security": user_security,
        "institution_value": item["institution_value"],
        "institution_price": item["institution_price"], "institution_price_as_of": item["institution_price_as_of"],
        "cost_basis": item["cost_basis"],
        "currency": currency,
        "quantity": item["quantity"]
    }
    if user_security.security.name == "Matthews Pacific Tiger Fund Insti Class":
        print(kwargs)
    Holding.objects.get_or_create(**kwargs)


"""
now = timezone.now().date()
days_nmb = 365 * 3
start_date = now - datetime.timedelta(days=days_nmb)
start_date = start_date.strftime("%Y-%m-%d")
end_date = now.strftime("%Y-%m-%d")
transactions_data = client.InvestmentTransactions.get(access_token=access_token, start_date=start_date,
                                                      end_date=end_date, offset=0, count=500)
print(transactions_data)
"""
user_institution.populate_transactions_loop_launch(type="investment_transactions")



