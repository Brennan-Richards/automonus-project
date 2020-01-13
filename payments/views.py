from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
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
from .models import MockSubscription

# Create your views here.
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django import forms
from payments.forms import (
    ExternalTransferFirstForm,
    ExternalTransferSecondForm,
    InternalTransferSecondForm,
)
from payments.stripe_manager import StripleManager
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def stripe_create_customer(request):
    context = dict()
    user = request.user
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        #Must decode body before converting to JSON
        data_unicode = request.body.decode('utf-8')
        #Convert to JSON
        data = json.loads(data_unicode)
        email = data['email'] if data['email'] else 'default_no_existing_email@example.com'
        print(data)
        payment_method = data['payment_method']

        # This creates a new Customer and attaches the default PaymentMethod in one API call.
        customer = stripe.Customer.create(
            payment_method=payment_method,
            email=email,
            invoice_settings={
            'default_payment_method': payment_method,
            },
        )

        #Set user customer ID, saved later.
        user.profile.stripe_customer_id = customer['id']

        # This creates a subscription by adding a customer to an item.
        subscription = stripe.Subscription.create(
            customer=user.profile.stripe_customer_id,
            items=[
            {
              'plan': 'plan_GV3Jk12u9FqN1c',
            },
            ],
            expand=['latest_invoice.payment_intent'],
        )

        # print("subscription:", subscription)

        #How to pass subscription back to the client?

        #Save subscription id and the corresponding quantity of institutions the user is allowed to add
        print(subscription)
        if subscription['status'] == 'active':
            user.profile.stripe_subscription_id = subscription['id']
            user.profile.institutions_connectable = subscription['quantity']
            user.profile.save()
        return JsonResponse(subscription)

class UpdateSubscriptionView(TemplateView, LoginRequiredMixin):
    template_name='subscription/update_subscription.html'

    def get(self, request, *args, **kwargs):
        if (self.request.user.profile.institutions_connectable > 0) or self.request.user.profile.cancel_at_period_end:
            return render(request, self.template_name)
        else:
            return redirect("subscribe")

    def get_context_data(self, **kwargs):
        context = super(UpdateSubscriptionView, self).get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        return context

@csrf_exempt
def stripe_upgrade_subscription(request):
    user = request.user
    #A view to update the quantity of institutions allowed on the account
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        #Must decode body before converting to JSON
        data_unicode = request.body.decode('utf-8')
        #Convert to JSON
        data = json.loads(data_unicode)
        institution_quantity = data['quantity']

        subscription = stripe.Subscription.retrieve(str(user.profile.stripe_subscription_id))

        stripe.Subscription.modify(
          subscription.id,
          cancel_at_period_end=False,
          items=[{
            'id': subscription['items']['data'][0].id,
            'quantity': institution_quantity,
          }]
        )

        #Set user profile institutions allowed to reflect change in subscription
        user.profile.institutions_connectable = institution_quantity
        user.profile.save()
        return JsonResponse({'status':'success'})

@csrf_exempt
def stripe_delete_subscription(request):
    user = request.user
    #A view to update the quantity of institutions allowed on the account
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # #Must decode body before converting to JSON
        # data_unicode = request.body.decode('utf-8')
        # #Convert to JSON
        # data = json.loads(data_unicode)
        # institution_quantity = data['quantity']

        subscription = stripe.Subscription.retrieve(str(user.profile.stripe_subscription_id))

        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=True
        )
        #Set user profile institutions allowed to reflect change in subscription
        user.profile.institutions_connectable = 0
        # user.profile.stripe_customer_id = ""
        user.profile.cancel_at_period_end = True

        #Deactivate all of a user's items
        active_user_institutions = UserInstitution.objects.filter(user=user, is_active=True)
        for item in active_user_institutions:
            item.is_active = False
            item.save()
        user.profile.save()

        return JsonResponse({'status':'success'})

@csrf_exempt
def stripe_reactivate_subscription(request):
    user = request.user
    if request.method == 'POST':
        #Cancels request to cancel at the end of the current billing period.
        stripe.api_key = 'sk_test_Cm8UAku0L4hL4G2aOpDMIM7r00iBv2frlo'

        subscription = stripe.Subscription.retrieve(str(user.profile.stripe_subscription_id))

        stripe.Subscription.modify(
          subscription.id,
          cancel_at_period_end=False,
          items=[{
            'id': subscription['items']['data'][0].id,
            'plan': 'plan_GV3Jk12u9FqN1c',
          }]
        )
        user.profile.institutions_connectable = subscription['quantity']
        user.profile.cancel_at_period_end = False
        user.profile.save()
        return JsonResponse({'status':'success'})

@method_decorator(login_required, name="dispatch")
class Subscribe(TemplateView):
    template_name = 'subscription/subscribe.html'
    stripe.api_key = settings.STRIPE_SECRET_KEY

    def get(self, request, *args, **kwargs):
        if request.user.profile.institutions_connectable > 0:
            return render(request, 'institutions/link.html')
        else:
            return render(request, 'subscription/subscribe.html')

    def get_context_data(self, **kwargs):
        context = super(Subscribe, self).get_context_data(**kwargs)
        user = self.request.user
        if user.profile.stripe_subscription_id:
            subscription = stripe.Subscription.retrieve(str(user.profile.stripe_subscription_id))
            context['subscription'] =  subscription #How to send subscription object back to client?
        return context

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
        #     return HttpResponseBadRequest(content='amount must be more than $0.5')
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


# Internal transfer views


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

class MockSubscriptionCreate(LoginRequiredMixin, CreateView):
    model = MockSubscription
    template_name = 'subscription/mocksubscription_form.html'
    fields = ['institutions_for_investments', 'institutions_for_liabilities']
    success_url = reverse_lazy("mocksubscription_display")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # def get(self, *args, **kwargs):
    #     if self.model.objects.get(user=self.request.user).exists():
    #         model = self.model.objects.get(user=self.request.user)
    #         return redirect("mocksubscription_update", pk=model.id)
    #     else:
    #         return render(request, template_name)

    # def get_absolute_url(self):
    #     return reverse('subscription_cost_display')

class MockSubscriptionUpdate(LoginRequiredMixin, UpdateView):
    model = MockSubscription
    fields = ['institutions_for_investments', 'institutions_for_liabilities']
    success_url = reverse_lazy("mocksubscription_display")
    template_name = 'subscription/mocksubscription_update_form.html'

class MockSubscriptionDisplay(TemplateView):
    template_name = "subscription/mocksubscription_display.html"

    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #     return self.render_to_response(context)
