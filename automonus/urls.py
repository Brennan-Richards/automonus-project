from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from . import views

from allauth.account.views import LoginView
from axes.decorators import axes_dispatch
from axes.decorators import axes_form_invalid
from django.utils.decorators import method_decorator
LoginView.dispatch = method_decorator(axes_dispatch)(LoginView.dispatch)
LoginView.form_invalid = method_decorator(axes_form_invalid)(LoginView.form_invalid)
from django.views import defaults as default_views


"""Check for rollback errors"""
def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('error-logger-debug/', trigger_error),

    path('adminnewurl/', admin.site.urls),
    path('', views.about, name='about'),

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

    # django all-auth
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('400/', default_views.bad_request,
                kwargs={'exception': Exception('Bad Request')}),
        path('403/', default_views.permission_denied,
                kwargs={'exception': Exception('Permission Denied')}),
        path('404/', default_views.page_not_found,
                kwargs={'exception': Exception('Page not Found')}),
        path('500/', default_views.server_error),
    ]