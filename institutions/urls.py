from django.urls import path, include
from . import views

urlpatterns = [
    path('link/', views.link, name='link_institution'),
    path('link/get-access-token/', views.get_access_token, name='get_access_token'),
    path("connected-institutions", views.UserInstitutions.as_view(), name="user_institutions"),
    path("disconnect-user-institution/<uuid>", views.DisconnectUserInstitution.as_view(), name="disconnect_user_institution"),
]
