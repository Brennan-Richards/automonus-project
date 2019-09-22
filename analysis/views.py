from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from accounts.models import Account, Transaction
from django.db.models import Avg, Count, Min, Sum
import json
from .utils import ChartData
from users.models import Profile
from investments.models import Holding, InvestmentTransaction
from django.contrib.auth.decorators import login_required


@login_required
def income_overview(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        charts_data = ChartData().get_charts_data(user=user, chart_type="pie", category="income")
        context = {"charts_data": charts_data}
    return render(request, 'analysis/income_overview.html', context)


@login_required
def spending_overview(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["depository", "credit"]
        charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="spending",
                                                  account_types=account_types)
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__gt=0,
                                                  account__user_institution__is_active=True
                                                  ).order_by("-date")[:100]
        transactions_total = ChartData().get_transactions_sum(user=user, account_types=account_types)
        context = {"charts_data": charts_data, "transactions": transactions, "transactions_total": transactions_total}
    return render(request, 'analysis/spending_overview.html', context)


@login_required
def liabilities_overview(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["loan"]
        charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="liabilities",
                                                  account_types=account_types)
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__gt=0,
                                                  account__user_institution__is_active=True
                                                  ).order_by("-id")[:100]
        accounts = Account.objects.filter(user_institution__user=user, type__name__in=account_types,
                                            user_institution__is_active=True) \
                                            .aggregate(total=Sum("current_balance"))
        total_balance = round(accounts["total"] if accounts.get("total") else 0, 2)
        context = {"total_balance": total_balance, "charts_data": charts_data, "transactions": transactions}
    return render(request, 'analysis/liabilities_overview.html', context)


@login_required
def savings_overview(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["depository"]
        accounts = Account.objects.filter(user_institution__user=user, type__name__in=account_types,
                                            user_institution__is_active=True) \
            .aggregate(total=Sum("current_balance"))
        total_balance = round(accounts["total"] if accounts.get("total") else 0, 2)
        charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="savings",
                                                  account_types=account_types)
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__lt=0,
                                                  account__user_institution__is_active=True).order_by("-date")[:100]
        context = {"charts_data": charts_data, "total_balance": total_balance, "transactions": transactions}
    return render(request, 'analysis/savings_overview.html', context)


@login_required
def investments_overview(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["investment"]
        user_holdings = Holding.objects.filter(account__user_institution__user=user,
                                                account__user_institution__is_active=True).aggregate(total_amount=Sum("institution_value"))
        total_amount = user_holdings["total_amount"] if user_holdings.get("total_amount") else 0
        total_investments = round(total_amount, 2)

        investment_transactions = InvestmentTransaction.objects.filter(account__user_institution__user=user,
                                                                        account__user_institution__is_active=True)[:100]
        charts_data = ChartData().get_charts_data(user=user, chart_type="line", category="investments", account_types=account_types)
        context = {"charts_data": charts_data, "total_investments": total_investments,
                   "investment_transactions": investment_transactions}
    return render(request, 'analysis/investments_overview.html', context)
