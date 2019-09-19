from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
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
    context = {"webhook_url": settings.PLAID_WEBHOOK_URL}
    return render(request, 'institutions/link.html', context=context)


@login_required
def get_access_token(request):
    print("get access token")
    user = request.user
    if request.method == 'POST':
        data = request.POST.copy()
        public_token = data['public_token']
        # the public token is received from Plaid Link
        response = client.Item.public_token.exchange(public_token)
        item_id = response["item_id"]  # unique id for combination of user + institution
        access_token = response['access_token']
        institution_name = data["metadata[institution][name]"]
        institution_id = data["metadata[institution][institution_id]"]
        institution, created = Institution.objects.update_or_create(plaid_id=institution_id,
                                                                    defaults={"name": institution_name}
                                                                    )

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
        user_institution.populate_or_update_accounts()

        # getting investments data
        user_institution.populate_securities_and_holdings()
        user_institution.populate_transactions_loop_launch(type="investment_transactions")

        # user_institution.populate_transactions()  # this is triggered when the webhook call is received
        return JsonResponse({"status": "success"})
