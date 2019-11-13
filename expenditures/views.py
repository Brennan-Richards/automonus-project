from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from accounts.models import Transaction
from expenditures.models import BudgetData
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from charts.utils import ChartData

# Create your views here.

@login_required
def expenditures_dashboard(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["depository", "credit"]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="line", category="spending",
                                                            account_types=account_types, date_period_days=30)
        transactions_in_period = Transaction.objects.filter(account__user_institution__user=user,
                                                            account__type__name__in=account_types,
                                                            date__gte=timezone.now()-timedelta(days=30),
                                                            amount__gt= 0, account__user_institution__is_active=True
                                                            ).aggregate(sum=Sum("amount"))
        sum_transactions = round(transactions_in_period.get("sum", ""), 2)
        all_transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__gt=0,
                                                  account__user_institution__is_active=True
                                                  ).order_by("-date")

        context = {"charts_data": charts_data,
                   "all_transactions": all_transactions,
                   "sum_transactions": sum_transactions,
                   }

        if user.profile.planned_life_expenses():
            context["total_living_expenses"] = BudgetData().total_living_expenses(user)

    return render(request, 'expenditures/expenditures_dashboard.html', context)

#Horne's Calculator Views

from .models import Display, Housing, Car, Utilities, Food, Miscellaneous, BudgetData, CustomExpense
from .forms import DisplayForm, HousingForm, CarForm, UtilitiesForm, FoodForm, MiscellaneousForm

@login_required
def hornescalculator_base(request):
    user = request.user
    # displayform = DisplayForm(request.POST or None)
    # user = request.user
    #
    # if displayform.is_valid():
    #     display = displayform.save(commit=False)
    #     display.user = user
    #     display.save()
    #     return redirect('hornescalculator_base')
    user_cars = Car.objects.filter(user=user)
    user_housings = Housing.objects.filter(user=user)
    custom_expenses = CustomExpense.objects.filter(user=user)

    context = { 'user_cars': user_cars,
                'user_housings': user_housings,
                'custom_expenses': custom_expenses }
    if user_cars:
        context["cars_costs"] = BudgetData.get_queryset_costs(user, "Car")
    if user_housings:
        context["housings_costs"] = BudgetData.get_queryset_costs(user, "Housing")

    return render(request, 'hornescalculator/hornescalculator_base.html', context)

# class UpdateDisplay(generic.UpdateView):
#     model = Display
#     template_name = 'automonus/update_display.html'
#     fields = ['display']
#     success_url = reverse_lazy('hornescalculator_base')

class HousingListView(ListView):
    model = Housing
    template_name = "hornescalculator/housing_list.html"
    def get_queryset(self):
        user = self.request.user
        return Housing.objects.filter(account__user_institution__user=user)

class CarListView(ListView):
    model = Car
    template_name = "hornescalculator/car_list.html"
    def get_queryset(self):
        user = self.request.user
        return Car.objects.filter(account__user_institution__user=user)

class CreateCustomExpense(LoginRequiredMixin, CreateView):
    model = CustomExpense
    template_name = 'hornescalculator/data/customexpense_create.html'
    fields = ['name', 'cost_per_pay_period', 'pay_period']
    success_url = reverse_lazy("hornescalculator_base")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.annual_cost = form.instance.get_total_costs()["yearly_total"]
        form.instance.monthly_cost = form.instance.get_total_costs()["monthly_total"]
        form.instance.semimonthly_cost = form.instance.get_total_costs()["semimonthly_total"]
        form.instance.biweekly_cost = form.instance.get_total_costs()["biweekly_total"]
        form.instance.weekly_cost = form.instance.get_total_costs()["weekly_total"]
        form.instance.daily_cost = form.instance.get_total_costs()["daily_total"]
        return super().form_valid(form)

class UpdateCustomExpense(LoginRequiredMixin, UpdateView):
    model = CustomExpense
    template_name = 'hornescalculator/data/customexpense_update.html'
    fields = ['name', 'cost_per_pay_period', 'pay_period']
    success_url = reverse_lazy("hornescalculator_base")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.annual_cost = form.instance.get_total_costs()["yearly_total"]
        form.instance.monthly_cost = form.instance.get_total_costs()["monthly_total"]
        form.instance.semimonthly_cost = form.instance.get_total_costs()["semimonthly_total"]
        form.instance.biweekly_cost = form.instance.get_total_costs()["biweekly_total"]
        form.instance.weekly_cost = form.instance.get_total_costs()["weekly_total"]
        form.instance.daily_cost = form.instance.get_total_costs()["daily_total"]
        return super().form_valid(form)

class CustomExpenseDelete(DeleteView):
    model = CustomExpense
    template_name = 'hornescalculator/data/customexpense_confirm_delete.html'
    success_url = reverse_lazy("hornescalculator_base")

