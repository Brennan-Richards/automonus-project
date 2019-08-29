from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse
from hornescalculator.forms import DisplayForm
from hornescalculator.models import Display, Tax, Housing, Car, Utilities, Food, Miscellaneous


@login_required
def about(request):
    return render(request, 'automonus/about.html')

# @login_required
# def link(request):
#     return render(request, 'automonus/link.html')

def marketing(request):
    user = request.user
    if user.is_authenticated:
        return redirect(request, 'automonus/hornescalculator.html')
    return render(request, 'automonus/marketing.html')


class UpdateDisplay(generic.UpdateView):
    model = Display
    template_name = 'automonus/update_display.html'
    fields = ['display']
    success_url = reverse_lazy('overview')
