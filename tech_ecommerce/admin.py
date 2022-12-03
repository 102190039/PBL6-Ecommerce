from django.contrib import admin

from tech_ecommerce.models import Interactive, Options, CartItem, Categories, ImgProducts, ProductChilds, ProductVariants, Products
# Register your models here.

admin.site.register(Categories)
admin.site.register(Products)
admin.site.register(ProductChilds)
admin.site.register(ImgProducts)
admin.site.register(ProductVariants)
admin.site.register(Options)
admin.site.register(CartItem)
admin.site.register(Interactive)