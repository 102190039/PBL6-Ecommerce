
import django_filters as filters
from tech_ecommerce.models import Products

class ProductFilter(filters.FilterSet):
    price_gte = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = filters.NumberFilter(field_name='price', lookup_expr='lte')
    rating_average_gte = filters.NumberFilter(field_name='rating_average', lookup_expr='gte')
    rating_average_lte = filters.NumberFilter(field_name='rating_average', lookup_expr='lte')
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    color = filters.CharFilter(field_name="color", lookup_expr='icontains')

    battery_gte = filters.CharFilter(field_name='specfication__battery_capacity', lookup_expr='gte')
    battery_lte = filters.CharFilter(field_name='specfication__battery_capacity', lookup_expr='lte')
    screen_gte = filters.CharFilter(field_name='specfication__screen_size', lookup_expr='gte')
    screen_lte = filters.CharFilter(field_name='specfication__screen_size', lookup_expr='lte')
    brand = filters.CharFilter(field_name="speficication__brand", lookup_expr='icontains')
    rom = filters.CharFilter(field_name="speficication__brand", lookup_expr='icontains')
    ram = filters.CharFilter(field_name="speficication__brand", lookup_expr='icontains')

    ordering = filters.OrderingFilter(fields=['category', 'price', 'rating_average'])
    class Meta:
        model = Products
        fields = ['id','price_lte','price_lte','rating_average_gte','rating_average_lte','category','seller','name','color',
        'brand','ram','rom','screen_gte','screen_gte','battery_gte','battery_lte']