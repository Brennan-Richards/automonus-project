from django.urls import path, include
from . import views

urlpatterns = [
    path('overview', views.overview, name='overview'),
    path('income', views.income, name='income'),
    path('tax', views.tax, name='tax'),
    path('housing', views.housing, name='housing'),
    path('car', views.car, name='car'),
    path('utilities', views.utilities, name='utilities'),
    path('food', views.food, name='food'),
    path('miscellaneous', views.miscellaneous, name='miscellaneous'),

    path('spending_overview', views.spending_overview, name='spending_overview'),

]
