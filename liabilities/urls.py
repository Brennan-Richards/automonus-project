from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('liabilities-dashboard/', views.liabilities_dashboard, name='liabilities_dashboard'),
    path('liability-analysis/<int:student_loan_id>/', views.liability_analysis, name='liability_analysis'),
    path('your-student-loans/', views.StudentLoanListView.as_view(), name="student_loan_list"),
    path('student-loans/make-a-payment/<int:student_loan_id>', views.StudentLoanPayView.as_view(), name="pay_student_loan"),
    path('link-a-guarantor/<int:student_loan_id>', views.GuarantorCreate.as_view(), name="guarantor_link"),
    path('transfer-success/<int:student_loan_id>', views.LoanPaymentSuccess.as_view(), name="loan_payment_success")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
