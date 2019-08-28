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

access_token = "access-sandbox-4e960511-06e3-4945-93fa-25420c4b5461"
data = client.Income.get(access_token)
print(data)

