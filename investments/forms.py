from django.forms import ModelForm, TextInput
from .models import MockInvestment

class UpdateMockInvestmentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateMockInvestmentForm, self).__init__(*args, **kwargs)
        self.fields['initial_principal'].widget.attrs['placeholder'] = self.instance.initial_principal
        self.fields['interest_rate'].widget.attrs['placeholder'] = self.instance.interest_rate
        self.fields['time_in_years'].widget.attrs['placeholder'] = self.instance.time_in_years
        self.fields['payment_amount_per_period'].widget.attrs['placeholder'] = self.instance.payment_amount_per_period
        self.fields['payment_period_in_days'].widget.attrs['placeholder'] = self.instance.payment_period_in_days
        self.fields['payment_period_in_days'].widget.attrs['placeholder'] = self.instance.payment_period_in_days
        self.fields['times_compounded_per_year'].widget.attrs['placeholder'] = self.instance.times_compounded_per_year
        for field in self.fields.values():
            field.required = True

    class Meta:
        model = MockInvestment
        fields = ['initial_principal', 'interest_rate', 'time_in_years', 'payment_amount_per_period',
                  'payment_period_in_days', 'times_compounded_per_year']
