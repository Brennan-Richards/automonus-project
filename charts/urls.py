from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [

    path('about_analysis/', views.about_analysis, name='about_analysis'),

]
