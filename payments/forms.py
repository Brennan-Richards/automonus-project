from django import forms
from django.contrib.auth.models import User
from accounts.models import Account
from institutions.models import UserInstitution
from .models import BillDestination, Bill
from decimal import Decimal

class BillModelForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['name', 'bill_destination', 'description', 'set_auto_pay', 'payment_period', 'amount']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('request_user')
        print(kwargs)
        super(BillModelForm, self).__init__(*args, **kwargs)
        self.fields['bill_destination'].queryset = BillDestination.objects.filter(user=user)


class ExternalTransferFirstForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "form-control", "id": "dest_email"}),
        required=True,
        label="Add email",
    )

    def clean(self):
        email = self.cleaned_data.get("email")

        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise forms.ValidationError("User with this email does not exist")
        if not email:
            raise forms.ValidationError("email requaried")


class ExternalTransferSecondForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ExternalTransferSecondForm, self).__init__(*args, **kwargs)

    dest_accounts = forms.CharField(
        label="Choose account for transfer to user", required=True
    )
    src_accounts = forms.CharField(label="Choose source account", required=True)
    amount = forms.DecimalField(
        label="Amount Transfer",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "min": 1,
                "max": "5",
                "type": "number",
                "step": "0.1",
            }
        ),
    )

    def clean(self):
        # check if user owner for src account
        self.amount = self.cleaned_data.get("amount")
        self.dest_accounts = self.cleaned_data.get("dest_accounts")
        self.src_accounts = self.cleaned_data.get("src_accounts")
        try:
            self.src_user_accounts = Account.objects.get(
                user_institution__user=self.user,
                uuid=self.cleaned_data.get("src_accounts"),
            )
        except Account.DoesNotExist as e:
            raise forms.ValidationError("User is not owner for provide source account")
        else:
            if Decimal(self.src_user_accounts.current_balance) < Decimal(
                self.cleaned_data.get("amount")
            ):
                raise forms.ValidationError(
                    f"Balance of provide user account { self.src_user_accounts.name } less than amount"
                )


class InternalTransferSecondForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(InternalTransferSecondForm, self).__init__(*args, **kwargs)

    dest_accounts = forms.CharField(label="Choose destination account", required=True)
    src_accounts = forms.CharField(label="Choose source account", required=True)
    amount = forms.DecimalField(
        label="Amount Transfer",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "min": 1,
                "max": "5",
                "type": "number",
                "step": "0.1",
            }
        ),
    )

    def clean(self):
        # check if user owner for src account
        self.amount = self.cleaned_data.get("amount")
        try:
            self.dest_user_accounts = Account.objects.get(
                user_institution__user=self.user,
                uuid=self.cleaned_data.get("dest_accounts"),
            )
        except Account.DoesNotExist as e:
            raise forms.ValidationError("User is not owner for provide dest account")
        try:
            self.src_user_accounts = Account.objects.get(
                user_institution__user=self.user,
                uuid=self.cleaned_data.get("src_accounts"),
            )
        except Account.DoesNotExist as e:
            raise forms.ValidationError("User is not owner for provide source account")
        else:
            if self.dest_user_accounts == self.src_user_accounts:
                raise forms.ValidationError("Accounts must be different")
            if Decimal(self.src_user_accounts.current_balance) < Decimal(
                self.cleaned_data.get("amount")
            ):
                raise forms.ValidationError(
                    f"Balance of provide user account { self.src_user_accounts.name } less than amount"
                )


class ConfirmBillPayForm(forms.Form):
    src_accounts = forms.CharField(label="Choose source account", required=True)
    user_confirmation = forms.BooleanField(label="I consent to pay this bill", required=True)