class DetailCustomExpense(LoginRequiredMixin, DetailView):
    model = CustomExpense
    template_name = 'hornescalculator/data/customexpense_details.html'

@login_required
def housing(request):
    housingform = HousingForm(request.POST or None)

    if housingform.is_valid():
        housing = housingform.save(commit=False)
        housing.user = request.user
        housing.annual_cost = housing.get_total_costs()["yearly_total"]
        housing.monthly_cost = housing.get_total_costs()["monthly_total"]
        housing.semimonthly_cost = housing.get_total_costs()["semimonthly_total"]
        housing.biweekly_cost = housing.get_total_costs()["biweekly_total"]
        housing.weekly_cost = housing.get_total_costs()["weekly_total"]
        housing.daily_cost = housing.get_total_costs()["daily_total"]
        housing.save()
        return redirect('hornescalculator_base')

    return render(request, 'hornescalculator/data/housing.html', {'form':housingform})

class DetailHousing(LoginRequiredMixin, DetailView):
    model = Housing
    template_name = 'hornescalculator/data/housing_details.html'

class UpdateHousing(LoginRequiredMixin, UpdateView):
    model = Housing
    template_name = 'hornescalculator/data/housing_update.html'
    form_class = HousingForm
    success_url = reverse_lazy('hornescalculator_base')

    def form_valid(self, form):
        housing_update = form.save(commit=False)
        housing_update.annual_cost = housing_update.get_total_costs()["yearly_total"]
        housing_update.monthly_cost = housing_update.get_total_costs()["monthly_total"]
        housing_update.semimonthly_cost = housing_update.get_total_costs()["semimonthly_total"]
        housing_update.biweekly_cost = housing_update.get_total_costs()["biweekly_total"]
        housing_update.weekly_cost = housing_update.get_total_costs()["weekly_total"]
        housing_update.daily_cost = housing_update.get_total_costs()["daily_total"]
        housing_update.save()
        return redirect('hornescalculator_base')

class HousingDelete(LoginRequiredMixin, DeleteView):
    model = Housing
    template_name = 'hornescalculator/data/housing_confirm_delete.html'
    success_url = reverse_lazy("hornescalculator_base")

@login_required
def car(request):
    carform = CarForm(request.POST or None)

    if carform.is_valid():
        car = carform.save(commit=False)
        car.user = request.user
        car.annual_cost = car.get_total_costs()["yearly_total"]
        car.monthly_cost = car.get_total_costs()["monthly_total"]
        car.semimonthly_cost = car.get_total_costs()["semimonthly_total"]
        car.biweekly_cost = car.get_total_costs()["biweekly_total"]
        car.weekly_cost = car.get_total_costs()["weekly_total"]
        car.daily_cost = car.get_total_costs()["daily_total"]
        car.gas = car.get_gas_cost()
        car.save()
        return redirect('hornescalculator_base')

    return render(request, 'hornescalculator/data/car.html', {'form':carform})


class DetailCar(LoginRequiredMixin, DetailView):
    model = Car
    template_name = 'hornescalculator/data/car_details.html'


class UpdateCar(LoginRequiredMixin, UpdateView):
    model = Car
    template_name = 'hornescalculator/data/car_update.html'
    form_class = CarForm
    success_url = reverse_lazy('hornescalculator_base')

    def form_valid(self, form):
        car_update = form.save(commit=False)
        car_update.annual_cost = car_update.get_total_costs()["yearly_total"]
        car_update.monthly_cost = car_update.get_total_costs()["monthly_total"]
        car_update.semimonthly_cost = car_update.get_total_costs()["semimonthly_total"]
        car_update.biweekly_cost = car_update.get_total_costs()["biweekly_total"]
        car_update.weekly_cost = car_update.get_total_costs()["weekly_total"]
        car_update.daily_cost = car_update.get_total_costs()["daily_total"]
        car_update.gas = car_update.get_total_costs()["yearly_total"]
        car_update.save()
        return redirect('hornescalculator_base')

