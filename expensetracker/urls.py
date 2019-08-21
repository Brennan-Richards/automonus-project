from django.urls import path, include
from . import views

urlpatterns = [

    path('spending_overview', views.spending_overview, name='spending_overview'),

]
