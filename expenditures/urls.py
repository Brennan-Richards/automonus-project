from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('expenditures_dashboard/', views.expenditures_dashboard, name='expenditures_dashboard'),

    #Horne's calculator views
    path('hornescalculator_base', views.hornescalculator_base, name='hornescalculator_base'),

    #Car and Housing object list views
    path('hornescalculator/yourhousing', views.HousingListView.as_view(), name="housing_list"),
    path('hornescalculator/yourcars', views.CarListView.as_view(), name="car_list"),

    #Delete Views
    path('hornescalculator/<int:pk>/confirm_housing_delete/', views.HousingDelete.as_view(), name='housing_delete'),
    path('hornescalculator/<int:pk>/confirm_car_delete/', views.CarDelete.as_view(), name='car_delete'),
    path('hornescalculator/<int:pk>/confirm_utilities_delete/', views.UtilitiesDelete.as_view(), name='utilities_delete'),
    path('hornescalculator/<int:pk>/confirm_food_delete/', views.FoodDelete.as_view(), name='food_delete'),
    path('hornescalculator/<int:pk>/confirm_miscellaneous_delete/', views.MiscellaneousDelete.as_view(), name='miscellaneous_delete'),
    path('hornescalculator/<int:pk>/confirm_customexpense_delete/', views.CustomExpenseDelete.as_view(), name='customexpense_delete'),

    # path('tax', views.tax, name='tax'),
    path('hornescalculator/housing', views.housing, name='housing_create'),
    path('hornescalculator/car', views.car, name='car_create'),
    path('hornescalculator/utilities', views.utilities, name='utilities_create'),
    path('hornescalculator/food', views.food, name='food_create'),
    path('hornescalculator/miscellaneous', views.miscellaneous, name='miscellaneous_create'),
    path('hornescalculator/customexpense', views.CreateCustomExpense.as_view(), name="customexpense_create"),

        #Detail views for all expenses & income
    # path('tax/<int:pk>', views.DetailTax.as_view(), name='tax_details'),
    path('hornescalculator/housing/<int:pk>', views.DetailHousing.as_view(), name='housing_details'),
    path('hornescalculator/car/<int:pk>', views.DetailCar.as_view(), name='car_details'),
    path('hornescalculator/utilities/<int:pk>', views.DetailUtilities.as_view(), name='utilities_details'),
    path('hornescalculator/food/<int:pk>', views.DetailFood.as_view(), name='food_details'),
    path('hornescalculator/miscellaneous/<int:pk>', views.DetailMiscellaneous.as_view(), name='miscellaneous_details'),

        #Update views for all expenses & income
    # path('tax/<int:pk>/update', views.UpdateTax.as_view(), name='tax_update'),
    path('hornescalculator/housing/<int:pk>/update', views.UpdateHousing.as_view(), name='housing_update'),
    path('hornescalculator/car/<int:pk>/update', views.UpdateCar.as_view(), name='car_update'),
    path('hornescalculator/utilities/<int:pk>/update', views.UpdateUtilities.as_view(), name='utilities_update'),
    path('hornescalculator/food/<int:pk>/update', views.UpdateFood.as_view(), name='food_update'),
    path('hornescalculator/miscellaneous/<int:pk>/update', views.UpdateMiscellaneous.as_view(), name='miscellaneous_update'),
    path('hornescalculator/customexpense/<int:pk>/update', views.UpdateCustomExpense.as_view(), name="customexpense_update"),
    # path('hornescalculator/display/<int:pk>/update', views.UpdateDisplay.as_view(), name='display_update')

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
