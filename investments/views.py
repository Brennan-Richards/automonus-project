from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData
from django.db.models import Sum
from .models import Holding, InvestmentTransaction
from accounts.models import Account

@login_required
def investments_dashboard(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["investment"]
        user_holdings = Holding.objects.filter(account__user_institution__user=user,
                                               account__user_institution__is_active=True).aggregate(total_amount=Sum("institution_value"))
        investment_accounts = Account.objects.filter(user_institution__user=user, type__name__in=account_types,
                                                     user_institution__is_active=True).aggregate(total_amount=Sum("current_balance"))
        total_investments = round(user_holdings["total_amount"], 2) if user_holdings.get("total_amount") else investment_accounts["total_amount"]

        holdings = Holding.objects.filter(account__user_institution__user=user,
                                          account__user_institution__is_active=True)

        investment_transactions = InvestmentTransaction.objects.filter(account__user_institution__user=user,
                                                                       account__user_institution__is_active=True)[:100]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="line", category="investments", account_types=account_types)
        context = {
                   "charts_data": charts_data, "total_investments": total_investments,
                   "investment_transactions": investment_transactions, "holdings":holdings
                   }
    return render(request, 'investments/investments_dashboard.html', context)
