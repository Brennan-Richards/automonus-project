from django.shortcuts import render, redirect
from django.http import HttpResponse
from expensetracker.models import Income, Housing, Car, Utilities, Food, Miscellaneous
from .forms import IncomeForm, HousingForm, CarForm, UtilitiesForm, FoodForm, MiscellaneousForm
# Create your views here.

def income(request):
    incomeform = IncomeForm(request.POST or None)

    if incomeform.is_valid():
        income = incomeform.save(commit=False)
        income.user = user
        income.save()
        return redirect('home')

    return render(request, 'expensetracker/income.html', {'form':incomeform})

def housing(request):
    housingform = HousingForm(request.POST or None)

    if housingform.is_valid():
        housing = housingform.save(commit=False)
        housing.user = user
        housing.save()
        return redirect('home')

    return render(request, 'expensetracker/housing.html', {'form':housingform})

def car(request):
    carform = CarForm(request.POST or None)

    if carform.is_valid():
        car = carform.save(commit=False)
        car.user = user
        car.save()
        return redirect('home')

    return render(request, 'expensetracker/car.html', {'form':carform})

def utilities(request):
    utilitiesform = UtilitiesForm(request.POST or None)

    if utilitiesform.is_valid():
        utility = utilitiesform.save(commit=False)
        utility.user = user
        utility.save()
        return redirect('home')

    return render(request, 'expensetracker/utilities.html', {'form':utilitiesform})

def food(request):
    foodform = FoodForm(request.POST or None)

    if foodform.is_valid():
        food = foodform.save(commit=False)
        food.user = user
        food.save()
        return redirect('home')

    return render(request, 'expensetracker/food.html', {'form':foodform})

def miscellaneous(request):
    miscellaneousform = MiscellaneousForm(request.POST or None)

    if miscellaneousform.is_valid():
        miscellaneous = miscellaneousform.save(commit=False)
        miscellaneous.user = user
        miscellaneous.save()
        return redirect('home')

    return render(request, 'expensetracker/miscellaneous.html', {'form':miscellaneousform})
