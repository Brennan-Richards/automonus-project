from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Investments
from django.views import generic
from django.urls import reverse_lazy

# Create your views here.

def investments_overview(request):

    return render(request, 'investments/investments_overview.html')
