from django import forms
from .models import Display, Housing, Car, Utilities, Food, Miscellaneous
from .models import BillDestination, Bill


class ConfirmBillPayForm(forms.Form):
    src_accounts = forms.CharField(label="Choose source account", required=True)
    user_confirmation = forms.BooleanField(label="I consent to pay this bill", required=True)

# class TaxForm(forms.ModelForm):
#     class Meta:
#         model = Tax
#         fields = ['dependents', 'state', 'filing_status', 'periods', 'pay_rate']

class BillModelForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['name', 'bill_destination', 'description', 'set_auto_pay', 'payment_period', 'amount']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('request_user')
        print(kwargs)
        super(BillModelForm, self).__init__(*args, **kwargs)
        self.fields['bill_destination'].queryset = BillDestination.objects.filter(user=user)

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
