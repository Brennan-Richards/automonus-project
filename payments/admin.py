from django.contrib import admin
from .models import MockSubscription, Bill, BillDestination

# Register your models here.

class MockSubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MockSubscription._meta.fields]

admin.site.register(MockSubscription, MockSubscriptionAdmin)


class BillAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bill._meta.fields]\

admin.site.register(Bill, BillAdmin)


class BillDestinationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BillDestination._meta.fields]\

admin.site.register(BillDestination, BillDestinationAdmin)
