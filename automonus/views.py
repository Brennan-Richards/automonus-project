from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from hornescalculator.forms import DisplayForm
from hornescalculator.models import Display, Tax, Housing, Car, Utilities, Food, Miscellaneous
from django.conf import settings
from django.http import JsonResponse
import requests
from plaid import Client
import json
from institutions.models import Institution, UserInstitution

client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)


@login_required
def about(request):
    return render(request, 'automonus/about.html')


@login_required
def link(request):
    """A page for clicking on the button to start Plaid integration"""
    context = {"webhook_url": settings.PLAID_WEBHOOK_URL}
    return render(request, 'automonus/link.html', context=context)


@login_required
def get_access_token(request):
    print("get access token")
    user = request.user
    if request.method == 'POST':
        data = request.POST.copy()
        public_token = data['public_token']
        # the public token is received from Plaid Link
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
        user_institution.populate_or_update_accounts()

        # getting investments data
        user_institution.populate_securities_and_holdings()
        user_institution.populate_transactions_loop_launch(type="investment_transactions")

        # user_institution.populate_transactions()  # this is triggered when the webhook call is received
        return JsonResponse({"status": "success"})


def marketing(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("about"))
    return render(request, 'automonus/marketing.html')


class UpdateDisplay(generic.UpdateView):
    model = Display
    template_name = 'automonus/update_display.html'
    fields = ['display']
    success_url = reverse_lazy('overview')
