from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('expenditures_analysis/', views.expenditures_analysis, name='expenditures_analysis'),

    #expenditure planning views
    path('overview', views.overview, name='overview'),

    path('tax', views.tax, name='tax'),
    path('housing', views.housing, name='housing'),
    path('car', views.car, name='car'),
    path('utilities', views.utilities, name='utilities'),
    path('food', views.food, name='food'),
    path('miscellaneous', views.miscellaneous, name='miscellaneous'),

    #Detail views for all expenses & income
    path('tax/<int:pk>', views.DetailTax.as_view(), name='tax_details'),
    path('housing/<int:pk>', views.DetailHousing.as_view(), name='housing_details'),
    path('car/<int:pk>', views.DetailCar.as_view(), name='car_details'),
    path('utilities/<int:pk>', views.DetailUtilities.as_view(), name='utilities_details'),
    path('food/<int:pk>', views.DetailFood.as_view(), name='food_details'),
    path('miscellaneous/<int:pk>', views.DetailMiscellaneous.as_view(), name='miscellaneous_details'),

    #Update views for all expenses & income
    path('tax/<int:pk>/update', views.UpdateTax.as_view(), name='tax_update'),
    path('housing/<int:pk>/update', views.UpdateHousing.as_view(), name='housing_update'),
    path('car/<int:pk>/update', views.UpdateCar.as_view(), name='car_update'),
    path('utilities/<int:pk>/update', views.UpdateUtilities.as_view(), name='utilities_update'),
    path('food/<int:pk>/update', views.UpdateFood.as_view(), name='food_update'),
    path('miscellaneous/<int:pk>/update', views.UpdateMiscellaneous.as_view(), name='miscellaneous_update'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
