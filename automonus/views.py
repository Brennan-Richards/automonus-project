from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

import requests
from plaid import Client
import json
import os

# Create your views here.

PLAID_CLIENT_ID = '5d37fe8b737a4f001252bfd9'
PLAID_SECRET = '176040b1d82a9d35dfc9aca8fe9943'
PLAID_PUBLIC_KEY = '6c5492915411a3645fdd0368516aa9'
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use development to test with live users and credentials and production
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

client = Client(client_id=PLAID_CLIENT_ID,
    secret=PLAID_SECRET,
    public_key=PLAID_PUBLIC_KEY,
    environment=PLAID_ENV
    )

access_token = None

public_token = None

def home(request):

    return render(request, 'automonus/home.html', {'plaid_public_key':PLAID_PUBLIC_KEY, 'plaid_environment':PLAID_ENV})

def get_access_token(request):

    if request.method == 'POST':
        global access_token
        public_token = request.form['public_token']
        #the public token is received from Plaid Link
        response = client.Item.public_token.exchange(public_token)
        access_token = response['access_token']
        print(access_token)
        item = Item.objects.create(token=access_token)
        item.save(commit=False)
        item.user = request.user
        item.save()

        return json.response