class CarDelete(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'hornescalculator/data/car_confirm_delete.html'
    success_url = reverse_lazy("hornescalculator_base")

@login_required
def utilities(request):
    utilitiesform = UtilitiesForm(request.POST or None)

    if utilitiesform.is_valid():
        utility = utilitiesform.save(commit=False)
        utility.user = request.user
        utility.annual_cost = utility.get_total_costs()["yearly_total"]
        utility.monthly_cost = utility.get_total_costs()["monthly_total"]
        utility.semimonthly_cost = utility.get_total_costs()["semimonthly_total"]
        utility.biweekly_cost = utility.get_total_costs()["biweekly_total"]
        utility.weekly_cost = utility.get_total_costs()["weekly_total"]
        utility.daily_cost = utility.get_total_costs()["daily_total"]
        utility.save()
        return redirect('hornescalculator_base')

    return render(request, 'hornescalculator/data/utilities.html', {'form':utilitiesform})


class DetailUtilities(LoginRequiredMixin, DetailView):
    model = Utilities
    template_name = 'hornescalculator/data/utilities_details.html'


class UpdateUtilities(LoginRequiredMixin, UpdateView):
    model = Utilities
    template_name = 'hornescalculator/data/utilities_update.html'
    form_class = UtilitiesForm
    success_url = reverse_lazy('hornescalculator_base')

    def form_valid(self, form):
        utilities_update = form.save(commit=False)
        utilities_update.annual_cost = utilities_update.get_total_costs()["yearly_total"]
        utilities_update.monthly_cost = utilities_update.get_total_costs()["monthly_total"]
        utilities_update.semimonthly_cost = utilities_update.get_total_costs()["semimonthly_total"]
        utilities_update.biweekly_cost = utilities_update.get_total_costs()["biweekly_total"]
        utilities_update.weekly_cost = utilities_update.get_total_costs()["weekly_total"]
        utilities_update.daily_cost = utilities_update.get_total_costs()["daily_total"]
        utilities_update.save()
        return redirect('hornescalculator_base')

class UtilitiesDelete(LoginRequiredMixin, DeleteView):
    model = Utilities
    template_name = 'hornescalculator/data/utilities_confirm_delete.html'
    success_url = reverse_lazy("hornescalculator_base")

@login_required
def food(request):
    foodform = FoodForm(request.POST or None)

    if foodform.is_valid():
        food = foodform.save(commit=False)
        food.user = request.user
        food.annual_cost = food.get_total_costs()["yearly_total"]
        food.monthly_cost = food.get_total_costs()["monthly_total"]
        food.semimonthly_cost = food.get_total_costs()["semimonthly_total"]
        food.biweekly_cost = food.get_total_costs()["biweekly_total"]
        food.weekly_cost = food.get_total_costs()["weekly_total"]
        food.daily_cost = food.get_total_costs()["daily_total"]
        food.save()
        return redirect('hornescalculator_base')

    return render(request, 'hornescalculator/data/food.html', {'form':foodform})


class DetailFood(LoginRequiredMixin, DetailView):
    model = Food
    template_name = 'hornescalculator/data/food_details.html'


class UpdateFood(LoginRequiredMixin, UpdateView):
    model = Food
    template_name = 'hornescalculator/data/food_update.html'
    form_class = FoodForm
    success_url = reverse_lazy('hornescalculator_base')

    def form_valid(self, form):
        food_update = form.save(commit=False)
        food_update.annual_cost = food_update.get_total_costs()["yearly_total"]
        food_update.monthly_cost = food_update.get_total_costs()["monthly_total"]
        food_update.semimonthly_cost = food_update.get_total_costs()["semimonthly_total"]
        food_update.biweekly_cost = food_update.get_total_costs()["biweekly_total"]
        food_update.weekly_cost = food_update.get_total_costs()["weekly_total"]
        food_update.daily_cost = food_update.get_total_costs()["daily_total"]
        food_update.save()
        return redirect('hornescalculator_base')

class FoodDelete(LoginRequiredMixin, DeleteView):
    model = Food
    template_name = 'hornescalculator/data/food_confirm_delete.html'
    success_url = reverse_lazy("hornescalculator_base")

@login_required
def miscellaneous(request):
    miscellaneousform = MiscellaneousForm(request.POST or None)

    if miscellaneousform.is_valid():
        miscellaneous = miscellaneousform.save(commit=False)
        miscellaneous.user = request.user
        miscellaneous.annual_cost = miscellaneous.get_total_costs()["yearly_total"]
        miscellaneous.monthly_cost = miscellaneous.get_total_costs()["monthly_total"]
        miscellaneous.semimonthly_cost = miscellaneous.get_total_costs()["semimonthly_total"]
        miscellaneous.biweekly_cost = miscellaneous.get_total_costs()["biweekly_total"]
        miscellaneous.weekly_cost = miscellaneous.get_total_costs()["weekly_total"]
        miscellaneous.daily_cost = miscellaneous.get_total_costs()["daily_total"]
        miscellaneous.save()
        return redirect('hornescalculator_base')

    return render(request, 'hornescalculator/data/miscellaneous.html', {'form':miscellaneousform})


class DetailMiscellaneous(LoginRequiredMixin, DetailView):
    model = Miscellaneous
    template_name = 'hornescalculator/data/miscellaneous_details.html'


class UpdateMiscellaneous(LoginRequiredMixin, UpdateView):
    model = Miscellaneous
    template_name = 'hornescalculator/data/miscellaneous_update.html'
    form_class = MiscellaneousForm
    success_url = reverse_lazy('hornescalculator_base')

    def form_valid(self, form):
        misc_update = form.save(commit=False)
        misc_update.annual_cost = misc_update.get_total_costs()["yearly_total"]
        misc_update.monthly_cost = misc_update.get_total_costs()["monthly_total"]
        misc_update.semimonthly_cost = misc_update.get_total_costs()["semimonthly_total"]
        misc_update.biweekly_cost = misc_update.get_total_costs()["biweekly_total"]
        misc_update.weekly_cost = misc_update.get_total_costs()["weekly_total"]
        misc_update.daily_cost = misc_update.get_total_costs()["daily_total"]
        misc_update.save()
        return redirect('hornescalculator_base')

class MiscellaneousDelete(LoginRequiredMixin, DeleteView):
    model = Miscellaneous
    template_name = 'hornescalculator/data/miscellaneous_confirm_delete.html'
    success_url = reverse_lazy("hornescalculator_base")

# @login_required
# def tax(request):
#     taxform = TaxForm(request.POST or None)
#
#     if taxform.is_valid():
#         tax = taxform.save(commit=False)
#         tax.user = request.user
#
#         filing_status = str(taxform.cleaned_data['filing_status'])
#         state = str(taxform.cleaned_data['state'])
#         exemptions = str(taxform.cleaned_data['dependents'])
#         pay_rate = str(taxform.cleaned_data['pay_rate'])
#
#         headers = {
#             'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjVkMzI4NDE4NDRmMzYwMWEyODMwYjI3YyIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTU2MzU5MTcwNH0.CvvzJUxbg2wbU56KqUvZ87k8nLz9XJ263QBG10sFjwo',
#             'Content-Type': 'application/x-www-form-urlencoded',
#         }
#
#         data = {
#           'state': taxform.cleaned_data['state'],
#           'filing_status': taxform.cleaned_data['filing_status'],
#           'pay_periods': taxform.cleaned_data['periods'],
#           'pay_rate': taxform.cleaned_data['pay_rate'],
#           'exemptions': taxform.cleaned_data['dependents'],
#         }
#
#         response = requests.post('https:/taxee.io/api/v2/calculate/2019', headers=headers, data=data)
#
#         json_response = response.json()
#
#         print(json_response)
#
#         tax.fica = json_response['annual']['fica']['amount']
#         tax.annual_state_tax = json_response['annual']['state']['amount']
#         tax.annual_federal_tax = json_response['annual']['federal']['amount']
#
#         tax.save()
#         return redirect('hornescalculator_base')
#
#     return render(request, 'hornescalculator/data/tax.html', {'form':taxform})
#
#
# class DetailTax(generic.DetailView):
#     model = Tax
#     template_name = 'hornescalculator/data/tax_details.html'
#
#
# class UpdateTax(generic.UpdateView):
#     model = Tax
#     template_name = 'hornescalculator/data/tax_update.html'
#     form_class = TaxForm
#     success_url = reverse_lazy('hornescalculator_base')
#
#     def form_valid(self, form):
#
#         tax_update = form.save(commit=False)
#
#         filing_status = str(tax_update.cleaned_data['filing_status'])
#         state = str(tax_update.cleaned_data['state'])
#         exemptions = str(tax_update.cleaned_data['dependents'])
#         pay_rate = str(tax_update.cleaned_data['pay_rate'])
#
#         headers = {
#             'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjVkMzI4NDE4NDRmMzYwMWEyODMwYjI3YyIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTU2MzU5MTcwNH0.CvvzJUxbg2wbU56KqUvZ87k8nLz9XJ263QBG10sFjwo',
#             'Content-Type': 'application/x-www-form-urlencoded',
#         }
#
#         data = {
#           'state': tax_update.cleaned_data['state'],
#           'filing_status': tax_update.cleaned_data['filing_status'],
#           'pay_periods': tax_update.cleaned_data['periods'],
#           'pay_rate': tax_update.cleaned_data['pay_rate'],
#           'exemptions': tax_update.cleaned_data['dependents'],
#         }
#
#         response = requests.post('https://taxee.io/api/v2/calculate/2019', headers=headers, data=data)
#
#         json_response = response.json()
#
#         print(json_response)
#
#         tax_update.fica = json_response['annual']['fica']['amount']
#         tax_update.annual_state_tax = json_response['annual']['state']['amount']
#         tax_update.annual_federal_tax = json_response['annual']['federal']['amount']
#
#         tax_update.save()
#
#         return redirect('hornescalculator_base')
