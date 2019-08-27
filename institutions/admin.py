from django.contrib import admin
from . models import *


class InstitutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Institution._meta.fields]


admin.site.register(Institution, InstitutionAdmin)


class UserInstitutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserInstitution._meta.fields]


admin.site.register(UserInstitution, UserInstitutionAdmin)
