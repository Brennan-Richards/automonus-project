from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
import uuid

class ModelBaseFieldsAbstract(models.Model):
    is_active = models.BooleanField(default=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True

class BudgetData():
    def calc_all_period_totals(expense, expense_period_choice):
        # Computes the total cost by period of any expense field regardless of the pay period.
        total = 0
        if expense_period_choice == 'Daily':
            total = expense * 365
        elif expense_period_choice == 'Weekly':
            total = expense * 52
        elif expense_period_choice == 'Monthly':
            total = expense * 12
        else:
            total = expense

        yearly_total = round(total,2)
        monthly_total = round((yearly_total / 12), 2)
        semimonthly_total = round((yearly_total / 24), 2)
        biweekly_total = round((yearly_total / 26), 2)
        weekly_total = round((yearly_total / 52), 2)
        daily_total = round((yearly_total / 365), 2)

        return { "yearly_total":yearly_total,
                 "monthly_total":monthly_total,
                 "semimonthly_total":semimonthly_total,
                 "biweekly_total":biweekly_total,
                 "weekly_total":weekly_total,
                 "daily_total":daily_total }

    def get_costs_all_periods(expense_names, expense_values, expense_periods):

        total = 0

        for expense in expense_names:
            if expense_periods[expense] == 'Daily':
                total += expense_values[expense] * Decimal(365)
            elif expense_periods[expense] == 'Weekly':
                total += expense_values[expense] * Decimal(52)
            elif expense_periods[expense] == 'Monthly':
                total += expense_values[expense] * Decimal(12)
            else:
                total += expense_values[expense] * Decimal(1)

        yearly_total = round(total, 2)
        monthly_total = round((yearly_total / 12), 2)
        semimonthly_total = round((yearly_total / 24), 2)
        biweekly_total = round((yearly_total / 26), 2)
        weekly_total = round((yearly_total / 12), 2)
        daily_total = round((yearly_total / 365), 2)

        return { "yearly_total":yearly_total,
                 "monthly_total":monthly_total,
                 "semimonthly_total":semimonthly_total,
                 "biweekly_total":biweekly_total,
                 "weekly_total":weekly_total,
                 "daily_total":daily_total }

    def get_queryset_costs(user, model_name):
        model = ContentType.objects.get(app_label='expenditures', model=model_name.lower()).model_class()
        queryset = model.objects.filter(user=user)
        dictionary = dict()
        #aggregate costs of all models in a queryset
        a = queryset.aggregate(yearly_total=Sum("annual_cost"))["yearly_total"]
        b = queryset.aggregate(monthly_total=Sum("monthly_cost"))["monthly_total"]
        c = queryset.aggregate(semimonthly_total=Sum("semimonthly_cost"))["semimonthly_total"]
        d = queryset.aggregate(biweekly_total=Sum("biweekly_cost"))["biweekly_total"]
        e = queryset.aggregate(weekly_total=Sum("weekly_cost"))["weekly_total"]
        f = queryset.aggregate(daily_total=Sum("daily_cost"))["daily_total"]

        dictionary["yearly_total"] = round(a, 2)
        dictionary["monthly_total"] = round(b, 2)
        dictionary["semimonthly_total"] = round(c, 2)
        dictionary["biweekly_total"] = round(d, 2)
        dictionary["weekly_total"] = round(e, 2)
        dictionary["daily_total"] = round(f, 2)
        return dictionary


# Definitions for PAY_PERIOD_CHOICES below.
DAILY = 'Daily'
WEEKLY = 'Weekly'
MONTHLY = 'Monthly'
YEARLY = 'Yearly'

# Choices variables for pay_period.
PAY_PERIOD_CHOICES = [
    (DAILY, 'Daily'),
    (WEEKLY, 'Weekly'),
    (MONTHLY, 'Monthly'),
    (YEARLY, 'Yearly'),
]

class Housing(ModelBaseFieldsAbstract):
    name = models.CharField(max_length=100, default="Housing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    mortgage = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    home_property_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    fire_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    homeowners_insurance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    annual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    semimonthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    biweekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    weekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    daily_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)


    mortgage_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=MONTHLY,
    )

    homeproptax_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    firetax_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    homeinsurance_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=MONTHLY,
    )

    def __str__(self):
        return self.name

    def mortgage_total_costs(self):
        mortgage = self.mortgage
        mortgage_period = self.mortgage_pay_per

        return BudgetData.calc_all_period_totals(mortgage, mortgage_period)

    def homeproptax_total_costs(self):
        homeproptax = self.home_property_tax
        homeproptax_period = self.homeproptax_pay_per

        return BudgetData.calc_all_period_totals(homeproptax, homeproptax_period)

    def firetax_total_costs(self):
        firetax = self.fire_tax
        firetax_per = self.firetax_pay_per

        return BudgetData.calc_all_period_totals(firetax, firetax_per)

    def homeinsurance_total_costs(self):
        homeinsurance = self.homeowners_insurance
        homeinsurance_period = self.homeinsurance_pay_per

        return BudgetData.calc_all_period_totals(homeinsurance, homeinsurance_period)

    def get_total_costs(self):
        expenses = ['mortgage', 'home_property_tax', 'fire_tax', 'homeowners_insurance']
        exp_values = {'mortgage':self.mortgage, 'home_property_tax': self.home_property_tax, 'fire_tax':self.fire_tax, 'homeowners_insurance':self.homeowners_insurance}
        choices = {'mortgage':self.mortgage_pay_per, 'home_property_tax':self.homeproptax_pay_per, 'fire_tax':self.firetax_pay_per, 'homeowners_insurance':self.homeinsurance_pay_per}

        return BudgetData.get_costs_all_periods(expenses, exp_values, choices)


