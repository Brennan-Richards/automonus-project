from plaid import Client
from django.conf import settings
import stripe
from institutions.models import UserInstitution
from accounts.models import Account
class StripleManager():
    default_client = Client(client_id=settings.PLAID_CLIENT_ID,
                            secret=settings.PLAID_SECRET,
                            public_key=settings.PLAID_PUBLIC_KEY,
                            environment=settings.PLAID_ENV)

    def __init__(self,
                 account_uuid,
                 client=default_client,
                 stripe_pk=settings.STRIPE_PUBLIC_KEY,
                 stripe_sk=settings.STRIPE_SECRET_KEY):
        self.account_uuid = account_uuid
        self.client = client
        self.stripe_pk = stripe_pk
        self.stripe_sk = stripe_sk


    def __create_access_token(self, public_token):
        exchange_token_response = self.client.Item.public_token.exchange(public_token)
        return exchange_token_response['access_token']


    def __create_bank_account_token(self, access_token, account_id):
        print(account_id)
        stripe_response = self.client.Processor.stripeBankAccountTokenCreate(access_token, account_id)
        return stripe_response['stripe_bank_account_token']

    def deposit_payment(self, currency, amount):
        account = Account.objects.get(uuid=self.account_uuid)
        pub_resp = self.client.Item.public_token.create(account.user_institution.access_token)
        access_token = self.__create_access_token(public_token=pub_resp.get('public_token'))
        bank_account_token = self.__create_bank_account_token(access_token=access_token, account_id=account.account_id)
        stripe.api_key = self.stripe_sk
        # Create a Customer
        customer = stripe.Customer.create(
            source=bank_account_token,
            description="Example customer" #TODO Change Name to user
        )
        customer_id = customer.id
        default_source = customer.default_source
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            customer=customer_id # Previously stored, then retrieved
        )
        print('charge', charge)
        return charge