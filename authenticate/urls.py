
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from authenticate.views import  AdminView, ChangePasswordView, GroupAndPermissionView, LoginView,  ResetPassword, RoleView, SellerView,  UserView


# app_name="authenticate"
router = DefaultRouter()
#Supplier
router.register('seller', SellerView, basename='seller')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login_token'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('resetpassword/', ResetPassword.as_view(), name='resetpassword'),

    path('register/',UserView.as_view(), name='register'),
    path('profile/<int:pk>/',UserView.as_view(), name='profile'),
    # path('profile/<int:pk>/',UserView.as_view(), name='profile-update'),

    path('register-admin/',AdminView.as_view(), name='register-admin'), 
    path('admin-profile/',AdminView.as_view(), name='admin-profile'),
    # path('admin-profile/<int:pk>/',AdminView.as_view(), name='admin-profile-one'),
    path('admin-profile/<int:pk>/',AdminView.as_view(), name='admin-profile-update'),

    path('role/',RoleView.as_view(), name='role'),
    path('group-permission/',GroupAndPermissionView.as_view(), name='group-permission'),

    path('changepassword/',ChangePasswordView.as_view(), name='changepassword'),

    path('', include(router.urls)),
]

