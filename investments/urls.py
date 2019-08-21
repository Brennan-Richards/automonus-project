from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [

    path('investments_overview', views.investments_overview, name='investments_overview'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
