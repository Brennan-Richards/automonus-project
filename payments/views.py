from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def enable_payments(request):
    return render(request, 'payments/enable.html')
