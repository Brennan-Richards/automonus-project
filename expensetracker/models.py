from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import decimal

# Create your models here.

class Income(models.Model):

    name = 'Income'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    salary = models.DecimalField(max_digits=11, decimal_places=2)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    BIWEEKLY = 'Biweekly'
    MONTHLY = 'Monthly'

    PAY_CHECK_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Biweekly'),
        (MONTHLY, 'Monthly'),
    ]

    paycheck_period = models.CharField(
        max_length=7,
        choices=PAY_CHECK_CHOICES,
        default=WEEKLY,
    )

    def __str__(self):
        return self.name

    # Use Taxee API


class Housing(models.Model):
    name = 'Housing'

    user = models.OneToOneField(User,  on_delete=models.CASCADE, default=False)

    mortgage = models.DecimalField(max_digits=11, decimal_places=2)
    home_property_tax = models.DecimalField(max_digits=11, decimal_places=2)
    fire_tax = models.DecimalField(max_digits=11, decimal_places=2)
    homeowners_insurance = models.DecimalField(max_digits=11, decimal_places=2)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

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

    values = [mortgage, home_property_tax, fire_tax, homeowners_insurance]
    choices = [mortgage_pay_per, homeproptax_pay_per, firetax_pay_per, homeinsurance_pay_per]

    def __str__(self):
        return self.name

    def yearly_total(self):
        total = 0
        choices = self.choices
        values = self.values

        for choice in choices:
            if choice == 'Daily':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 365.0
            elif choice == 'Weekly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 52.0
            elif choice == 'Monthly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 12.0
            else:
                total = values[choices.index(choice)]

        return total

class Car(models.Model):
    name = 'Car'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    gas = models.DecimalField(max_digits=11, decimal_places=2)
    maintenance = models.DecimalField(max_digits=11, decimal_places=2)
    car_insurance = models.DecimalField(max_digits=11, decimal_places=2)
    car_property_tax = models.DecimalField(max_digits=11, decimal_places=2)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

    PAY_PERIOD_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]

    gas_pay_per = models.CharField(
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

    values = [gas, maintenance, car_insurance, car_property_tax]
    choices = [gas_pay_per, maintenance_pay_per, carinsurance_pay_per, carproptax_pay_per]

    def __str__(self):
        return self.name

    def yearly_total(self):
        total = 0
        choices = self.choices
        values = self.values

        for choice in choices:

            if choice == 'Daily':
                operator = 365.0
            elif choice == 'Weekly':
                operator = 52.0
            elif choice == 'Monthly':
                operator = 12.0
            else:
                operator = 1.0

            total += values[choices.index(choice)] * decimal.create_decimal_from_float(operator)

        return total

class Utilities(models.Model):
    name = 'Utilities'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    electricity = models.DecimalField(max_digits=11, decimal_places=2)
    heating = models.DecimalField(max_digits=11, decimal_places=2)
    phone = models.DecimalField(max_digits=11, decimal_places=2)
    cable = models.DecimalField(max_digits=11, decimal_places=2)
    internet = models.DecimalField(max_digits=11, decimal_places=2)
    water = models.DecimalField(max_digits=11, decimal_places=2)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

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

    def yearly_total(self):
        total = 0
        choices = self.choices
        values = self.values

        for choice in choices:
            if choice == 'Daily':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 365.0
            elif choice == 'Weekly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 52.0
            elif choice == 'Monthly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 12.0
            else:
                total = values[choices.index(choice)]

        return total

class Food(models.Model):
    name = 'Food'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    groceries = models.DecimalField(max_digits=11, decimal_places=2)
    restaurant_food_costs = models.DecimalField(max_digits=11, decimal_places=2)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

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

    values = [groceries, restaurant_food_costs]
    choices = [groceries_pay_per, restaurant_pay_per]

    def __str__(self):
        return self.name

    def yearly_total(self):
        total = 0
        choices = self.choices
        values = self.values

        for choice in choices:
            if choice == 'Daily':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 365.0
            elif choice == 'Weekly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 52.0
            elif choice == 'Monthly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 12.0
            else:
                total = values[choices.index(choice)]

        return total

class Miscellaneous(models.Model):
    name = 'Miscellaneous'

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=False)

    health_insurance = models.DecimalField(max_digits=11, decimal_places=2)
    life_insurance = models.DecimalField(max_digits=11, decimal_places=2)
    clothing = models.DecimalField(max_digits=11, decimal_places=2)

    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

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

    def yearly_total(self):
        total = 0
        choices = self.choices
        values = self.values

        for choice in choices:
            if choice == 'Daily':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 365.0
            elif choice == 'Weekly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 52.0
            elif choice == 'Monthly':
                total = Decimal.from_float(total) + values[choices.index(choice)] * 12.0
            else:
                total = values[choices.index(choice)]

        return total
