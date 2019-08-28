from django.contrib import admin
from .models import *


class SecurityTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SecurityType._meta.fields]


admin.site.register(SecurityType, SecurityTypeAdmin)


class SecurityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Security._meta.fields]


admin.site.register(Security, SecurityAdmin)


class HoldingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Holding._meta.fields]


admin.site.register(Holding, HoldingAdmin)