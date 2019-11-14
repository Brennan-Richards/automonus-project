from django.forms import ModelForm, TextInput
from .models import LiabilityAnalysis

class UpdateLiabilityAnalysisForm(ModelForm):
    class Meta:
        model = LiabilityAnalysis
        fields = ['mock_payment_amount']