class Car(ModelBaseFieldsAbstract):
    name = models.CharField(max_length=100, default="Car")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    gas = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    car_mpg = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    maintenance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    car_insurance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    car_property_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    miles_driven = models.IntegerField(default=0)
    annual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    semimonthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    biweekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    weekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    daily_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)

    current_price_of_gas = Decimal(2.68) # TODO: Replace this with an updated price of gas

    miles_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    maintenance_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    carinsurance_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=MONTHLY,
    )

    carproptax_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    def __str__(self):
        return self.name

    def gas_total_costs(self):
        gas = self.gas
        gas_period = self.miles_per

        return BudgetData.calc_all_period_totals(gas, gas_period)

    def maintenance_total_costs(self):
        maintenance = self.maintenance
        maintenance_period = self.maintenance_pay_per

        return BudgetData.calc_all_period_totals(maintenance, maintenance_period)

    def carinsurance_total_costs(self):
        carinsurance = self.car_insurance
        carinsurance_period = self.carinsurance_pay_per

        return BudgetData.calc_all_period_totals(carinsurance, carinsurance_period)

    def carproptax_total_costs(self):
        carproptax = self.car_property_tax
        carproptax_period = self.carproptax_pay_per

        return BudgetData.calc_all_period_totals(carproptax, carproptax_period)

    def get_gas_cost(self):

        cost_per_mile = self.current_price_of_gas / self.car_mpg
        miles_driven = self.miles_driven

        return cost_per_mile * miles_driven


    def get_total_costs(self):

        expenses = ['gas', 'maintenance', 'car_insurance', 'car_property_tax']

        exp_values = {'gas':self.gas, 'maintenance': self.maintenance, 'car_insurance':self.car_insurance, 'car_property_tax':self.car_property_tax}
        choices = {'gas':self.miles_per, 'maintenance':self.maintenance_pay_per, 'car_insurance':self.carinsurance_pay_per, 'car_property_tax':self.carproptax_pay_per}
        dict = BudgetData.get_costs_all_periods(expenses, exp_values, choices)
        return dict

