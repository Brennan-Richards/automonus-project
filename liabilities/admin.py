from django.contrib import admin
from .models import *

# Register your models here.

class StudentLoanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StudentLoan._meta.fields]


admin.site.register(StudentLoan, StudentLoanAdmin)

class StudentLoanSnapshotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StudentLoanSnapshot._meta.fields]


admin.site.register(StudentLoanSnapshot, StudentLoanSnapshotAdmin)


class DisbursementDateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DisbursementDate._meta.fields]


admin.site.register(DisbursementDate, DisbursementDateAdmin)


class ServicerAddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServicerAddress._meta.fields]


admin.site.register(ServicerAddress, ServicerAddressAdmin)

class CreditCardSnapshotAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CreditCardSnapshot._meta.fields]


admin.site.register(CreditCardSnapshot, CreditCardSnapshotAdmin)

class CreditCardAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CreditCard._meta.fields]


admin.site.register(CreditCard, CreditCardAdmin)

class APRAdmin(admin.ModelAdmin):
    list_display = [field.name for field in APR._meta.fields]


admin.site.register(APR, APRAdmin)

class LiabilityAnalysisAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LiabilityAnalysis._meta.fields]


admin.site.register(LiabilityAnalysis, LiabilityAnalysisAdmin)

class GuarantorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Guarantor._meta.fields]


admin.site.register(Guarantor, GuarantorAdmin)
