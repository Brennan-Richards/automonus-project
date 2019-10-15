from plaid import Client
from django.conf import settings
import stripe

class StripleManager():
    default_client = Client(client_id=settings.PLAID_CLIENT_ID,
                            secret=settings.PLAID_SECRET,
                            public_key=settings.PLAID_PUBLIC_KEY,
                            environment=settings.PLAID_ENV)

    def __init__(self,
                 public_token,
                 account_id,
                 client=default_client,
                 stripe_pk=settings.STRIPE_PUBLIC_KEY,
                 stripe_sk=settings.STRIPE_SECRET_KEY):
        self.public_token = public_token
        self.account_id = account_id
        self.client = client
        self.stripe_pk = stripe_pk
        self.stripe_sk = stripe_sk


    def __create_access_token(self):
        exchange_token_response = self.client.Item.public_token.exchange(self.public_token)
        return exchange_token_response['access_token']


    def __create_bank_account_token(self, access_token):
        stripe_response = self.client.Processor.stripeBankAccountTokenCreate(access_token, self.account_id)
        return stripe_response['stripe_bank_account_token']

    def deposit_payment(self, currency, amount):
        access_token = self.__create_access_token()
        bank_account_token = self.__create_bank_account_token(access_token=access_token)
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