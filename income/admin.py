from django.contrib import admin
from .models import *


class IncomeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Income._meta.fields]


admin.site.register(Income, IncomeAdmin)


class IncomeStreamAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IncomeStream._meta.fields]


admin.site.register(IncomeStream, IncomeStreamAdmin)
