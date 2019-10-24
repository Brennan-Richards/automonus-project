from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import (
    JsonResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.views import View
from django.views.generic import TemplateView
from plaid import Client
import json
import stripe
from payments.stripe_manager import StripleManager
from decimal import Decimal
from institutions.models import UserInstitution
from accounts.models import Account

# Create your views here.
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django import forms
from payments.forms import (
    ExternalTransferFirstForm,
    ExternalTransferSecondForm,
    InternalTransferSecondForm,
)
from payments.stripe_manager import StripleManager
from django.utils.decorators import method_decorator


@login_required
def enable_payments(request):
    user = request.user
    available_masks = ["1111", "0000"]
    user_institution = UserInstitution.objects.filter(user=user)
    user_accounts = Account.objects.filter(
        user_institution__in=user_institution, mask__in=available_masks
    )
    context = {"user_institution": user_institution, "user_accounts": user_accounts}
    return render(request, "payments/enable.html", context=context)


@method_decorator(login_required, name="dispatch")
class StripeChecker(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        # Look up the author we're interested in.
        currency = request.POST.get("currency", None)
        amount = int(Decimal(request.POST.get("amount", None)) * 100)
        account_uuid = request.POST.get("account_uuid", None)
        # if amount < 50:
        #     return HttpResponseBadRequest(content='amount must be more than 0.5$')
        sm = StripleManager(account_uuid=account_uuid)
        try:
            a = 1
        except Exception as e:
            return HttpResponseBadRequest(content=f"{e}")
        resp = sm.deposit_payment(currency=currency, amount=amount)
        return JsonResponse({"status": resp})


@method_decorator(login_required, name="dispatch")
class ExternalTransferCreateView(FormView):
    template_name = "payments/ext_tranfer_create.html"
    form_class = ExternalTransferFirstForm

    def get_context_data(self, **kwargs):
        context = super(ExternalTransferCreateView, self).get_context_data(**kwargs)
        return context

    def get_success_url(self, user_id):
        return reverse("external_transfer_value", kwargs={"to_user": user_id})

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # return super().form_valid(form)
        print(form.user)
        return HttpResponseRedirect(
            self.get_success_url(user_id=form.user.profile.uuid)
        )


@method_decorator(login_required, name="dispatch")
class ExternalTransferValueView(FormView):
    template_name = "payments/ext_transfer_value.html"
    form_class = ExternalTransferSecondForm

    def get_context_data(self, **kwargs):
        context = super(ExternalTransferValueView, self).get_context_data(**kwargs)
        uuid = self.kwargs.get("to_user", "")
        to_user = User.objects.get(profile__uuid=uuid)
        src_user_institutions = UserInstitution.objects.filter(user=self.request.user)
        dest_user_institutions = UserInstitution.objects.filter(user=to_user)
        context["src_user_institutions"] = src_user_institutions
        context["dest_user_institutions"] = dest_user_institutions
        context["to_user"] = to_user
        # uuid = User.objects.get(profile_user__uuid=uuid)
        return context

    def get_success_url(self):
        return reverse("external_transfer_success")

    def get_form_kwargs(self):
        kwargs = super(ExternalTransferValueView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # params
        currency = "usd"
        amount = int(Decimal(form.amount) * 100)
        app_fee = StripleManager.calculate_application_fee(
            form.amount
        )  # TODO STRIPE FEE
        account_uuid = form.src_user_accounts.uuid
        dest_account_uuid = form.dest_accounts
        # init manager
        sm = StripleManager(account_uuid=account_uuid)
        # call deposit method
        try:
            resp = sm.transfer_between_accounts(
                dest_account_uuid=dest_account_uuid,
                currency=currency,
                amount=amount,
                app_fee=app_fee,
            )
        except Exception as e:
            return HttpResponseRedirect(reverse("try_again_later"))
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name="dispatch")
class ExternalTransferSuccessView(TemplateView):
    template_name = "payments/external_transfer_success.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


# Internal methods


class InternalTransferValueView(FormView):
    template_name = "payments/int_transfer_value.html"
    form_class = InternalTransferSecondForm

    def get_context_data(self, **kwargs):
        context = super(InternalTransferValueView, self).get_context_data(**kwargs)
        src_user_institutions = UserInstitution.objects.filter(user=self.request.user)
        context["src_user_institutions"] = src_user_institutions
        context["dest_user_institutions"] = src_user_institutions
        return context

    def get_success_url(self):
        return reverse("internal_transfer_success")

    def get_form_kwargs(self):
        kwargs = super(InternalTransferValueView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        currency = "usd"
        amount = int(Decimal(form.amount) * 100)
        app_fee = StripleManager.calculate_application_fee(
            form.amount
        )  # TODO STRIPE FEE
        account_uuid = form.src_user_accounts.uuid
        dest_account_uuid = form.dest_user_accounts.uuid
        # init manager
        sm = StripleManager(account_uuid=account_uuid)
        # call deposit method
        try:
            resp = sm.transfer_between_accounts(
                dest_account_uuid=dest_account_uuid,
                currency=currency,
                amount=amount,
                app_fee=app_fee,
            )
        except Exception as e:
            return HttpResponseRedirect(reverse("try_again_later"))
        return HttpResponseRedirect(self.get_success_url())


class InternalTransferSuccessView(TemplateView):
    template_name = "payments/internal_transfer_success.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class TryAgainErrorView(TemplateView):
    template_name = "payments/try_again_later.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
