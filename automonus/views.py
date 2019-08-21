from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse

# Create your views here.

def home(request):

    return render(request, 'automonus/home.html')
