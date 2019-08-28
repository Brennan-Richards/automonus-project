from django import forms
from .models import Display, Income, Tax, Housing, Car, Utilities, Food, Miscellaneous		

  class IncomeForm(forms.ModelForm):
     class Meta:
         model = Income
         fields = ['salary', 'paycheck_period']

  class TaxForm(forms.ModelForm):
     class Meta:
         model = Tax
         fields = ['dependents', 'state', 'filing_status', 'periods', 'pay_rate']

  class HousingForm(forms.ModelForm):
     class Meta:
         model = Housing
         fields = ['mortgage', 'mortgage_pay_per', 'home_property_tax', 'homeproptax_pay_per',
         'fire_tax', 'firetax_pay_per', 'homeowners_insurance','homeinsurance_pay_per']

  class CarForm(forms.ModelForm):
     class Meta:
         model = Car
         fields = ['miles_driven', 'miles_per', 'car_mpg', 'maintenance', 'maintenance_pay_per', 'car_insurance',
         'carinsurance_pay_per', 'car_property_tax', 'carproptax_pay_per']

  class UtilitiesForm(forms.ModelForm):
     class Meta:
         model = Utilities
         fields = ['electricity', 'electricity_pay_per', 'heating', 'heating_pay_per',
         'phone', 'phone_pay_per', 'cable', 'cable_pay_per', 'internet', 'internet_pay_per', 'water',
         'water_pay_per']

  class FoodForm(forms.ModelForm):
     class Meta:
         model = Food
         fields = ['groceries', 'groceries_pay_per', 'restaurant_food_costs', 'restaurant_pay_per']

  class MiscellaneousForm(forms.ModelForm):
     class Meta:
         model = Miscellaneous
         fields = ['health_insurance', 'healthinsurance_pay_per', 'life_insurance', 'lifeinsurance_pay_per',
         'clothing', 'clothing_pay_per']

  class DisplayForm(forms.ModelForm):
     class Meta:
         model = Display
         fields = ['display']
