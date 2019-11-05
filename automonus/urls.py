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

from django_otp.admin import OTPAdminSite

"""Check for rollback errors"""
def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [

    path('error-logger-debug/', trigger_error),

    #Main application views
    path('', views.home, name='home'),
    path('login_signup/', views.login_signup, name='login_signup'),
    path('master_dashboard/', views.master_dashboard, name="master_dashboard"),
    path('adminnewurl/', admin.site.urls),

    #Extends to utilitity URLs
    path('charts/', include('charts.urls')),
    path('institutions/', include('institutions.urls')),
    path('user-accounts/', include('users.urls')),
    path('webhooks/', include('webhooks.urls')),
    path('payments/', include('payments.urls')),

    #Extend to URLs of financial-object-based applications
    path('accounts/', include('accounts.urls')),
    path('income/', include('income.urls')),
    path('investments/', include('investments.urls')),
    path('liabilities/', include('liabilities.urls')),
    path('expenditures/', include('expenditures.urls')),

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
else:
    admin.site.__class__ = OTPAdminSite  # Two factor authentication for admin site
