from django.contrib import admin
from .models import MockSubscription

# Register your models here.

class MockSubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MockSubscription._meta.fields]

admin.site.register(MockSubscription, MockSubscriptionAdmin)
