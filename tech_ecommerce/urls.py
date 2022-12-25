
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tech_ecommerce.views import CartItemViewSet, CategoryViewSet, ImgProductViewSet, InteractiveViewSet, OptionViewSet, ProductChildViewSet, ProductListView, ProductVariantViewSet, ProductViewSet, SpeficicationViewSet

router = DefaultRouter()
router.register(r'product', ProductViewSet, basename='product_crud')
router.register(r'category', CategoryViewSet, basename='category_crud')
router.register(r'product-speficication', SpeficicationViewSet, basename='speficication')
router.register(r'product-images', ImgProductViewSet, basename='img_crud')
router.register(r'product-childs', ProductChildViewSet, basename='product_child')
router.register(r'product-variants', ProductVariantViewSet, basename='product_variant')
router.register(r'product-variant-options', OptionViewSet, basename='option')
router.register(r'cart-item', CartItemViewSet, basename='cart_item')
router.register(r'interactive', InteractiveViewSet, basename='interactive')
router.register(r'product-list', ProductListView, basename='product_list')


urlpatterns = [
    path('', include(router.urls)),
    #path('product-list/', ProductListView.as_view()),
]