from django.contrib import admin
from .models import Display, Tax, Housing, Car, Utilities, Food, Miscellaneous

# Register your models here.

admin.site.register(Tax)

admin.site.register(Housing)

admin.site.register(Car)

admin.site.register(Utilities)

admin.site.register(Food)

admin.site.register(Miscellaneous)

admin.site.register(Display)
