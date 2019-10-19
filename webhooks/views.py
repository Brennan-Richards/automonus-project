from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from institutions.models import UserInstitution
from django.utils import timezone
import datetime
from django.conf import settings
import stripe
from payments.models import PaymentOrder

@csrf_exempt
def webhook_handler(request):
    """Information about webhooks: https://support.plaid.com/hc/en-us/articles/360008414233-Webhook-overview
    Webhook url should be specified on frontend side while authentication a user to an institution(bank):
    parameter 'webhook' of Plaid.create()

    'available_products': ['assets', 'auth', 'balance', 'credit_details', 'identity', 'investments', 'liabilities']

    According to this doc, it looks like production environment of plaid needs some data to calculate main items
    like income, assets etc. When item's data is ready, webhook is fired:
    https://support.plaid.com/hc/en-us/articles/360008413893-Income-webhooks

    Information about transactions webhooks:
    https://support.plaid.com/hc/en-us/articles/360010526393-Transactions-webhooks
    """
    print("webhook received!")
    data = json.loads(request.body)
    print(data)

    item_id = data["item_id"]
    user_insitution = UserInstitution.objects.get(plaid_id=item_id)

    if data["webhook_type"] == "INCOME":
        print("INCOME webhook")
        if data["webhook_code"] == "PRODUCT_READY":
            print("income webhook 'Product Ready'")

    elif data["webhook_type"] == "TRANSACTIONS":
        print("Transactions webhook")
        if data["webhook_code"] == "INITIAL_UPDATE":
            """Plaid fires the INITIAL_UPDATE webhook when an Item's initial transaction pull has finished. """
            print("transactions initial update")
            user_insitution.populate_transactions_loop_launch()

        elif data["webhook_code"] == "HISTORICAL_UPDATE":
            """After the initial transaction pull is finished, Plaid will begin the historical transaction pull.
            Plaid fires the HISTORICAL_UPDATE webhook when the historical transaction pull for an Item is finished."""
            print("transactions historical update")
            user_insitution.populate_transactions_loop_launch()

        elif data["webhook_code"] == "DEFAULT_UPDATE":
            """The DEFAULT_UPDATE webhook is fired when Plaid fetches new pending or posted transactions for an Item."""
            print("transactions default update")
            user_insitution.populate_transactions_loop_launch()

        elif data["webhook_code"] == "TRANSACTIONS_REMOVED":
            """Plaid sends a TRANSACTIONS_REMOVED webhook when pending or posted transactions have been removed
            from our system."""
            """ToDo: it look like they will just delete a transaction from the list.
            Some functionality to make reverse comparing of transactions in the database and in plaid needs
            to be implemented"""
            print("transactions removed webhook")

    return HttpResponse(status=200)


@csrf_exempt
def stripe_webhook_handler(request):
    """Information about webhooks: 
    """
    print('stripe_webhook_handler')
    payload = request.body
    event = None
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Event.construct_from(
        json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        print('error', e)
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'charge.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        try:
            po = PaymentOrder.objects.get(tx_id=payment_intent.get('id', None))
        except PaymentOrder.DoesNotExist as e:
            print('DoesNotExist')
            return HttpResponse(status=400)
        else:
            po.status = payment_intent.get('status', None)
            po.save()
        # handle_payment_intent_succeeded(payment_intent)
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object # contains a stripe.PaymentMethod
    # ... handle other event types
    else:
        print('payment_intent', event.data.object)
        # Unexpected event type
    return HttpResponse(status=200)
