from django import forms
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from django.utils.html import format_html
from django.contrib.sites.models import Site
from allauth.account.forms import LoginForm, BaseSignupForm, ResetPasswordForm
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from users.models import Profile
from django.contrib import messages
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

current_site = Site.objects.get_current()
CURRENT_SITE_NAME = current_site.name


class CustomCheckbox(Field):
    template = 'account/custom_checkbox.html'


class CustomResetPasswordForm(ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['email'].label = False
        self.helper.form_tag = False


class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'] = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": _("Email")}))
        self.fields['login'].label = False
        self.fields['password'].label = False
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Field('login'),
            Field('password', placeholder=_("Password*")),
            CustomCheckbox('remember'),
        )

    def user_credentials(self):
        credentials = super(CustomLoginForm, self).user_credentials()
        credentials['username'] = credentials.get('email') or credentials.get('username')
        return credentials


class CustomSignupForm(BaseSignupForm):
    email = forms.EmailField(required=True, label=False, widget=forms.TextInput(attrs={'placeholder': _("Email*")}))
    password1 = forms.CharField(label=False,
                                widget=forms.PasswordInput(attrs={"placeholder": _("Password*")}))
    password2 = forms.CharField(label=False, widget=forms.PasswordInput(attrs={"placeholder": _("Password again*")}))
    agree_to_receive_emails = forms.BooleanField(required=False, initial=False)
    agree_with_tos = forms.BooleanField(required=True, initial=False,
                                            label=" I've read & agree with the <a href='{}' "
                                                  "target='_blank'>Terms of Service</a>"
                                            .format("/general-information/terms-of-service",
                                                    ))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(
    ))

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('email', placeholder=_("Email*")),
            Field('password1', autocomplete='off', placeholder=_("Password*")),
            Field('password2', autocomplete='off', placeholder=_("Password (again)*")),
            CustomCheckbox('agree_with_tos'),
            CustomCheckbox('agree_to_receive_emails'),
            Field("captcha"),
        )

    def save(self, request):
        agree_to_receive_emails = self.cleaned_data.get("agree_to_receive_emails")
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)

        setup_user_email(request, user, [])
        profile, created = Profile.objects.get_or_create(user=user)
        profile.agree_to_receive_emails = True if agree_to_receive_emails else False
        profile.save(force_update=True)
        return user