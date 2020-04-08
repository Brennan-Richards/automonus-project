from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from institutions.models import Institution, UserInstitution
from accounts.models import Account, Transaction
from payments.models import PaymentOrder
from accounts.models import Currency, AccountType, AccountSubType
from investments.models import UserSecurity, Security, Holding, TylersAdjustment
from .forms import TylersAdjustmentForm
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils import timezone
from .utilities import *

# Create your views here.

def home(request):
    return render(request, 'automonus/home.html')

def login_signup(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("master_dashboard"))
    return render(request, 'automonus/login_signup.html')

@login_required
def tylers_whiteboards(request):
    context = dict()
    user = request.user

    if user.profile.get_user_institutions():
        holdings = Holding.objects.filter(account__user_institution__user=user, account__user_institution__is_active=True)

        # Get total P/L across all holdings
        aggregate_pl = 0
        for holding in holdings:
            profit_or_loss = holding.institution_value - (holding.cost_basis * holding.quantity)
            aggregate_pl += profit_or_loss

        if len(TylersAdjustment.objects.filter(user=user)) > 0:
            adjustment_obj = TylersAdjustment.objects.get(user=user)
            adjustment_value = adjustment_obj.adjustment
            context["adjustment"] = round(adjustment_value, 2)
            context["real_profit_or_loss"] = round((aggregate_pl + adjustment_value), 2) # adjustment meant to account for profit withdrawn

        context["aggregate_pl"] = round(aggregate_pl, 2)
    return render(request, 'automonus/tylers_whiteboards.html', context)


class TylersAdjustmentCreate(LoginRequiredMixin, CreateView):
    template_name = "automonus/tylers_adjustment_create.html"
    form_class = TylersAdjustmentForm
    success_url = reverse_lazy("tylers_whiteboards")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TylersAdjustmentUpdate(LoginRequiredMixin, UpdateView):
    model = TylersAdjustment
    template_name = "automonus/tylers_adjustment_update.html"
    form_class = TylersAdjustmentForm
    success_url = reverse_lazy("tylers_whiteboards")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


from plaid import Client
client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)

@csrf_exempt
def update_account_info(request):
    if request.method == 'POST':
        # getting investments data
        user_institution = UserInstitution.objects.get(user=request.user, is_active=True)
        access_token = user_institution.access_token


        accounts_response = client.Accounts.get(access_token)
        accounts = accounts_response['accounts']
        # Takes in a list of accounts from response and returns True if accounts created/updated successfully.
        get_or_create_user_accounts(accounts, user_institution)

        data = client.Holdings.get(access_token)
        securities = data["securities"]
        holdings = data["holdings"]
        # Takes in securities and holdings data and returns True if Securities/Holdings created/updated successfully.
        get_or_create_user_holdings_securities(securities, holdings, user_institution)

        start_date = (timezone.now().date() - datetime.timedelta(days=1095)).strftime("%Y-%m-%d")
        end_date = timezone.now().date().strftime("%Y-%m-%d")
        transactions_data = client.InvestmentTransactions.get(access_token=access_token, start_date=start_date,
                                                              end_date=end_date, offset=0, count=500)
        # print(transactions_data)
        # Populate the database with new investment transactions.
        populate_investment_transactions(user_institution, transactions_data)


    return JsonResponse({'status':'success'})


@login_required
def master_dashboard(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["depository"]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="line", category="accounts",
                                                            account_types=account_types)
        # print(charts_data)
        accounts = Account.objects.filter(user_institution__user=user, user_institution__is_active=True,
                                          type__name__in=account_types)
        payment_orders = PaymentOrder.objects.filter(from_account__in=accounts)
        context = {
            "charts_data": charts_data,
            "accounts":accounts,
            "payment_orders": payment_orders
        }
    return render(request, 'automonus/master_dashboard.html', context)
