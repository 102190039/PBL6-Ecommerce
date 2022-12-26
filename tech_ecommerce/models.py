

import datetime
from django.db import models
from authenticate.models import Seller, UserProfile
from django.db.models.signals import pre_delete,post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    total = models.IntegerField(default=0, blank=True)


class Products(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,related_name='products')
    category = models.ForeignKey(Categories, on_delete=models.CASCADE,related_name='products')
    name = models.CharField(max_length=255) 
    slug = models.SlugField(null=True, blank=True)
    price = models.FloatField(default=0, blank=True) 
    original_price = models.FloatField(default=0, blank=True)
    short_description = models.TextField(null=True, blank=True) 
    description = models.TextField(null=True, blank=True) 
    discount_rate = models.FloatField(default=0, blank=True)
    rating_average = models.FloatField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True)
    color = models.CharField(max_length=100,null=True, blank=True)
    quantity_sold = models.IntegerField(default=0, blank=True)
    review_count = models.IntegerField(default=0, blank=True) 
    
@receiver(post_save, sender=Products)
def save_product(sender,instance, **kwargs):
    instance.slug = f"/product/{instance.pk}/"
    instance.price = instance.original_price* (100.0-instance.discount_rate) /100.0
    instance.modified_at = datetime.datetime.today()
    instance.category.total += 1
    instance.category.save()
    instance.seller.product_count += 1
    instance.seller.save()

@receiver(pre_delete, sender = Products)
def delete_product(sender,instance,*args,**kwargs):
    category = instance.category
    category.total -= 1
    seller = instance.seller
    seller.product_count -= 1
    seller.save()
    category.save()


class ImgProducts(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='img_products')
    link = models.URLField(max_length=255)
    name = models.CharField(max_length=255)

class Speficication(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE, related_name='speficication')
    brand = models.CharField(max_length=100)
    cpu_speed = models.CharField(max_length=100, null=True, blank=True)
    gpu = models.CharField(max_length=100, null=True, blank=True)
    ram = models.CharField(max_length=100, null=True, blank=True)
    rom = models.CharField(max_length=100, null=True, blank=True)
    screen_size = models.CharField(max_length=100,null=True,blank=True)
    battery_capacity = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    chip_set = models.CharField(max_length=100, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    

class ProductChilds(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product_childs')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE,related_name='product_childs')
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0, blank=True)
    inventory_status = models.BooleanField(default=True, blank=True)
    selected = models.BooleanField(default=False, blank=True)
    thumbnail_url = models.URLField(max_length=256, null=True, blank=True)
    name_url = models.CharField(max_length=256, null=True, blank=True)
    option1 = models.CharField(max_length=256, null=True, blank=True)
    option2 = models.CharField(max_length=256, null=True, blank=True)


class ProductVariants(models.Model):
    VARIANT_CHOICES = [
    ('Màu', 'Màu'),
    ('Dung lượng', 'Dung lượng')]
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product_variants')
    name = models.CharField(max_length=10, choices = VARIANT_CHOICES, default = 'Màu')

class Options(models.Model):
    product_variant = models.ForeignKey(ProductVariants, on_delete=models.CASCADE, related_name='options')
    product_child = models.ForeignKey(ProductChilds, on_delete=models.CASCADE,related_name='options')
    value = models.CharField(max_length=100)
@receiver(post_save, sender=Options)
def save_option(sender,instance, **kwargs):
    child= instance.product_child
    if instance.product_variant == "Màu":
        child.option1 = instance.value
    if instance.product_variant == "Dung Lượng":
        child.option2 = instance.value
    child.save()   

class CartItem(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='cart_items')
    product_child = models.ForeignKey(ProductChilds, on_delete=models.CASCADE,related_name='cart_items')
    quantity = models.IntegerField(default=0, blank=True)
    total_price = models.FloatField(default=0, blank=True)

@receiver(pre_delete, sender = CartItem)
def delete_cart(sender,instance,*args,**kwargs):
    user = instance.user
    user.cart_count = user.cart_count-1 if user.cart_count>0 else 0
    user.save()

class Interactive(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name='interactives')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='interactive')
    favorite = models.BooleanField(default=True)
    comment = models.TextField()
    link = models.URLField(max_length=255, null=True, blank=True)
    rating = models.IntegerField(default=0)
    time_interactive = models.DateTimeField(auto_now=True, blank=True)

@receiver(post_save, sender=Interactive)
def save_interactive(sender,instance, **kwargs):
    product = instance.product
    product.review_count +=1 
    product.rating_average = (product.rating_average + instance.rating)/2 
    product.save()