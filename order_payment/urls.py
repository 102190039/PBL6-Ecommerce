from django.urls import include, path
from rest_framework.routers import DefaultRouter

from order_payment.views import OrderDetailViewSet, OrderViewSet, PayInViewSet, PayPalView, PurchasedProductView


router = DefaultRouter()
router.register(r'order', OrderViewSet, basename='order')
router.register(r'order-details', OrderDetailViewSet, basename='order_detail')
router.register(r'checkout', PayInViewSet, basename='checkout')
router.register(r'checkout-paypal', PayPalView, basename='paypal')
router.register(r'purchased', PurchasedProductView, basename='purchased')



urlpatterns = [
    path('', include(router.urls)),
]