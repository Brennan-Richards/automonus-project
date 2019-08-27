from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Display, Tax, Income, Housing, Car, Utilities, Food, Miscellaneous
from .forms import DisplayForm, TaxForm, IncomeForm, HousingForm, CarForm, UtilitiesForm, FoodForm, MiscellaneousForm
from django.views import generic
from django.urls import reverse_lazy

from decimal import *
import requests
import json

# Create your views here.

@login_required
def overview(request):

    displayform = DisplayForm(request.POST or None)

    if displayform.is_valid():
        display = displayform.save(commit=False)
        display.user = request.user
        display.save()
        return redirect('overview')

    return render(request, 'hornescalculator/overview.html', {'form':displayform})

# Income views.

@login_required
def income(request):
    incomeform = IncomeForm(request.POST or None)

    if incomeform.is_valid():
        income = incomeform.save(commit=False)
        income.user = request.user
        income.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/income.html', {'form':incomeform})

class DetailIncome(generic.DetailView):
    model = Income
    template_name = 'hornescalculator/data/income_details.html'

class UpdateIncome(generic.UpdateView):
    model = Income
    template_name = 'hornescalculator/data/income_update.html'
    fields = ['salary', 'paycheck_period']
    success_url = reverse_lazy('overview')

@login_required
def tax(request):
    taxform = TaxForm(request.POST or None)

    if taxform.is_valid():
        tax = taxform.save(commit=False)
        tax.user = request.user

        filing_status = str(taxform.cleaned_data['filing_status'])
        state = str(taxform.cleaned_data['state'])
        exemptions = str(taxform.cleaned_data['dependents'])
        pay_rate = str(taxform.cleaned_data['pay_rate'])

        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjVkMzI4NDE4NDRmMzYwMWEyODMwYjI3YyIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTU2MzU5MTcwNH0.CvvzJUxbg2wbU56KqUvZ87k8nLz9XJ263QBG10sFjwo',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
          'state': taxform.cleaned_data['state'],
          'filing_status': taxform.cleaned_data['filing_status'],
          'pay_periods': taxform.cleaned_data['periods'],
          'pay_rate': taxform.cleaned_data['pay_rate'],
          'exemptions': taxform.cleaned_data['dependents'],
        }

        response = requests.post('https:/taxee.io/api/v2/calculate/2019', headers=headers, data=data)

        json_response = response.json()

        print(json_response)

        tax.fica = json_response['annual']['fica']['amount']
        tax.annual_state_tax = json_response['annual']['state']['amount']
        tax.annual_federal_tax = json_response['annual']['federal']['amount']

        tax.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/tax.html', {'form':taxform})

class DetailTax(generic.DetailView):
    model = Tax
    template_name = 'hornescalculator/data/tax_details.html'

class UpdateTax(generic.UpdateView):
    model = Tax
    template_name = 'hornescalculator/data/tax_update.html'
    form_class = TaxForm
    success_url = reverse_lazy('overview')

    def form_valid(self, form):

        tax_update = form.save(commit=False)

        filing_status = str(tax_update.cleaned_data['filing_status'])
        state = str(tax_update.cleaned_data['state'])
        exemptions = str(tax_update.cleaned_data['dependents'])
        pay_rate = str(tax_update.cleaned_data['pay_rate'])

        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjVkMzI4NDE4NDRmMzYwMWEyODMwYjI3YyIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTU2MzU5MTcwNH0.CvvzJUxbg2wbU56KqUvZ87k8nLz9XJ263QBG10sFjwo',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
          'state': tax_update.cleaned_data['state'],
          'filing_status': tax_update.cleaned_data['filing_status'],
          'pay_periods': tax_update.cleaned_data['periods'],
          'pay_rate': tax_update.cleaned_data['pay_rate'],
          'exemptions': tax_update.cleaned_data['dependents'],
        }

        response = requests.post('https://taxee.io/api/v2/calculate/2019', headers=headers, data=data)

        json_response = response.json()

        print(json_response)

        tax_update.fica = json_response['annual']['fica']['amount']
        tax_update.annual_state_tax = json_response['annual']['state']['amount']
        tax_update.annual_federal_tax = json_response['annual']['federal']['amount']

        tax_update.save()

        return redirect('overview')


