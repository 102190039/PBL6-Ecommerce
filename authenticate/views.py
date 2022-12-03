
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from authenticate.models import Seller
from authenticate.serializers import AdminSerializer, GroupSerializer, LoginSerializer, SellerSerializer, PasswordSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from rest_framework import status
from django.urls import reverse
from validate_email import validate_email
from django.contrib.auth import authenticate
from authenticate import group_permission
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from tech_e import settings
from tech_ecommerce.models import Categories, Products


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    # def get_permissions(self):
    #     # if self.request.method in [ 'GET', 'PUT','PATCH']:
    #     #     self.permission_classes = [IsAuthenticated, ]

    #     if self.request.method in ['GET', 'PUT','PATCH','POST']:
    #         self.permission_classes = [AllowAny, ]
    #     return super().get_permissions()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        username_data = request.data.get("username")
        password_data = request.data.get("password")
        user = authenticate(request=request,
            username=username_data,
            password=password_data
        )
        if user and serializer.is_valid():
            token = get_tokens_for_user(user)
            
            return Response({
                "message": "login is success!",
                "data": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name:": user.last_name,
                    "role": user.groups.all()[0].name,
                },
                "token": token,
            })
        else:
            return Response({"massage": "Login is failed",
                            "error": "username or password is not correct"
                             }, status=status.HTTP_200_OK)


