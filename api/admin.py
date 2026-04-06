from django.contrib import admin
from .models import Item, RentalTransaction

admin.site.register(Item)
admin.site.register(RentalTransaction)