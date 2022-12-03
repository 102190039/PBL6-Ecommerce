from django.contrib import admin

from order_payment.models import Order, OrderDetail, PayIn, PayOut, Payment

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Payment)
admin.site.register(PayIn)
admin.site.register(PayOut)