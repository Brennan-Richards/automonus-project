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
from institutions.models import UserInstitution
from accounts.models import Account
# Create your views here.

@login_required
def enable_payments(request):
    user = request.user
    available_masks = ['1111', '0000']
    user_institution = UserInstitution.objects.filter(user=user)
    user_accounts = Account.objects.filter(user_institution__in=user_institution, mask__in=available_masks)
    context = {
        'user_institution': user_institution,
        'user_accounts': user_accounts,
    }
    return render(request, 'payments/enable.html', context=context)


class StripeChecker(View):

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        # Look up the author we're interested in.
        currency = request.POST.get('currency', None)
        amount = int(Decimal(request.POST.get('amount', None)) * 100)
        account_uuid = request.POST.get('account_uuid', None)
        # if amount < 50:
        #     return HttpResponseBadRequest(content='amount must be more than 0.5$')
        sm = StripleManager(account_uuid=account_uuid)
        try:
            a = 1
        except Exception as e: 
            return HttpResponseBadRequest(content=f'{e}')
        resp = sm.deposit_payment(currency=currency,
                                  amount=amount)  
        return  JsonResponse({"status": resp})