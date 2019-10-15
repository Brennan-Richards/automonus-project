from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [

    path('enable-payments/', views.enable_payments, name='enable_payments'),
    path('check-auth/', views.StripeChecker.as_view(), name='check_stripe'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
