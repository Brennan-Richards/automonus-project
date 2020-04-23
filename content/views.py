from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from .models import AbstractStudentLoan
from .forms import AbstractStudentLoanForm
from django.views.generic.edit import CreateView, UpdateView

# Create your views here.

class AbstractLoanCreate(CreateView):
    template_name = "content/abstract_loan_create.html"
    form_class = AbstractStudentLoanForm
    success_url = reverse_lazy('abstract_loan_chart')

    def form_valid(self, form):
        print("Form valid")
        return super().form_valid(form)

class AbstractLoanChart(TemplateView):
    template_name = "content/abstract_loan_chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if AbstractStudentLoan.objects.get(id=1) is not None:
            abstract_loan = AbstractStudentLoan.objects.get(id=1)
            payment_amount = abstract_loan.payment_amount

            if abstract_loan.payments_reduces_balance(payment_amount):

                context['reduces'] = True
                context['payment_amount'] = payment_amount
                chart_name = "Path of your student loans up until the payoff date at ${} payments".format(payment_amount)
                chart_type = "line"
                chart_categories = abstract_loan.amortize_to_zero()["dates_as_categories"]
                data = abstract_loan.amortize_to_zero()["amortization_series"]
                chart_series = [{"name":"Your Loan's Remaining Principal Balance","data":data}]
                context["charts_data"] = [{"title": chart_name, "type": chart_type, "categories": chart_categories,
                              "chart_series": chart_series}]
                #Data for written description of loan.
                context["total_interest"] = abstract_loan.amortize_to_zero()["total_interest"]
                context["total_principal"] = abstract_loan.amortize_to_zero()["total_principal"]
                context["total_cost_of_loan"] = abstract_loan.amortize_to_zero()["total_cost_of_loan"]
                context["payoff_date"] = abstract_loan.amortize_to_zero()["payoff_date"]
            else:
                context["reduces"] = False
                context["minimum_payment_amount"] = abstract_loan.amortize_to_zero()

        else:
            context['no_abstract_loan'] = True
        return context


class AbstractLoanUpdate(UpdateView):
    template_name = 'content/abstract_loan_update.html'
    form_class = AbstractStudentLoanForm
    success_url = reverse_lazy('abstract_loan_chart')

    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        return AbstractStudentLoan.objects.get(id=1)
