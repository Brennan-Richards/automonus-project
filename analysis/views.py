from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from accounts.models import Transaction
from django.db.models import Avg, Count, Min, Sum
import json

# Create your views here.

def income_overview(request):

    user = request.user

    # projected_income_after_tax = user.income.projected_yearly_minus_tax
    # projected_yearly_taxes = user.income.projected_yearly_taxes

    return render(request, 'analysis/income_overview.html', {'true_income':projected_yearly_after_tax, 'tax':projected_yearly_taxes})


def spending_overview(request):
    user = request.user
    spending_transactions = Transaction.objects.filter(account__user_institution__user=user, amount__lt=0)\
        .values('date', 'currency__code')\
        .annotate(amount=Sum('amount'))
    data = dict()
    for item in spending_transactions:
        currency_code = item["currency__code"]
        date = item["date"]
        # date = item["date"].strftime("%m/%d/%Y")
        amount = float(item["amount"])
        if not currency_code in data:
            data[currency_code] = dict()
        if not date in data[currency_code]:
            data[currency_code][date] = 0
        data[currency_code][date] += abs(amount)

    chart_series = list()
    chart_categories = list()  # x axis values

    for currency, dates_data in data.items():
        """Adding dates to chart_categories list in order to iterate them while preparing charts data.
        If some date has value for one currencty, but it does not have it for another currency, then 0 value should be
        added instead"""

        """dates_data has a format of {date: amount, date2: amount2}"""
        chart_categories += list(dates_data.keys())  # keys are dates in this dictionary

    chart_categories = sorted(list(set(chart_categories)))  # removing duplicated values and sorting the list

    for currency, dates_data in data.items():
        chart_series_data = list()
        for date in chart_categories:
            if date in dates_data:
                amount = dates_data[date]
            else:
                amount = 0
            chart_series_data.append(amount)

        chart_series.append({
            "name": currency,
            "data": chart_series_data
        })
    chart_categories = [item.strftime("%m/%d/%Y") for item in chart_categories]
    chart_data = {"title": "Spending Overview", "type": "line", "categories": chart_categories, "chart_series": chart_series}
    context = {"chart_data": chart_data}
    return render(request, 'analysis/spending_overview.html', context)


def liabilities_overview(request):
    return render(request, 'analysis/liabilities_overview.html')


def savings_overview(request):
    return render(request, 'analysis/savings_overview.html')


def investments_overview(request):
    return render(request, 'analysis/investments_overview.html')
