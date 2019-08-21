from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Savings
from django.views import generic
from django.urls import reverse_lazy

# Create your views here.

def savings_overview(request):

    return render(request, 'savings/savings_overview.html')
