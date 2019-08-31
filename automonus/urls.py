from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.about, name='about'),
    path('link/', views.link, name='link'),

    path('academy/', include('academy.urls')),
    path('analysis/', include('analysis.urls')),
    path('planning/', include('planner.urls')),

    path('hornescalculator/', include('hornescalculator.urls')),
    path('accounts/', include('accounts.urls')),
    path('institutions/', include('institutions.urls')),
    path('user-accounts/', include('users.urls')),
    path('webhooks/', include('webhooks.urls')),
    path('income/', include('income.urls')),
    path('savings/', include('savings.urls')),
    path('investments/', include('investments.urls')),

    # path('link/', views.link, name='link'),

    path('display/<int:pk>/update', views.UpdateDisplay.as_view(), name='display_update'),
    path('marketing/', views.marketing, name='marketing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
