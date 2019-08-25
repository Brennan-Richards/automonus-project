from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class AccountTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AccountType._meta.fields]


admin.site.register(AccountType, AccountTypeAdmin)


class AccountSubTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AccountSubType._meta.fields]


admin.site.register(AccountSubType, AccountSubTypeAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Currency._meta.fields]


admin.site.register(Currency, CurrencyAdmin)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Institution._meta.fields]


admin.site.register(Institution, InstitutionAdmin)


class UserInstitutionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserInstitution._meta.fields]


admin.site.register(UserInstitution, UserInstitutionAdmin)


class AccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Account._meta.fields]


admin.site.register(Account, AccountAdmin)