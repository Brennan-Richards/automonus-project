from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from institutions.models import Institution, UserInstitution
from accounts.models import Transaction
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData

# Create your views here.

def home(request):
    return render(request, 'automonus/home.html')

def login_signup(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("master_dashboard"))
    return render(request, 'automonus/login_signup.html')

@login_required
def master_dashboard(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["depository"]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="line", category="accounts",
                                                            account_types=account_types)
        context = {"charts_data": charts_data}
    return render(request, 'automonus/master_dashboard.html', context)


# from hornescalculator.forms import DisplayForm
# from expenditures.models import Display

# class UpdateDisplay(generic.UpdateView):
#     model = Display
#     template_name = 'automonus/update_display.html'
#     fields = ['display']
#     success_url = reverse_lazy('overview')
