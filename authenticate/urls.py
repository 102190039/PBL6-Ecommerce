
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from authenticate.views import  AdminView, GroupAndPermissionView, LoginView, Logout, PasswordView, RoleView, SellerView,  UserView


# app_name="authenticate"
router = DefaultRouter()
#Supplier
router.register('seller', SellerView, basename='seller')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login_token'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('logout/', Logout.as_view(), name='logout'),
    path('password/',PasswordView.as_view(), name='password'),

    path('register/',UserView.as_view({'post': 'create'}), name='register'),
    path('profile/<int:pk>/',UserView.as_view({'get': 'retrieve','put':'update'}), name='profile'),
    path('profile/<int:pk>/upload-avt/',UserView.as_view({'put':'update_image'}), name='profile-avt'),

    path('register-admin/',AdminView.as_view(), name='register-admin'), 
    path('admin-profile/',AdminView.as_view(), name='admin-profile'),
    path('admin-profile/<int:pk>/',AdminView.as_view(), name='admin-profile-update'),

    path('role/',RoleView.as_view(), name='role'),
    path('group-permission/',GroupAndPermissionView.as_view(), name='group-permission'),

    path('', include(router.urls)),
]

