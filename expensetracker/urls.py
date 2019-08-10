from django.urls import path, include
from . import views

urlpatterns = [
    path('income', views.income, name='income'),
    path('housing', views.housing, name='housing'),
    path('car', views.car, name='car'),
    path('utilities', views.utilities, name='utilities'),
    path('food', views.food, name='food'),
    path('miscellaneous', views.miscellaneous, name='miscellaneous'),
]
