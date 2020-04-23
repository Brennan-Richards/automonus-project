from django.forms import ModelForm, TextInput
from django import forms
from .models import AbstractStudentLoan

class AbstractStudentLoanForm(ModelForm):
    class Meta:
        model = AbstractStudentLoan
        fields = ['interest_rate_percentage', 'payment_amount', 'current_balance', 'payments_per_year']
