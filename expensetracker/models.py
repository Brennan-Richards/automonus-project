from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import *

# Create your models here.


#METHOD - Computes the yearly total of any expense field regardless of the pay period.
def calc_yearly_total(expense, expense_period_choice):

    yearly_total = 0

    if expense_period_choice == 'Daily':
        yearly_total = expense * 365
    elif expense_period_choice == 'Weekly':
        yearly_total = expense * 52
    elif expense_period_choice == 'Monthly':
        yearly_total = expense * 12
    else:
        yearly_total = expense

    return round(yearly_total,2)

class Income(models.Model):

    name = 'Income'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    salary = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    # Definitions for PAY_PERIOD_CHOICES below.
    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Biweekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

    # Choices variables for pay_period.
    PAY_PERIOD_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (BIWEEKLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]

    paycheck_period = models.CharField(
        max_length=7,
        choices=PAY_PERIOD_CHOICES,
        default=WEEKLY,
    )

    def __str__(self):
        return self.name

    def calc_income(self):

        if self.paycheck_period == 'Daily':
            yearly_income = self.salary * 365
        elif self.paycheck_period == 'Weekly':
            yearly_income = self.salary * 52
        elif self.paycheck_period == 'Biweekly':
            yearly_income = self.salary * 26
        elif self.paycheck_period == 'Monthly':
            yearly_income = self.salary * 12

        return yearly_income

    #def deduct(self):
    # Use Taxee API

class Tax(models.Model):
    name = 'Tax'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    dependents = models.IntegerField()
    state = models.CharField(max_length=2)
    pay_rate = models.DecimalField(max_digits=11, decimal_places=2, default=0)


    fica = models.IntegerField(default=0)
    annual_state_tax = models.IntegerField(default=0)
    annual_federal_tax = models.IntegerField(default=0)

    SINGLE = 'single'
    MARRIED = 'married'
    MARRIED_SEPARATELY = 'married_separately'
    HEAD_OF_HOUSEHOLD = 'head_of_household'

    FILING_STATUS_CHOICES = [
        (SINGLE, 'Single'),
        (MARRIED, 'Married'),
        (MARRIED_SEPARATELY, 'Married Separately'),
        (HEAD_OF_HOUSEHOLD, 'Head of Household')
    ]

    filing_status = models.CharField(
        max_length=20,
        choices=FILING_STATUS_CHOICES,
        default=SINGLE,
    )

    # Definitions for PERIODS_CHOICES below.
    DAILY = 365
    WEEKLY = 52
    BIWEEKLY = 26
    SEMIMONTHLY = 24
    MONTHLY = 12
    YEARLY = 1

    # Choices variables for periods.
    PERIODS_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (SEMIMONTHLY, 'Semi-monthly'),
        (BIWEEKLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]

    periods = models.IntegerField(
        choices=PERIODS_CHOICES,
        default=52,
    )

    def annual_cost(self):
        fica = self.fica
        state = self.annual_state_tax
        federal = self.annual_federal_tax

        total = fica + state + federal

        return total

    def calc_income(self):

        return self.pay_rate * self.periods

    def income_after_tax_and_fica(self):

        return self.calc_income() - self.annual_cost()