class ResetPassword(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = PasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({
                "message": "Reset password is Failed!",
                "error": serializer.errors,
            })

        email_data = request.data["email"]
        is_valid_email = validate_email(email_data, verify=True)
        if is_valid_email:

            if User.objects.filter(email=email_data).exists():
                user = User.objects.get(email=email_data)
                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()
                current_site = get_current_site(request).domain
                realativeLink = reverse('login_token')
                url = 'http://' + current_site + realativeLink
                send_mail(
                    subject='Reset your password is success!',
                    message='Hello '+user.username+'!\n your NewPassword is ' +
                    password+'.!!\nClick link to login: '+url+'.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email_data]
                )
                return Response({
                    "message": "Reset password Success!",
                    'detail': 'Please check your mail to complete register!!!',
                },
                    status=status.HTTP_200_OK,
                )
            return Response({
                "message": "Reset password is Failed!",
                'error': 'Email current have not in database! Please re-enter email!!!',
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({
            "message": "Reset password is Failed!",
            'error': 'Email not exist! Please re-enter email!!!',
        },
            status=status.HTTP_400_BAD_REQUEST
        )


# Register
class UserView(APIView):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in [ 'GET', 'PUT','PATCH']:
            self.permission_classes = [IsAuthenticated, ]

        if self.request.method in ['POST']:
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def get(self, request, pk=None):     
        user = User.objects.filter(pk=pk).get()
        serializer = UserSerializer(instance= user)
        return Response(serializer.data)
        
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email_data = request.data["email"]
        username_data = request.data["username"]
        password_data = request.data["password"]
        is_valid_email = validate_email(email_data, verify=True)
        if is_valid_email:
            if not serializer.is_valid():
                return Response({
                    "message": "Register is Failed!",
                    "error": serializer.errors,
                })
            if User.objects.filter(username=username_data).exists():
                return Response({
                    "message": "Register is Failed!",
                    "error": "This email or username exists!"})

            serializer.save()
            send_mail(
                subject='Register account user is success!',
                message='Your information account: \nusername: ' +
                username_data+'\npassword: '+password_data,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email_data]
            )
            return Response({
                "message": "Registration Success!",
                'detail': 'Please check your mail to complete register!!!',
            }, status=status.HTTP_200_OK,)
        return Response({
            "message": "Register is Failed!",
            'error': 'email not exist! Please re-enter email!!!',
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,pk):     
        user = User.objects.filter(pk=pk).get()
        serializer = self.serializer_class(instance=user,data=request.data)
        if not serializer.is_valid():
            return Response({
                    "message": "Update Profile is failed!",
                    "error": serializer.errors,
                })
        serializer.save()
        return Response({
                "message": "Update Profile completed!",
                'detail': '',
            }, status=status.HTTP_200_OK,)

    def patch(self, request,pk):     
        user = User.objects.filter(pk=pk).get()
        serializer = self.serializer_class(instance=user,data=request.data)
        if not serializer.is_valid():
            return Response({
                    "message": "Update Profile is failed!",
                    "error": serializer.errors,
                })
        serializer.save()
        return Response({
                "message": "Update Profile completed!",
                'detail': '',
            }, status=status.HTTP_200_OK,)
        

class AdminView(APIView):
    serializer_class = AdminSerializer
    permission_classes = [group_permission.IsAdmin, ]

    def get(self, request, pk=None):
        if pk is not None:
            user = User.objects.filter(pk=pk).get()
            serializer = UserSerializer(instance= user)
            return Response(serializer.data)
        many_user = User.objects.all()
        serializer = UserSerializer(instance= many_user,many=True)
        return Response(serializer.data) 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email_data = request.data["email"]
        username_data = request.data["username"]
        password_data = request.data["password"]
        is_valid_email = validate_email(email_data, verify=True)
        if is_valid_email:
            if not serializer.is_valid():
                return Response({
                    "message": "Register is Failed!",
                    "error": serializer.errors,
                })
            if User.objects.filter(email=email_data, username=username_data).exists():
                return Response({"Error": "This email or username exists!"})

            serializer.save()
            send_mail(
                subject='Register account staff is success!',
                message='Your information account: \nusername: ' +
                username_data+'\npassword: '+password_data,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email_data]
            )
            return Response({
                "message": "Registration Success!",
                'detail': 'Please check your mail to complete register!!!',
            }, status=status.HTTP_200_OK,)
        return Response({
            "message": "Register is Failed!",
            'error': 'email not exist! Please re-enter email!!!',
        }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,pk):     
        user = User.objects.filter(pk=pk).get()
        serializer = self.serializer_class(instance=user,data=request.data)
        if not serializer.is_valid():
            return Response({
                    "message": "Update Profile is failed!",
                    "error": serializer.errors,
                })
        serializer.save()
        return Response({
                "message": "Update Profile completed!",
                'detail': '',
            }, status=status.HTTP_200_OK,)
    def delete(self, request, *args, **kwargs):
        pass

class RoleView(APIView):
    permission_classes = [AllowAny, ]
    def get(self, request):
        groups = Group.objects.all()
        role = {}
        for group in groups:
            role[group.id] = group.name         
        return Response({"role": role})

class GroupAndPermissionView(APIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser, ]
    queryset = Group.objects.all()

    def get(self, request):
        groups = Group.objects.all()
        serializer= GroupSerializer(groups,many=True)
        return Response(serializer.data)

class SellerView(ViewSet):
    def get_permissions(self):
        if self.action in ['list','retrieve','create','update', 'destroy'] :
            return [AllowAny(),] 
        return super().get_permissions()
    # List admin mới dc quyen truy cap
    def list(self, request):
        queryset = Seller.objects.all()
        serializer = SellerSerializer(queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, pk=None):
        queryset = Seller.objects.all()
        seller = get_object_or_404(queryset, pk=pk)
        serializer = SellerSerializer(seller)
        return Response(serializer.data)

    def create(self, request):
        seializer = SellerSerializer(data=request.data)
        if not seializer.is_valid():
            return Response({
                "message":"Create Seller is Failed!",
                "errors":seializer.errors
            })
        seializer.save()
        return Response({
            "message":"Create Seller is success!",
            "data": seializer.data
        })
    def update(self, request, pk=None):
        queryset = Seller.objects.all()
        seller = get_object_or_404(queryset, pk=pk)
        serializer = SellerSerializer(instance=seller, data=request.data)
        if not serializer.is_valid():
            return Response({
                "message":"Seller updated is failed!",
                "errors":serializer.errors,
            }
            )
        serializer.save()
        return Response({
            "message":"Seller updated is sucess!"
        },
        status=status.HTTP_204_NO_CONTENT
        )
    def destroy(self, request, pk=None):
        queryset = Seller.objects.all()
        seller = get_object_or_404(queryset, pk=pk)
        seller.delete()
        return Response({
            "message":"Seller deleted is success!"
        })

class ChangePasswordView(APIView):
    def get_permissions(self):
        if self.request.method in ['PATCH']:
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()
    def patch(self, request):
            user = self.request.user
            data = request.data
            serializer = ChangePasswordView(instance=user, data=data)
            if serializer:
                old_password = serializer.data['old_password']
                new_password = serializer.data['new_password']
                confirm_newpass = serializer.data['confirm_newpass']
                if not user.check_password(old_password):
                    return Response(
                        {'message':'old_password is incorrect!',
                        'errors': serializer.errors
                        },
                    )
                if confirm_newpass != new_password:
                    return Response(
                        {'message':'confirm_password is incorrect!',
                        'errors': serializer.errors
                        },
                    )
                user.set_password(serializer.data['new_password'])
                user.save()
                return Response({
                    'message':'changepassword is success!'},
                    status=status.HTTP_205_RESET_CONTENT
                )
            return Response({
                'message':'changepassword is fail!',
                'errors': serializer.errors
                },
            )




