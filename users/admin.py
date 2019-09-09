from django.contrib import admin
from .models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]


admin.site.register(Profile, ProfileAdmin)