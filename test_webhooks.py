import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'automonus.settings.development'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
import django
django.setup()
from automonus.settings import development as settings
from institutions.models import UserInstitution
import time
from django.utils import timezone
import datetime

from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)

# a = client.Item.webhook.update(access_token="access-sandbox-9ecc948d-8468-472c-b3fc-4ce772c6bac2",
#                            webhook="https://f24727c3.ngrok.io/accounts/webhook-handler/")
# print("response")
#
# print(a)

"""
user_institution = UserInstitution.objects.get(plaid_id="XXyXBdgVeDCal8PyVKwgtWRazZQP4NfdX9kQP")
offset = 0
now = timezone.now().date()
start_date = now - datetime.timedelta(days=365*3)
while True:
    result = user_institution.populate_transactions(start_date=start_date, offset=offset)
    if not result:
        break
    offset += 500  # 500 is the maximum value for count so it is the maximum step value for offset
"""

