from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.urls import reverse_lazy

# Create your views here.

def home(request):

    return render(request, 'academy/home.html')
