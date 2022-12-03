from django.db import models

from authenticate.models import Seller, UserProfile
from tech_ecommerce.models import ProductChilds

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='order')
    total_price = models.FloatField(default=0, blank=True)
    order_count = models.IntegerField(default=0, blank=True)


class OrderDetail(models.Model):
    product_child = models.ForeignKey(ProductChilds, on_delete=models.CASCADE, related_name='order_detail')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,related_name='order_details')
    quantity = models.IntegerField(default=0, blank=True)
    price = models.FloatField(default=0, blank=True)
    total_price = models.FloatField(default=0, blank=True)
    discount = models.FloatField(default=0, blank=True)


class PayIn(models.Model):
    TYPE_PAYMENT = [
    ('online', 'online'),
    ('offline', 'offline')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='pay_in')
    received_time = models.DateTimeField(null=True, blank=True)
    number_money = models.FloatField(default=0, blank=True)
    status_payment = models.BooleanField(default=False, blank=True)
    type_payment = models.CharField(max_length=10, choices = TYPE_PAYMENT)


class PayOut(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,related_name='pay_out')
    current_balance = models.FloatField(default=0, blank=True)
    account = models.CharField(max_length=14)


class Payment(models.Model):
    pay_out = models.ForeignKey(PayOut, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    pay_in = models.ForeignKey(PayIn, on_delete=models.CASCADE, related_name='payment', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    money = models.FloatField()