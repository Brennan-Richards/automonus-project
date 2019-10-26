from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Income
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData

# Create your views here.

@login_required
def income_analysis(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        income_streams = IncomeStream.objects.filter(income__user_institution__user=user,
                                                     income__user_institution__is_active=True)
        #savings data
        account_types = ["depository"]
        accounts = Account.objects.filter(user_institution__user=user, type__name__in=account_types,
                                          user_institution__is_active=True) \
                                          .aggregate(total=Sum("current_balance"))
        total_balance = round(accounts["total"] if accounts.get("total") else 0, 2)
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__lt=0,
                                                  account__user_institution__is_active=True).order_by("-date")[:100]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="pie", category="income", account_types=account_types)
        context = {
                    "charts_data": charts_data,
                    "income_streams":income_streams,
                    "total_balance":total_balance,
                    "transactions":transactions
                  }
    return render(request, 'income/income_analysis.html', context)
