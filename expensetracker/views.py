from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Expenditures
from django.views import generic
from django.urls import reverse_lazy

from decimal import *
import requests
import json

# Create your views here.


def spending_overview(request):

    return render(request, 'expensetracker/spending_overview.html')
