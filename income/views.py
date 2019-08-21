from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Income
from django.views import generic
from django.urls import reverse_lazy

# Create your views here.

def income_overview(request):

    return render(request, 'income/income_overview.html')
