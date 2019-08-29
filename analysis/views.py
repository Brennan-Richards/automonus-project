from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy

# Create your views here.

def income_overview(request):

    return render(request, 'analysis/income_overview.html')

def spending_overview(request):

    return render(request, 'analysis/spending_overview.html')

def liabilities_overview(request):

    return render(request, 'analysis/liabilities_overview.html')

def savings_overview(request):

    return render(request, 'analysis/savings_overview.html')

def investments_overview(request):

    return render(request, 'analysis/investments_overview.html')
