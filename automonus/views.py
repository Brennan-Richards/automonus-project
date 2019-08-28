from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

import requests
from plaid import Client
import json
import os
from django.contrib.auth.decorators import login_required
from institutions.models import Institution, UserInstitution
from django.conf import settings
from hornescalculator.forms import DisplayForm
from hornescalculator.models import Display, Income, Tax, Housing, Car, Utilities, Food, Miscellaneous

# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use development to test with live users and credentials and production
# to go live

client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)


@login_required
def home(request):
    webhook_url = settings.PLAID_WEBHOOK_URL
    context = {'plaid_public_key': settings.PLAID_PUBLIC_KEY, 'plaid_environment': settings.PLAID_ENV,
               "webhook_url": webhook_url}
    return render(request, 'automonus/home.html', context)


@login_required
def get_access_token(request):
    user = request.user
    if request.method == 'POST':
        data = request.POST.copy()
        public_token = data['public_token']
        #the public token is received from Plaid Link
        response = client.Item.public_token.exchange(public_token)
        item_id = response["item_id"]  # unique id for combination of user + institution
        access_token = response['access_token']
        institution_name = data["metadata[institution][name]"]
        institution_id = data["metadata[institution][institution_id]"]
        institution, created = Institution.objects.update_or_create(plaid_id=institution_id,
                                                                        defaults={"name": institution_name}
                                                                    )
        user_institution, created = UserInstitution.objects.update_or_create(plaid_id=item_id,
                                                                             user=user, institution=institution,
                                                                        defaults={"access_token": access_token}
                                                                    )

        """
        Some products can be unavailable for the chosen institution, if they were not included on js side, like docs say
        about this:
        
        'A list of Plaid product(s) you wish to use. 
        Valid products are: transactions, auth, identity, income, assets, investments, and liabilities. 
        Only institutions that support all requested products will be shown. 
        In Production, you will be billed for each product that you specify when initializing Link.'
        """
        user_institution.populate_income_information()
        user_institution.populate_accounts()
        # user_institution.populate_transactions()  # this is triggered when the webhook call is received
        return JsonResponse({"status": "success"})


@login_required
def about(request):
    return render(request, 'automonus/about.html')


def marketing(request):
    if user.is_authenticated:
        return redirect(request, 'automonus/hornescalculator.html')
    return render(request, 'automonus/marketing.html')


class UpdateDisplay(generic.UpdateView):
    model = Display
    template_name = 'automonus/update_display.html'
    fields = ['display']
    success_url = reverse_lazy('overview')

