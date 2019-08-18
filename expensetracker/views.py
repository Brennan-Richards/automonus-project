from django.shortcuts import render, redirect
from django.http import HttpResponse
from expensetracker.models import Income, Tax, Housing, Car, Utilities, Food, Miscellaneous
from .forms import IncomeForm, TaxForm, HousingForm, CarForm, UtilitiesForm, FoodForm, MiscellaneousForm
from django.views import generic
from django.urls import reverse_lazy

from decimal import *
import requests
import json

# Create your views here.


# Income views.

def income(request):
    incomeform = IncomeForm(request.POST or None)

    if incomeform.is_valid():
        income = incomeform.save(commit=False)
        income.user = request.user
        income.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/income.html', {'form':incomeform})

class DetailIncome(generic.DetailView):
    model = Income
    template_name = 'expensetracker/income_details.html'

class UpdateIncome(generic.UpdateView):
    model = Income
    template_name = 'expensetracker/income_update.html'
    fields = ['salary', 'paycheck_period']
    success_url = reverse_lazy('automonus_content')

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

        response = requests.post('https://taxee.io/api/v2/calculate/2019', headers=headers, data=data)

        json_response = response.json()

        print(json_response)

        tax.fica = json_response['annual']['fica']['amount']
        tax.annual_state_tax = json_response['annual']['state']['amount']
        tax.annual_federal_tax = json_response['annual']['federal']['amount']

        tax.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/tax.html', {'form':taxform})

class DetailTax(generic.DetailView):
    model = Tax
    template_name = 'expensetracker/tax_details.html'

class UpdateTax(generic.UpdateView):
    model = Tax
    template_name = 'expensetracker/tax_update.html'
    form_class = TaxForm
    success_url = reverse_lazy('automonus_content')

    def form_valid(self, form):

        form.save(commit=False)

        filing_status = str(form.cleaned_data['filing_status'])
        state = str(form.cleaned_data['state'])
        exemptions = str(form.cleaned_data['dependents'])
        pay_rate = str(form.cleaned_data['pay_rate'])

        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjVkMzI4NDE4NDRmMzYwMWEyODMwYjI3YyIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTU2MzU5MTcwNH0.CvvzJUxbg2wbU56KqUvZ87k8nLz9XJ263QBG10sFjwo',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
          'state': form.cleaned_data['state'],
          'filing_status': form.cleaned_data['filing_status'],
          'pay_periods': form.cleaned_data['periods'],
          'pay_rate': form.cleaned_data['pay_rate'],
          'exemptions': form.cleaned_data['dependents'],
        }

        response = requests.post('https://taxee.io/api/v2/calculate/2019', headers=headers, data=data)

        json_response = response.json()

        print(json_response)

        form.fica = json_response['annual']['fica']['amount']
        form.annual_state_tax = json_response['annual']['state']['amount']
        form.annual_federal_tax = json_response['annual']['federal']['amount']

        form.save()

        return redirect('automonus_content')


# Expense views.

def housing(request):
    housingform = HousingForm(request.POST or None)

    if housingform.is_valid():
        housing = housingform.save(commit=False)
        housing.user = request.user
        housing.annual_cost = housing.yearly_total()
        housing.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/housing.html', {'form':housingform})

class DetailHousing(generic.DetailView):
    model = Housing
    template_name = 'expensetracker/housing_details.html'

class UpdateHousing(generic.UpdateView):
    model = Housing
    template_name = 'expensetracker/housing_update.html'
    form_class = HousingForm
    success_url = reverse_lazy('automonus_content')

    def form_valid(self, form):
        housing_update = form.save(commit=False)
        housing_upate.annual_cost = housing_update.yearly_total()
        housing.save()
        return redirect('automonus_content')

def car(request):
    carform = CarForm(request.POST or None)

    if carform.is_valid():
        car = carform.save(commit=False)
        car.user = request.user
        car.annual_cost = car.yearly_total()
        car.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/car.html', {'form':carform})

class DetailCar(generic.DetailView):
    model = Car
    template_name = 'expensetracker/car_details.html'

class UpdateCar(generic.UpdateView):
    model = Car
    template_name = 'expensetracker/car_update.html'
    fields = ['gas', 'gas_pay_per', 'maintenance', 'maintenance_pay_per', 'car_insurance',
    'carinsurance_pay_per', 'car_property_tax', 'carproptax_pay_per']
    success_url = reverse_lazy('automonus_content')

def utilities(request):
    utilitiesform = UtilitiesForm(request.POST or None)

    if utilitiesform.is_valid():
        utility = utilitiesform.save(commit=False)
        utility.user = request.user
        utility.annual_cost = utility.yearly_total()
        utility.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/utilities.html', {'form':utilitiesform})

class DetailUtilities(generic.DetailView):
    model = Utilities
    template_name = 'expensetracker/utilities_details.html'

class UpdateUtilities(generic.UpdateView):
    model = Utilities
    template_name = 'expensetracker/utilities_update.html'
    fields = ['electricity', 'electricity_pay_per', 'heating', 'heating_pay_per',
    'phone', 'phone_pay_per', 'cable', 'cable_pay_per', 'internet', 'internet_pay_per', 'water',
    'water_pay_per']
    success_url = reverse_lazy('automonus_content')

def food(request):
    foodform = FoodForm(request.POST or None)

    if foodform.is_valid():
        food = foodform.save(commit=False)
        food.user = request.user
        food.annual_cost = food.yearly_total()
        food.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/food.html', {'form':foodform})

class DetailFood(generic.DetailView):
    model = Food
    template_name = 'expensetracker/food_details.html'

class UpdateFood(generic.UpdateView):
    model = Food
    template_name = 'expensetracker/food_update.html'
    fields = ['groceries', 'groceries_pay_per', 'restaurant_food_costs', 'restaurant_pay_per']
    success_url = reverse_lazy('automonus_content')


def miscellaneous(request):
    miscellaneousform = MiscellaneousForm(request.POST or None)

    if miscellaneousform.is_valid():
        miscellaneous = miscellaneousform.save(commit=False)
        miscellaneous.user = request.user
        miscellaneous.annual_cost = miscellaneous.yearly_total()
        miscellaneous.save()
        return redirect('automonus_content')

    return render(request, 'expensetracker/miscellaneous.html', {'form':miscellaneousform})

class DetailMiscellaneous(generic.DetailView):
    model = Miscellaneous
    template_name = 'expensetracker/miscellaneous_details.html'

class UpdateMiscellaneous(generic.UpdateView):
    model = Miscellaneous
    template_name = 'expensetracker/miscellaneous_update.html'
    fields = ['health_insurance', 'healthinsurance_pay_per', 'life_insurance', 'lifeinsurance_pay_per',
    'clothing', 'clothing_pay_per']
    success_url = reverse_lazy('automonus_content')
