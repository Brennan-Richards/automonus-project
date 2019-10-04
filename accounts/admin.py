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


class AccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Account._meta.fields]


admin.site.register(Account, AccountAdmin)


class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TransactionCategory._meta.fields]


admin.site.register(TransactionCategory, TransactionCategoryAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Transaction._meta.fields]


admin.site.register(Transaction, TransactionAdmin)


class AccountSnapshotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AccountSnapshot._meta.fields]


admin.site.register(AccountSnapshot, AccountSnapshotAdmin)
