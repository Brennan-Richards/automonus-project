from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
import requests
from plaid import Client
import json
import os
from django.contrib.auth.decorators import login_required
from accounts.models import Institution, UserInstitution
from django.conf import settings

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
    context = {'plaid_public_key': settings.PLAID_PUBLIC_KEY, 'plaid_environment': settings.PLAID_ENV}
    return render(request, 'automonus/home.html', context)


@login_required
def get_access_token(request):
    user = request.user
    if request.method == 'POST':
        data = request.POST.copy()
        public_token = data['public_token']
        #the public token is received from Plaid Link
        response = client.Item.public_token.exchange(public_token)
        access_token = response['access_token']
        institution_name = data["metadata[institution][name]"]
        institution_id = data["metadata[institution][institution_id]"]
        institution, created = Institution.objects.update_or_create(plaid_id=institution_id,
                                                                        defaults={"name": institution_name}
                                                                    )
        user_institution, created = UserInstitution.objects.update_or_create(user=user, institution=institution,
                                                                        defaults={"access_token": access_token}
                                                                    )
        user_institution.populate_income_information()
        user_institution.populate_accounts()
        return JsonResponse({"status": "success"})
