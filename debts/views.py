from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Debts
from django.views import generic
from django.urls import reverse_lazy

# Create your views here.

def liabilities_overview(request):

    return render(request, 'debts/liabilities_overview.html')
