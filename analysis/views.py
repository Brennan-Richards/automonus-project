from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from accounts.models import Account, Transaction
from django.db.models import Avg, Count, Min, Sum
import json
from .utils import ChartData
from users.models import Profile
from investments.models import Holding, InvestmentTransaction


def income_overview(request):
    user = request.user
    Profile.objects.get_or_create(user=user)
    charts_data = ChartData().get_charts_data(user=user, chart_type="pie", category="income")
    context = {"charts_data": charts_data}
    return render(request, 'analysis/income_overview.html', context)


def spending_overview(request):
    user = request.user
    charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="spending")
    transactions = Transaction.objects.filter(account__user_institution__user=user,
                                              account__type__name="credit", amount__gt=0
                                              ).order_by("-id")[:100]
    context = {"charts_data": charts_data, "transactions": transactions}
    return render(request, 'analysis/spending_overview.html', context)


def liabilities_overview(request):
    return render(request, 'analysis/liabilities_overview.html')


def savings_overview(request):
    user = request.user
    accounts = Account.objects.filter(user_institution__user=user, type__name="depository") \
        .aggregate(total=Sum("available_balance"))
    available_balance = round(accounts.get("total", 0), 2)

    charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="savings")
    context = {"charts_data": charts_data, "available_balance": available_balance}
    return render(request, 'analysis/savings_overview.html', context)


def investments_overview(request):
    user = request.user
    user_holdings = Holding.objects.filter(account__user_institution__user=user).aggregate(total_amount=Sum("institution_value"))
    total_investments = round(user_holdings.get("total_amount", 0), 2)
    investment_transactions = InvestmentTransaction.objects.filter(account__user_institution__user=user)[:100]
    charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="investments")
    context = {"charts_data": charts_data, "total_investments": total_investments,
               "investment_transactions": investment_transactions}
    return render(request, 'analysis/investments_overview.html', context)
