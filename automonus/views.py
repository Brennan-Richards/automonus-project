from django.shortcuts import render
from django.http import HttpResponse
from expensetracker.models import Income, Housing, Car, Utilities, Food, Miscellaneous
from django.contrib import auth

# Create your views here.

def home(request):
        return render(request, 'home.html')
