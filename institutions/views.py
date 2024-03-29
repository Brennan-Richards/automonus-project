from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Institution, UserInstitution
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from plaid import Client

client = Client(client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    public_key=settings.PLAID_PUBLIC_KEY,
    environment=settings.PLAID_ENV
)


class UserInstitutions(LoginRequiredMixin, generic.ListView):
    template_name = 'institutions/user_institutions.html'

    def get_queryset(self):
        user = self.request.user
        queryset = UserInstitution.objects.filter(user=user, is_active=True)
        print(queryset)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset


class DisconnectUserInstitution(LoginRequiredMixin, generic.View):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            uuid = kwargs.get("uuid")
            self.user_institution = get_object_or_404(UserInstitution, uuid=uuid, user=user)
        return super(DisconnectUserInstitution, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.user_institution.is_active:
            self.user_institution.is_active = False
            self.user_institution.save(force_update=True)
            messages.success(request, "Updated!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def link(request):
    """A page for clicking on the button to start Plaid integration"""
    user = request.user
    items_connected = len(UserInstitution.objects.filter(user=request.user, is_active=True))
    num_items_allowed = request.user.profile.institutions_connectable
    can_connect = (items_connected < num_items_allowed)
    if num_items_allowed == 0:
        return redirect("subscribe")
    elif not(user.profile.num_items_connected() < user.profile.institutions_connectable):
        #User must upgrade subscription to connect more items.
        return redirect("update_subscription")
    context = {"webhook_url": settings.PLAID_WEBHOOK_URL,
               "can_connect_another": can_connect,
               "num_items_connected":items_connected,
               "num_items_allowed": num_items_allowed}
    return render(request, 'institutions/link.html', context=context)


@login_required
def get_access_token(request):
    print("get access token")
    user = request.user
    if request.method == 'POST':
        data = request.POST.copy()
        print(data)
        public_token = data['public_token']
        account_id = data['account_id']
        print(account_id)
        # the public token is received from Plaid Link
        response = client.Item.public_token.exchange(public_token)

        # asset_response = asset.Item.public_token.exchange(public_token)
        # print(response, asset_response)
        item_id = response["item_id"]  # unique id for combination of user + institution
        access_token = response['access_token']
        institution_name = data["metadata[institution][name]"]
        institution_id = data["metadata[institution][institution_id]"]
        institution, created = Institution.objects.update_or_create(plaid_id=institution_id,
                                                                    defaults={"name": institution_name})

        #getting stripe bank account token
        stripe_response = client.Processor.stripeBankAccountTokenCreate(access_token, account_id)
        stripe_bank_account_token = stripe_response['stripe_bank_account_token']

        # to prevent not creating UserInstitution if it was deactivated before and has is_active=False
        user_institution, created = UserInstitution.objects.update_or_create(plaid_id=item_id,
                                                                             user=user, institution=institution, is_active=True,
                                                                             defaults={"access_token": access_token}
                                                                             )
        """
        Some products can be unavailable for the chosen institution, if they were not included on js side, like docs say
        about this:

        'A list of Plaid product(s) you wish to use.
        Valid products are: transactions, auth, identity, income, assets, investments, and liabilities.
        Only institutions that support all requested products will be shown.
        In Production, you will be billed for each product that you specify when initializing Link.'
        """
        user_institution.populate_income_information()
        user_institution.populate_or_update_accounts(stripe_bank_account_token=stripe_bank_account_token)

        #getting liabilites data
        user_institution.populate_liabilities_data()
        user_institution.populate_credit_card_data()


        # getting investments data
        user_institution.populate_securities_and_holdings()
        user_institution.populate_transactions_loop_launch(type="investment_transactions")

        # user_institution.populate_transactions()  # this is triggered when the webhook call is received
        return JsonResponse({"status": "success"})
