from django.contrib import admin
from .models import Room,Message,Product, Order
# Register your models here.

admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Product)
admin.site.register(Order)
