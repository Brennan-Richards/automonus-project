from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Income, IncomeStream
from accounts.models import Account, Transaction
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData
from django.db.models import Sum

# Create your views here.

@login_required
def income_dashboard(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["depository"]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="pie", category="income")
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__lt=0,
                                                  account__user_institution__is_active=True).order_by("date")
        context = {
                    "charts_data": charts_data,
                    "transactions":transactions
                  }
    return render(request, 'income/income_dashboard.html', context)
