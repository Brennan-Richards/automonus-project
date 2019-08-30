from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [

    path('income_overview/', views.income_overview, name='income_overview'),
    path('spending_overview/', views.spending_overview, name='spending_overview'),
    path('liabilities_overview', views.liabilities_overview, name='liabilities_overview'),
    path('savings_overview', views.savings_overview, name='savings_overview'),
    path('investments_overview', views.investments_overview, name='investments_overview'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
