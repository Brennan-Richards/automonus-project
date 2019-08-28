from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('income/', include('income.urls')),
    path('expensetracker/', include('expensetracker.urls')),
    path('savings/', include('savings.urls')),
    path('debts/', include('debts.urls')),
    path('investments/', include('investments.urls')),
    path('get_access_token/', views.get_access_token, name="get_access_token"),
    path('institutions/', include('institutions.urls')),
    path('user-accounts/', include('users.urls')),
    path('webhooks/', include('webhooks.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
