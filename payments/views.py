from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views import View
from plaid import Client
import json
import stripe
from payments.stripe_manager import StripleManager
from decimal import Decimal
# Create your views here.

@login_required
def enable_payments(request):
    stripe.api_key = 'sk_test_Cm8UAku0L4hL4G2aOpDMIM7r00iBv2frlo'
    return render(request, 'payments/enable.html')


class StripeChecker(View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        # Look up the author we're interested in.
        currency = request.POST.get('currency', None)
        amount = int(Decimal(request.POST.get('amount', None)) * 100)
        public_token = request.POST.get('public_token', None)
        account_id = request.POST.get('account_id', None)
        print(amount)
        # if amount < 50:
        #     return HttpResponseBadRequest(content='amount must be more than 0.5$')
        sm =  StripleManager(public_token=public_token,
                             account_id=account_id)
        try:
            resp = sm.deposit_payment(currency=currency,
                               amount=amount)
        except Exception as e: 
            return HttpResponseBadRequest(content=f'{e}')
        return  JsonResponse({"status": resp})