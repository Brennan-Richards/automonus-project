from plaid import Client
from django.conf import settings
import stripe
import time
from institutions.models import UserInstitution
from accounts.models import Account, AccountNumber
from django.utils import timezone
import datetime
from payments.models import PaymentOrder
from decimal import Decimal

class StripleManager:
    default_client = Client(
        client_id=settings.PLAID_CLIENT_ID,
        secret=settings.PLAID_SECRET,
        public_key=settings.PLAID_PUBLIC_KEY,
        environment=settings.PLAID_ENV,
    )

    def __init__(
        self,
        account_uuid,
        client=default_client,
        stripe_pk=settings.STRIPE_PUBLIC_KEY,
        stripe_sk=settings.STRIPE_SECRET_KEY,
    ):
        self.account_uuid = account_uuid
        self.client = client
        self.stripe_pk = stripe_pk
        self.stripe_sk = stripe_sk
        stripe.api_key = self.stripe_sk

    def __create_access_token(self, public_token):
        exchange_token_response = self.client.Item.public_token.exchange(public_token)
        return exchange_token_response["access_token"]

    def __create_bank_account_token(self, access_token, account_id):
        stripe_response = self.client.Processor.stripeBankAccountTokenCreate(
            access_token, account_id
        )
        return stripe_response["stripe_bank_account_token"]

    def get_last_tx(self):
        account = Account.objects.get(uuid=self.account_uuid)
        access_token = account.user_institution.access_token
        now = timezone.now().date()
        start_date = now - datetime.timedelta(days=1)
        start_date = now.strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        try:
            transactions_data = self.client.Transactions.get(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                offset=0,
                count=100,
            )
        except Exception as e:
            print(e)
            return False
        return transactions_data

    def __stripe_create_customer(self, *args, **kwargs):
        # Create a Customer
        bank_account_token = kwargs.get("bank_account_token", "")
        customer = stripe.Customer.create(
            source=bank_account_token,
            description="Example customer",  # TODO Change Name to user
        )
        return customer

    def __get_account_individual(self, access_token, account_id, currency="usd"):
        dest_identity_data = self.client.Identity.get(access_token)
        dest_accounts_identity = dest_identity_data.get('accounts', None)

        individual_external_account = {}
        for account in dest_accounts_identity:
            if account['account_id'] == account_id:
                balances = account.get('balances', None)
                owners = account.get('owners', None)
                if owners:
                    addresses = owners[0].get('address', [])
                    for address in addresses:
                        if address.get('primary', False):
                            individual_external_account['address'] = {
                                'city': address.get('city', ''),
                                'country': 'US',  # US ACH support only for USA accounts
                                'line1': address.get('street', ''),
                                'postal_code': address.get('postal_code', ''),
                                'state': address.get('region', ''),
                            }

                    emails = owners[0].get('emails', [])
                    for email in emails:
                        if email.get('primary', False):
                            individual_external_account['email'] = email.get('data', '')

                    phone_numbers = owners[0].get('phone_numbers', [])
                    for phone in phone_numbers:
                        if phone.get('primary', False):
                            individual_external_account['phone'] = phone.get('data', '')

                    names = owners[0].get('names', [])
                    if names:
                        name = names[0].split()
                        individual_external_account['last_name'] = name[-1]
                        name.remove(name[-1])
                        individual_external_account['first_name'] = ' '.join(name)  #concat other names
        individual_external_account['dob'] = {
                'day': '31',
                'month': '5',
                'year': '1948',
        }
        return individual_external_account

    def deposit_payment(self, currency, amount, app_fee=0):
        account = Account.objects.get(uuid=self.account_uuid)
        pub_resp = self.client.Item.public_token.create(
            account.user_institution.access_token
        )
        access_token = self.__create_access_token(
            public_token=pub_resp.get("public_token")
        )
        bank_account_token = self.__create_bank_account_token(
            access_token=access_token, account_id=account.account_id
        )
        # Create a Customer
        customer = self.stripe.Customer.create(
            source=bank_account_token,
            description="Example customer",  # TODO Change Name to user
        )
        customer_id = customer.id
        default_source = customer.default_source
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            customer=customer_id,  # Previously stored, then retrieved
        )
        return charge

    def transfer_between_accounts(self, dest_account_uuid, amount, currency="usd", app_fee=0):
        # get accounts
        src_account = Account.objects.get(uuid=self.account_uuid)
        dest_account = Account.objects.get(uuid=dest_account_uuid)

        # get public token
        src_pub_resp = self.client.Item.public_token.create(
            src_account.user_institution.access_token
        )
        dest_account_resp = self.client.Item.public_token.create(
            dest_account.user_institution.access_token
        )
        # access token
        src_access_token = self.__create_access_token(
            public_token=src_pub_resp.get("public_token")
        )
        dest_access_token = self.__create_access_token(
            public_token=dest_account_resp.get("public_token")
        )
        # bank_account token
        src_bank_account_token = self.__create_bank_account_token(
            access_token=src_access_token, account_id=src_account.account_id
        )
        dest_bank_account_token = self.__create_bank_account_token(
            access_token=dest_access_token, account_id=dest_account.account_id
        )
        # Create a Customers
        src_customer = self.__stripe_create_customer(
            bank_account_token=src_bank_account_token
        )

        # create dest account
        individual_data = self.__get_account_individual(access_token=dest_access_token,
                                      account_id=dest_account.account_id)

        des_number = AccountNumber.objects.get(
            account=dest_account, number_type=AccountNumber.ACH
        )

        external_account_test = {
            "object": "bank_account",
            "country": "US",  # US ACH support only for USA accounts
            "account_number": '000123456789',
            "routing_number": '110000000',
            "currency": dest_account.currency.code,
        }

        external_account={
            "object": "bank_account",
            "country": "US",  # US ACH support only for USA accounts
            "account_number": des_number.number_id,
            "routing_number": des_number.number_routing,
            "currency": dest_account.currency.code,
        }

        dest_connect_account = stripe.Account.create(
            country="US",
            type="custom",
            default_currency="usd",
            business_type="individual",
            external_account=external_account_test if settings.ACH_STRIPE_TEST else external_account,
            individual=individual_data,
            requested_capabilities=["legacy_payments"],
        )

        dest_bank_account = stripe.Account.create_external_account(
            external_account=dest_bank_account_token, id=dest_connect_account.id
        )

        stripe.Account.modify(
            dest_bank_account["account"],
            tos_acceptance={
                "date": int(time.time()),
                "ip": "8.8.8.8",  # Depends on what web framework you're using
            },
        )

        charge = stripe.Charge.create(
            amount=amount,
            application_fee_amount=app_fee,
            currency=currency,
            customer=src_customer.id,
            destination=dest_bank_account["account"],
        )

        po = PaymentOrder.objects.create(
            from_account=src_account,
            to_account=dest_account,
            amount=Decimal(amount) / 100,
            fee=Decimal(app_fee) / 100,
            tx_id=charge.get('id', ''),
            customer=charge.get('customer', ''),
            destination=charge.get('destination', ''),
            description=charge.get('description', ''),
            status=charge.get('description', 'failure'),
        )
        return po