# Expense views.
@login_required
def housing(request):
    housingform = HousingForm(request.POST or None)

    if housingform.is_valid():
        housing = housingform.save(commit=False)
        housing.user = request.user
        housing.annual_cost = housing.yearly_total()
        housing.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/housing.html', {'form':housingform})

class DetailHousing(generic.DetailView):
    model = Housing
    template_name = 'hornescalculator/data/housing_details.html'

class UpdateHousing(generic.UpdateView):
    model = Housing
    template_name = 'hornescalculator/data/housing_update.html'
    form_class = HousingForm
    success_url = reverse_lazy('overview')

    def form_valid(self, form):
        housing_update = form.save(commit=False)
        housing_upate.annual_cost = housing_update.yearly_total()
        form.save()
        return redirect('overview')

@login_required
def car(request):
    carform = CarForm(request.POST or None)

    if carform.is_valid():
        car = carform.save(commit=False)
        car.user = request.user
        car.annual_cost = car.yearly_total()
        car.gas = car.get_gas_cost()
        car.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/car.html', {'form':carform})

class DetailCar(generic.DetailView):
    model = Car
    template_name = 'hornescalculator/data/car_details.html'

class UpdateCar(generic.UpdateView):
    model = Car
    template_name = 'hornescalculator/data/car_update.html'
    form_class = CarForm
    success_url = reverse_lazy('overview')

    def form_valid(self, form):
        car_update = form.save(commit=False)
        car_update.annual_cost = car_update.yearly_total()
        car_update.gas = car_update.get_gas_cost()
        car_update.save()
        return redirect('overview')

@login_required
def utilities(request):
    utilitiesform = UtilitiesForm(request.POST or None)

    if utilitiesform.is_valid():
        utility = utilitiesform.save(commit=False)
        utility.user = request.user
        utility.annual_cost = utility.yearly_total()
        utility.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/utilities.html', {'form':utilitiesform})

class DetailUtilities(generic.DetailView):
    model = Utilities
    template_name = 'hornescalculator/data/utilities_details.html'

class UpdateUtilities(generic.UpdateView):
    model = Utilities
    template_name = 'hornescalculator/data/utilities_update.html'
    form_class = UtilitiesForm
    success_url = reverse_lazy('overview')

    def form_valid(self, form):
        utilities_update = form.save(commit=False)
        utilities_upate.annual_cost = utilities_update.yearly_total()
        utilities_update.save()
        return redirect('overview')

@login_required
def food(request):
    foodform = FoodForm(request.POST or None)

    if foodform.is_valid():
        food = foodform.save(commit=False)
        food.user = request.user
        food.annual_cost = food.yearly_total()
        food.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/food.html', {'form':foodform})

class DetailFood(generic.DetailView):
    model = Food
    template_name = 'hornescalculator/data/food_details.html'

class UpdateFood(generic.UpdateView):
    model = Food
    template_name = 'hornescalculator/data/food_update.html'
    form_class = FoodForm
    success_url = reverse_lazy('overview')

    def form_valid(self, form):
        food_update = form.save(commit=False)
        food_upate.annual_cost = food_update.yearly_total()
        food_update.save()
        return redirect('overview')

@login_required
def miscellaneous(request):
    miscellaneousform = MiscellaneousForm(request.POST or None)

    if miscellaneousform.is_valid():
        miscellaneous = miscellaneousform.save(commit=False)
        miscellaneous.user = request.user
        miscellaneous.annual_cost = miscellaneous.yearly_total()
        miscellaneous.save()
        return redirect('overview')

    return render(request, 'hornescalculator/data/miscellaneous.html', {'form':miscellaneousform})

class DetailMiscellaneous(generic.DetailView):
    model = Miscellaneous
    template_name = 'hornescalculator/data/miscellaneous_details.html'

class UpdateMiscellaneous(generic.UpdateView):
    model = Miscellaneous
    template_name = 'hornescalculator/data/miscellaneous_update.html'
    form_class = MiscellaneousForm
    success_url = reverse_lazy('overview')

    def form_valid(self, form):
        misc_update = form.save(commit=False)
        misc_upate.annual_cost = misc_update.yearly_total()
        misc_update.save()
        return redirect('overview')
