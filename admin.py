from django.contrib import admin
from .models import OrderItem,Order,Item,BillingAddress,Coupon

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','ordered']
# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Item)
admin.site.register(BillingAddress)
admin.site.register(Coupon)
