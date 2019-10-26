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
from liabilities.models import StudentLoan
from income.models import IncomeStream
from investments.models import Holding, InvestmentTransaction
from django.contrib.auth.decorators import login_required


def about_analysis(request):
    return render(request, 'charts/about_analysis.html')
