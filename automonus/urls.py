from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.content, name='automonus_content'),
    path('display/<int:pk>/update', views.UpdateDisplay.as_view(), name='display_update'),
    path('accounts/', include('accounts.urls')),
    path('expensetracker/', include('expensetracker.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
