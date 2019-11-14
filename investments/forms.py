from django.forms import ModelForm, TextInput
from .models import MockInvestment

class UpdateMockInvestmentForm(ModelForm):
    class Meta:
        model = MockInvestment
        fields = ['initial_principal', 'interest_rate', 'time_in_years', 'input_amount_per_period',
                  'input_period_in_days', 'times_compounded_per_year']
