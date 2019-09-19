from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from hornescalculator.forms import DisplayForm
from hornescalculator.models import Display, Tax, Housing, Car, Utilities, Food, Miscellaneous
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from institutions.models import Institution, UserInstitution



@login_required
def about(request):
    return render(request, 'automonus/about.html')


def marketing(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("about"))
    return render(request, 'automonus/marketing.html')


class UpdateDisplay(generic.UpdateView):
    model = Display
    template_name = 'automonus/update_display.html'
    fields = ['display']
    success_url = reverse_lazy('overview')
