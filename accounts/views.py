from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from accounts.models import Transaction
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData

# Create your views here.

# @login_required
# def accounts_analysis(request):
#     context = dict()
#     user = request.user
#     if user.profile.get_user_institutions():
#         account_types = ["depository"]
#         charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="line", category="savings",
#                                                             account_types=account_types)
#         context = {"charts_data": charts_data}
#     return render(request, 'accounts/accounts_analysis.html', context)
