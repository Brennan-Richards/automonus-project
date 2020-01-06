from django.contrib import admin
from .models import MockSubscription, PaymentOrder

# Register your models here.

class MockSubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MockSubscription._meta.fields]

admin.site.register(MockSubscription, MockSubscriptionAdmin)

class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentOrder._meta.fields]

admin.site.register(PaymentOrder, PaymentOrderAdmin)