class Utilities(ModelBaseFieldsAbstract):
    name = 'Utilities'
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)
    electricity = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    heating = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    phone = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    cable = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    internet = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    annual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    semimonthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    biweekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    weekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    daily_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)

    electricity_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    heating_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    phone_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    cable_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    internet_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    water_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=YEARLY,
    )

    def __str__(self):
        return self.name

    def electricity_total_costs(self):
        electricity = self.electricity
        electricity_period = self.electricity_pay_per

        return BudgetData.calc_all_period_totals(electricity, electricity_period)

    def heating_total_costs(self):
        heating = self.heating
        heating_period = self.heating_pay_per

        return BudgetData.calc_all_period_totals(heating, heating_period)

    def phone_total_costs(self):
        phone = self.phone
        phone_period = self.phone_pay_per

        return BudgetData.calc_all_period_totals(phone, phone_period)

    def cable_total_costs(self):
        cable = self.cable
        cable_period = self.cable_pay_per

        return BudgetData.calc_all_period_totals(cable, cable_period)

    def internet_total_costs(self):
        internet = self.internet
        internet_period = self.internet_pay_per

        return BudgetData.calc_all_period_totals(internet, internet_period)

    def water_total_costs(self):
        water = self.water
        water_period = self.water_pay_per

        return BudgetData.calc_all_period_totals(water, water_period)

    def get_total_costs(self):
        expenses = ['electricity', 'heating', 'phone', 'cable', 'internet', 'water']

        exp_values = {'electricity':self.electricity, 'heating': self.heating, 'phone':self.phone, 'cable':self.cable, 'internet':self.internet, 'water':self.water}
        choices = {'electricity':self.electricity_pay_per, 'heating':self.heating_pay_per, 'phone':self.phone_pay_per, 'cable':self.cable_pay_per, 'internet':self.internet_pay_per, 'water':self.water_pay_per}

        return BudgetData.get_costs_all_periods(expenses, exp_values, choices)

class Food(ModelBaseFieldsAbstract):
    name = 'Food'
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)
    groceries = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    restaurant_food_costs = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    annual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    semimonthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    biweekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    weekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    daily_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)

    groceries_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    restaurant_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    def __str__(self):
        return self.name

    def groceries_total_costs(self):
        return BudgetData.calc_all_period_totals(self.groceries, self.groceries_pay_per)

    def restaurant_total_costs(self):
        return BudgetData.calc_all_period_totals(self.restaurant_food_costs, self.restaurant_pay_per)

    def yearly_total(self, period=None):
        return round((self.groceries_total_costs() + self.restaurant_total_costs()), 2)


class Miscellaneous(ModelBaseFieldsAbstract):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)
    health_insurance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    life_insurance = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    clothing = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    annual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    semimonthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    biweekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    weekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    daily_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)

    healthinsurance_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    lifeinsurance_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    clothing_pay_per = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    def __str__(self):
        return self.name

    def healthinsurance_total_costs(self):
        healthinsurance = self.health_insurance
        healthinsurance_period = self.healthinsurance_pay_per

        return BudgetData.calc_all_period_totals(healthinsurance, healthinsurance_period)


    def lifeinsurance_total_costs(self):
        lifeinsurance = self.life_insurance
        lifeinsurance_period = self.lifeinsurance_pay_per

        return BudgetData.calc_all_period_totals(lifeinsurance, lifeinsurance_period)

    def clothing_total_costs(self):
        clothing = self.clothing
        clothing_period = self.clothing_pay_per

        return BudgetData.calc_all_period_totals(clothing, clothing_period)

    def get_total_costs(self):
        expenses = ['health_insurance', 'life_insurance', 'clothing']

        exp_values = {'health_insurance':self.health_insurance, 'life_insurance': self.life_insurance, 'clothing':self.clothing}
        choices = {'health_insurance':self.healthinsurance_pay_per, 'life_insurance':self.lifeinsurance_pay_per, 'clothing':self.clothing_pay_per}

        return BudgetData.get_costs_all_periods(expenses, exp_values, choices)

