from django import forms
from investments.models import TylersAdjustment


class TylersAdjustmentForm(forms.ModelForm):
    class Meta:
        model = TylersAdjustment
        fields =  ['adjustment']
