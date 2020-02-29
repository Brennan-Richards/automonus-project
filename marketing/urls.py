from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('marketing-master-dashboard/', views.marketing_master_dashboard, name='marketing_master_dashboard'),
    path('facebook-ads-dashboard/', views.facebook_ads_dashboard, name='facebook_ads_dashboard'),
    path('google-ads-dashboard/', views.google_ads_dashboard, name='google_ads_dashboard'),
    path('yelp-ads-dashboard/', views.yelp_ads_dashboard, name='yelp_ads_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
