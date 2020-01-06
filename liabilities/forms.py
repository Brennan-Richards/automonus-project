from django.forms import ModelForm, TextInput
from django import forms
from .models import LiabilityAnalysis, StudentLoan

class UpdateLiabilityAnalysisForm(ModelForm):
    class Meta:
        model = LiabilityAnalysis
        fields = ['mock_payment_amount']\

class StudentLoanPayForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.loan_id = kwargs.pop("loan_id")
        super(StudentLoanPayForm, self).__init__(*args, **kwargs)

    # student_loan = StudentLoan.objects.get(user=user)
    amount = forms.DecimalField(
        label="Payment Amount",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00", # ToDo: Set to LoanPayment amount if such a model exists
                "min": 1,
                "max": "5",
                "type": "number",
                "step": "1",
            }
        )
    )

    consent = forms.BooleanField(label="I give my consent to allow Automonus to process a payment to my loan guarantor.")
