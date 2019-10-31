from django.shortcuts import render
from .models import StudentLoan, CreditCard, APR
from accounts.models import Account, Transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from charts.utils import ChartData

# Create your views here.

@login_required
def liabilities_dashboard(request):
    context = dict()
    user = request.user
    if user.profile.get_user_institutions():
        account_types = ["loan"]
        account_subtypes = ["student"]
        charts_data = ChartData().get_charts_data_by_module(user=user, chart_type="line", category="liabilities",
                                                            account_types=account_types, account_subtypes=account_subtypes)
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__gt=0,
                                                  account__user_institution__is_active=True
                                                  ).order_by("-id")[:100]
        student_loan_accounts = Account.objects.filter(user_institution__user=user, type__name__in=account_types,
                                          subtype__name__in=account_subtypes, user_institution__is_active=True) \
                                          .aggregate(total=Sum("current_balance"))

        student_loan = StudentLoan.objects.get(account__user_institution__user=user, user_institution__is_active=True)
        # amortize_30 = student_loan.amortize(30, student_loan.minimum_payment_amount)
        credit_card = CreditCard.objects.get(account__user_institution__user=user, user_institution__is_active=True)
        apr = APR.objects.get(credit_card__account__user_institution__user=user, credit_card__user_institution__is_active=True)

        remaining_principal_balance = student_loan_accounts["total"]

        context = {
                   "charts_data": charts_data,
                   "transactions": transactions,
                   "student_loan": student_loan,
                   "credit_card": credit_card,
                   "apr": apr,
                   # "a": amortize_30
                   }
    return render(request, 'liabilities/liabilities_dashboard.html', context)
