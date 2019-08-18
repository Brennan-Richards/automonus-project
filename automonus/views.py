from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from expensetracker.forms import DisplayForm
from expensetracker.models import Display, Income, Tax, Housing, Car, Utilities, Food, Miscellaneous
import urllib

# Create your views here.

def content(request):

    displayform = DisplayForm(request.POST or None)

    if displayform.is_valid():
        display = displayform.save(commit=False)
        display.user = request.user
        display.save()
        return redirect('automonus_content')

    return render(request, 'automonus/automonus_content.html', {'form':displayform})

class UpdateDisplay(generic.UpdateView):
    model = Display
    template_name = 'automonus/update_display.html'
    fields = ['display']
    success_url = reverse_lazy('automonus_content')
