
from django.db import models
from authenticate.models import Seller, UserProfile

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


class ImgProducts(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='img_products')
    link = models.URLField(max_length=255)


class Speficication(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE)
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
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0, blank=True)
    inventory_status = models.BooleanField(default=True, blank=True)
    selected = models.BooleanField(default=False, blank=True)
    thumbnail_url = models.URLField(max_length=100, null=True, blank=True)


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
    

class CartItem(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='cart_items')
    product_child = models.ForeignKey(ProductChilds, on_delete=models.CASCADE,related_name='cart_items')
    quantity = models.IntegerField(default=0, blank=True)
    total_price = models.FloatField(default=0, blank=True)


class Interactive(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,related_name='interactive')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='interactive')
    favorite = models.BooleanField(default=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=255, null=True, blank=True)
    rating = models.IntegerField(default=0, blank=True)
    time_interactive = models.DateTimeField(auto_now=True, blank=True)