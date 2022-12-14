from django.db import models
from django.contrib.auth.models import User
from authenticate.models import Seller, UserProfile
from tech_ecommerce.models import ProductChilds, Products
from django.db.models.signals import pre_delete,post_save
from django.dispatch import receiver

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order')
    total_price = models.FloatField(default=0, blank=True)
    order_count = models.IntegerField(default=0, blank=True)


class OrderDetail(models.Model):
    product_child = models.ForeignKey(ProductChilds, on_delete=models.CASCADE, related_name='order_detail')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,related_name='order_detail')
    quantity = models.IntegerField(default=0, blank=True)
    price = models.FloatField(default=0, blank=True)
    total_price = models.FloatField(default=0, blank=True)
    discount = models.FloatField(default=0, blank=True)

@receiver(post_save, sender=OrderDetail)
def save_order_detail(sender,instance, **kwargs):
    product = instance.product_child.product
    product.quantity_sold += instance.quantity
    product.save()
    order = instance.order
    order.total_price+= instance.total_price
    order.order_count +=1
    order.save()
    


class PayIn(models.Model):
    TYPE_PAYMENT = [
    ('online', 'online'),
    ('offline', 'offline')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='pay_in')
    received_time = models.DateTimeField(null=True, blank=True)
    number_money = models.FloatField(default=0, blank=True)
    status_payment = models.BooleanField(max_length=20, default=False)
    type_payment = models.CharField(max_length=10, choices = TYPE_PAYMENT)


class PayOut(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, primary_key=True, related_name='pay_out')
    current_balance = models.FloatField(default=0, blank=True)
    account = models.CharField(max_length=255, blank=True)


class Payment(models.Model):
    pay_out = models.ForeignKey(PayOut, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    pay_in = models.ForeignKey(PayIn, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    money = models.FloatField()

class PurchasedProduct(models.Model):
    STATUS_PURCHASE = [
    ('delivering', 'delivering'),
    ('delivered', 'delivered'),
    ('canceled', 'canceled')]
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='purchased_products')
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField(default=0)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='purchased_products')
    status_purchase= models.CharField(max_length=20, choices = STATUS_PURCHASE, default='delivering')
# @receiver(post_save, sender=PurchasedProduct)
# def save_purchase(sender,instance, **kwargs):
#     instance.seller_id = instance.product.seller_id