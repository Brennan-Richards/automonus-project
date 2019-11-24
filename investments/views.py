from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData
from django.db.models import Sum
from .models import Holding, InvestmentTransaction, MockInvestment
from accounts.models import Account
from .forms import UpdateMockInvestmentForm

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

@login_required
def investment_calculator(request):
    user = request.user
    context = {}

    mock_investment = MockInvestment.objects.filter(user=user).first()

    if mock_investment:
        form = UpdateMockInvestmentForm(request.POST, instance=mock_investment)
    else:
        form = UpdateMockInvestmentForm(request.POST)

    context["form"] = form

    if form.is_valid():
        investment = form.save(commit=False)
        investment.user = user
        investment.save()

    if mock_investment:
        context["mock_investment"] = mock_investment
        final_value = mock_investment.calculate_return()["final_value"]
        context["final_value"] = final_value
        total_interest_earned = mock_investment.calculate_return()["total_interest_earned"]
        context["total_interest_earned"] = total_interest_earned
        context["total_principal_input"] = round(final_value - total_interest_earned, 2)
        context["last_date"] = mock_investment.calculate_return()["last_date"]
        chart_name = "Projection of mock investment"
        chart_type = "line"
        chart_categories = mock_investment.calculate_return()["growth_series_dates"]
        data = mock_investment.calculate_return()["growth_series"]
        chart_series = [{"name":"Investment Value ($)", "data":data}]
        context["charts_data"] = [{"title": chart_name, "type": chart_type, "categories": chart_categories,
                      "chart_series": chart_series}]

    # else:
    #     create_form = UpdateMockInvestmentForm(request.POST)
    #     context["create_form"] = create_form
    #     if create_form.is_valid():
    #         print(create_form)
    #         create_form.save()


    return render(request, 'investments/investment_calculator.html', context)