class CustomExpense(ModelBaseFieldsAbstract):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    name = models.CharField(max_length=100)
    cost_per_pay_period = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    annual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    monthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    semimonthly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    biweekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    weekly_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
    daily_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)

    pay_period = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    def get_total_costs(self):
        yearly_total = BudgetData.calc_all_period_totals(self.cost_per_pay_period, self.pay_period)
        monthly_total = round((yearly_total/12), 2)
        semimonthly_total = round((yearly_total/24), 2)
        biweekly_total = round((yearly_total/26), 2)
        weekly_total = round((yearly_total/52), 2)
        daily_total = round((yearly_total/365), 2)
        dict

        return { "yearly_total":yearly_total,
                 "monthly_total":monthly_total,
                 "semimonthly_total":semimonthly_total,
                 "biweekly_total":biweekly_total,
                 "weekly_total":weekly_total,
                 "daily_total":daily_total }

class Display(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

    DISPLAY_PERIOD_CHOICES = [
        (DAY, 'Day'),
        (WEEK, 'Week'),
        (MONTH, 'Month'),
        (YEAR, 'Year'),
    ]

    display = models.CharField(
        max_length=5,
        choices=DISPLAY_PERIOD_CHOICES,
        default=YEAR,
    )

    def display_string(self):
        if self.display == 'day':
            return 'day'
        elif self.display == 'week':
            return 'week'
        elif self.display == 'month':
            return 'month'
        else:
            return 'year'

    def display_operator(self):
        if self.display == 'day':
            return 365.00
        elif self.display == 'week':
            return 52.00
        elif self.display == 'month':
            return 12.00
        else:
            return 1.00


# class Tax(models.Model):
#     name = 'Tax'
#     user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)
#     dependents = models.IntegerField()
#     state = models.CharField(max_length=2)
#     pay_rate = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True, null=True)
#     fica = models.IntegerField(default=0)
#     annual_state_tax = models.IntegerField(default=0)
#     annual_federal_tax = models.IntegerField(default=0)
#     SINGLE = 'single'
#     MARRIED = 'married'
#     MARRIED_SEPARATELY = 'married_separately'
#     HEAD_OF_HOUSEHOLD = 'head_of_household'
#
#     FILING_STATUS_CHOICES = [
#         (SINGLE, 'Single'),
#         (MARRIED, 'Married'),
#         (MARRIED_SEPARATELY, 'Married Separately'),
#         (HEAD_OF_HOUSEHOLD, 'Head of Household')
#     ]
#
#     filing_status = models.CharField(
#         max_length=20,
#         choices=FILING_STATUS_CHOICES,
#         default=SINGLE,
#     )
#
#     # Definitions for PERIODS_CHOICES below.
#     DAILY = 365
#     WEEKLY = 52
#     BIWEEKLY = 26
#     SEMIMONTHLY = 24
#     MONTHLY = 12
#     YEARLY = 1
#
#     # Choices variables for periods.
#     PERIODS_CHOICES = [
#         (DAILY, 'Daily'),
#         (WEEKLY, 'Weekly'),
#         (SEMIMONTHLY, 'Semi-monthly'),
#         (BIWEEKLY, 'Biweekly'),
#         (MONTHLY, 'Monthly'),
#         (YEARLY, 'Yearly'),
#     ]
#
#     periods = models.IntegerField(
#         choices=PERIODS_CHOICES,
#         default=52,
#     )
#
#     def annual_cost(self):
#         fica = self.fica
#         state = self.annual_state_tax
#         federal = self.annual_federal_tax
#
#         total = fica + state + federal
#
#         return total
#
#     def calc_income(self):
#
#         return self.pay_rate * self.periods
#
#     def income_after_tax_and_fica(self):
#
#         return self.calc_income() - self.annual_cost()
