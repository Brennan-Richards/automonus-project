from django.contrib import admin
from .models import *

# Register your models here.

class AbstractStudentLoanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AbstractStudentLoan._meta.fields]


admin.site.register(AbstractStudentLoan, AbstractStudentLoanAdmin)
