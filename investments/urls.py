from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('investments_dashboard/', views.investments_dashboard, name='investments_dashboard'),
    path('investment_calculator/', views.investment_calculator, name='investment_calculator'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
