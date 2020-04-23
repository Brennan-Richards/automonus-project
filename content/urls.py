from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    # An abstract loan calculator as content for automonus CMS main site.
    path('abstract-loan-create/', views.AbstractLoanCreate.as_view(), name="abstract_loan_create"),
    path('abstract-loan-update/', views.AbstractLoanUpdate.as_view(), name="abstract_loan_update"),
    path('abstract-loan-chart/', views.AbstractLoanChart.as_view(), name="abstract_loan_chart")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