class Housing(models.Model):
    name = 'Housing'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    mortgage = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    home_property_tax = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    fire_tax = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    homeowners_insurance = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    annual_cost = models.DecimalField(max_digits=11, decimal_places=2, default=0)

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

    def mortgage_yt(self):
        mortgage = self.mortgage
        mortgage_period = self.mortgage_pay_per

        return calc_yearly_total(mortgage, mortgage_period)

    def homeproptax_yt(self):
        homeproptax = self.home_property_tax
        homeproptax_period = self.homeproptax_pay_per

        return calc_yearly_total(homeproptax, homeproptax_period)

    def firetax_yt(self):
        firetax = self.fire_tax
        firetax_per = self.firetax_pay_per

        return calc_yearly_total(firetax, firetax_per)

    def homeinsurance_yt(self):
        homeinsurance = self.homeowners_insurance
        homeinsurance_period = self.homeinsurance_pay_per

        return calc_yearly_total(homeinsurance, homeinsurance_period)


    def yearly_total(self):
        expenses = ['mortgage', 'home_property_tax', 'fire_tax', 'homeowners_insurance']
        exp_values = {'mortgage':self.mortgage, 'home_property_tax': self.home_property_tax, 'fire_tax':self.fire_tax, 'homeowners_insurance':self.homeowners_insurance}
        choices = {'mortgage':self.mortgage_pay_per, 'home_property_tax':self.homeproptax_pay_per, 'fire_tax':self.firetax_pay_per, 'homeowners_insurance':self.homeinsurance_pay_per}
        total = 0

        for expense in expenses:
            if choices[expense] == 'Daily':
                total += exp_values[expense] * Decimal(365)
            elif choices[expense] == 'Weekly':
                total += exp_values[expense] * Decimal(52)
            elif choices[expense] == 'Monthly':
                total += exp_values[expense] * Decimal(12)
            else:
                total += exp_values[expense] * Decimal(1)

        return round(total, 2)

class Car(models.Model):
    name = 'Car'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    miles = models.IntegerField()
    maintenance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    car_insurance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    car_property_tax = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    gas_cost = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    annual_cost = models.DecimalField(max_digits=11, decimal_places=2, default=0)


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

    def gas_yt(self):
        gas = self.gas
        gas_period = self.gas_pay_per

        return calc_yearly_total(gas, gas_period)

    def maintenance_yt(self):
        maintenance = self.maintenance
        maintenance_period = self.maintenance_pay_per

        return calc_yearly_total(maintenance, maintenance_period)

    def carinsurance_yt(self):
        carinsurance = self.car_insurance
        carinsurance_period = self.carinsurance_pay_per

        return calc_yearly_total(carinsurance, carinsurance_period)

    def carproptax_yt(self):
        carproptax = self.car_property_tax
        carproptax_period = self.carproptax_pay_per

        return calc_yearly_total(carproptax, carproptax_period)

    def yearly_total(self):

        expenses = ['gas', 'maintenance', 'car_insurance', 'car_property_tax']

        exp_values = {'gas':self.gas, 'maintenance': self.maintenance, 'car_insurance':self.car_insurance, 'car_property_tax':self.car_property_tax}
        choices = {'gas':self.gas_pay_per, 'maintenance':self.maintenance_pay_per, 'car_insurance':self.carinsurance_pay_per, 'car_property_tax':self.carproptax_pay_per}

        total = 0

        for expense in expenses:

            if choices[expense] == 'Daily':
                total += exp_values[expense] * Decimal(365)
            elif choices[expense] == 'Weekly':
                total += exp_values[expense] * Decimal(52)
            elif choices[expense] == 'Monthly':
                total += exp_values[expense] * Decimal(12)
            else:
                total += exp_values[expense] * Decimal(1)

        return round(total,2)

class Utilities(models.Model):
    name = 'Utilities'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    electricity = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    heating = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    phone = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    cable = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    internet = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    water = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    annual_cost = models.DecimalField(max_digits=11, decimal_places=2, default=0)


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

    def electricity_yt(self):
        electricity = self.electricity
        electricity_period = self.electricity_pay_per

        return calc_yearly_total(electricity, electricity_period)

    def heating_yt(self):
        heating = self.heating
        heating_period = self.heating_pay_per

        return calc_yearly_total(heating, heating_period)

    def phone_yt(self):
        phone = self.phone
        phone_period = self.phone_pay_per

        return calc_yearly_total(phone, phone_period)

    def cable_yt(self):
        cable = self.cable
        cable_period = self.cable_pay_per

        return calc_yearly_total(cable, cable_period)

    def internet_yt(self):
        internet = self.internet
        internet_period = self.internet_pay_per

        return calc_yearly_total(internet, internet_period)

    def water_yt(self):
        water = self.water
        water_period = self.water_pay_per

        return calc_yearly_total(water, water_period)

    def yearly_total(self):
        expenses = ['electricity', 'heating', 'phone', 'cable', 'internet', 'water']

        exp_values = {'electricity':self.electricity, 'heating': self.heating, 'phone':self.phone, 'cable':self.cable, 'internet':self.internet, 'water':self.water}
        choices = {'electricity':self.electricity_pay_per, 'heating':self.heating_pay_per, 'phone':self.phone_pay_per, 'cable':self.cable_pay_per, 'internet':self.internet_pay_per, 'water':self.water_pay_per}

        total = 0

        for expense in expenses:

            if choices[expense] == 'Daily':
                total += exp_values[expense] * Decimal(365)
            elif choices[expense] == 'Weekly':
                total += exp_values[expense] * Decimal(52)
            elif choices[expense] == 'Monthly':
                total += exp_values[expense] * Decimal(12)
            else:
                total += exp_values[expense] * Decimal(1)

        return round(total,2)

