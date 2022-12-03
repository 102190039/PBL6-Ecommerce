from django.contrib import admin

# Register your models here.
from .models import Seller, UserProfile

admin.site.register(UserProfile)
admin.site.register(Seller)