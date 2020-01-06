from django.contrib import admin
from .models import *

# Register your models here.

class BillAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bill._meta.fields]\

admin.site.register(Bill, BillAdmin)


class BillDestinationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BillDestination._meta.fields]\

admin.site.register(BillDestination, BillDestinationAdmin)


class HousingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Housing._meta.fields]


admin.site.register(Housing, HousingAdmin)


class CarAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Car._meta.fields]


admin.site.register(Car, CarAdmin)


class UtilitiesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Utilities._meta.fields]


admin.site.register(Utilities, UtilitiesAdmin)


class FoodAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Food._meta.fields]


admin.site.register(Food, FoodAdmin)


class MiscellaneousAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Miscellaneous._meta.fields]


admin.site.register(Miscellaneous, MiscellaneousAdmin)
