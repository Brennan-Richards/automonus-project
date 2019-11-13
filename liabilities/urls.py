from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('liabilities_dashboard/', views.liabilities_dashboard, name='liabilities_dashboard'),
    path('liability_analysis/<int:student_loan_id>/', views.liability_analysis, name='liability_analysis'),
    path('yourloans/', views.StudentLoanListView.as_view(), name="student_loan_list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