class Food(models.Model):
    name = 'Food'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    groceries = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    restaurant_food_costs = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    annual_cost = models.DecimalField(max_digits=11, decimal_places=2, default=0)


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

    def groceries_yt(self):
        groceries = self.groceries
        groceries_period = self.groceries_pay_per

        return calc_yearly_total(groceries, groceries_period)

    def restaurant_yt(self):
        restaurant = self.restaurant_food_costs
        restaurant_period = self.restaurant_pay_per

        return calc_yearly_total(restaurant, restaurant_period)

    def yearly_total(self):
        expenses = ['groceries', 'restaurant_food_costs']

        exp_values = {'groceries':self.groceries, 'restaurant_food_costs': self.restaurant_food_costs}
        choices = {'groceries':self.groceries_pay_per, 'restaurant_food_costs':self.restaurant_pay_per}

        total = 0

        for expense in expenses:

            if choices[expense] == 'Daily':
                total += exp_values[expense] * Decimal(365)
            elif choices[expense] == 'Weekly':
                total += exp_values[expense] * Decimal(52)
            elif choices[expense] == 'Monthly':
                total += exp_values[expense] * Decimal(12)
            else:
                total += exp_values[expense] * Decimal(1)

        return round(total,2)

class Miscellaneous(models.Model):
    name = 'Miscellaneous'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    health_insurance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    life_insurance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    clothing = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    annual_cost = models.DecimalField(max_digits=11, decimal_places=2, default=0)


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

    def healthinsurance_yt(self):
        healthinsurance = self.health_insurance
        healthinsurance_period = self.healthinsurance_pay_per

        return calc_yearly_total(healthinsurance, healthinsurance_period)


    def lifeinsurance_yt(self):
        lifeinsurance = self.life_insurance
        lifeinsurance_period = self.lifeinsurance_pay_per

        return calc_yearly_total(lifeinsurance, lifeinsurance_period)

    def clothing_yt(self):
        clothing = self.clothing
        clothing_period = self.clothing_pay_per

        return calc_yearly_total(clothing, clothing_period)

    def yearly_total(self):
        expenses = ['health_insurance', 'life_insurance', 'clothing']

        exp_values = {'health_insurance':self.health_insurance, 'life_insurance': self.life_insurance, 'clothing':self.clothing}
        choices = {'health_insurance':self.healthinsurance_pay_per, 'life_insurance':self.lifeinsurance_pay_per, 'clothing':self.clothing_pay_per}

        total = 0

        for expense in expenses:

            if choices[expense] == 'Daily':
                total += exp_values[expense] * Decimal(365)
            elif choices[expense] == 'Weekly':
                total += exp_values[expense] * Decimal(52)
            elif choices[expense] == 'Monthly':
                total += exp_values[expense] * Decimal(12)
            else:
                total += exp_values[expense] * Decimal(1)

        return round(total,2)

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

    def cost_of_living_expenses(self):
        user_id = self.user.id

        car = Car.objects.get(user=user_id).annual_cost
        house = Housing.objects.get(user=user_id).annual_cost
        utilities = Utilities.objects.get(user=user_id).annual_cost
        food = Food.objects.get(user=user_id).annual_cost
        misc = Miscellaneous.objects.get(user=user_id).annual_cost

        totals = [car, house, utilities, food, misc]

        all_cost = 0

        for total in totals:
            all_cost += total

        return round(all_cost,2)
