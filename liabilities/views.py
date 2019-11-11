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
        print(charts_data)
        transactions = Transaction.objects.filter(account__user_institution__user=user,
                                                  account__type__name__in=account_types, amount__gt=0,
                                                  account__user_institution__is_active=True
                                                  ).order_by("-id")[:100]
        student_loan_accounts = Account.objects.filter(user_institution__user=user, type__name__in=account_types,
                                          subtype__name__in=account_subtypes, user_institution__is_active=True) \
                                          .aggregate(total=Sum("current_balance"))
        query_kwargs = {
            "account__user_institution__user": user,
            "user_institution__is_active": True
        }

        remaining_principal_balance = student_loan_accounts["total"]

        context = {
                   "charts_data": charts_data,
                   "transactions": transactions
                   }
        try:
            student_loans = StudentLoan.objects.filter(**query_kwargs)
            context["student_loans"] = student_loans
        except StudentLoan.objects.get(**query_kwargs).DoesNotExist:
            student_loans = None

        try:
            credit_cards = CreditCard.objects.filter(**query_kwargs)
            context["credit_cards"] = credit_cards
        except CreditCard.objects.filter(**query_kwargs).DoesNotExist:
            credit_cards = None

    return render(request, 'liabilities/liabilities_dashboard.html', context)

@login_required
def liability_analysis(request):
    user = request.user
    context = dict()

    student_loan = StudentLoan.objects.get(account__user_institution__user=user, user_institution__is_active=True)
    #Variables for charts_data dictionary
    payment_amount = 10000
    if student_loan.amortize_to_zero(payment_amount=payment_amount) is not False:
        chart_name = "Path of your student loan up until the payoff date"
        chart_type = "line"
        chart_categories = student_loan.amortize_to_zero(payment_amount=payment_amount)["dates_as_categories"]
        data = student_loan.amortize_to_zero(payment_amount=payment_amount)["amortization_series"]
        chart_series = [{"name":"Student Loan Balance","data":data}]
        context["charts_data"] = [{"title": chart_name, "type": chart_type, "categories": chart_categories,
                      "chart_series": chart_series}]
        #Data for written description of loan.
        context["total_interest"] = student_loan.amortize_to_zero(payment_amount=payment_amount)["total_interest"]
        context["total_principal"] = student_loan.amortize_to_zero(payment_amount=payment_amount)["total_principal"]
        context["total_cost_of_loan"] = student_loan.amortize_to_zero(payment_amount=payment_amount)["total_cost_of_loan"]
    print(context)
    return render(request, 'liabilities/liability_analysis.html', context)
