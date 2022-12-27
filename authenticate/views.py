
import traceback
from django.contrib.auth.models import Group
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework_simplejwt.views import TokenObtainPairView
from authenticate.models import Seller, UserProfile
from authenticate.serializers import AdminSerializer, AvtSerializer, GroupSerializer, LoginSerializer, SellerSerializer, PasswordSerializer, UserSerializer
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
from rest_framework.decorators import action


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class Logout(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        return Response({"message": "Goodbye!"},status=status.HTTP_200_OK)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        # serializer = self.serializer_class(data=request.data)
        usernameData = request.data.get("username")
        passwordData = request.data.get("password")
        user = authenticate(request=request,
            username=usernameData,
            password=passwordData
        )
        if user and user.is_active:
            token = get_tokens_for_user(user)
            role = []
            for group in user.groups.all():
                role.append(group.name)
            return Response({
                "message": "login is success!",
                "data": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": role
                },
                "token": token,
            }, status=status.HTTP_200_OK)
        else:
            try:
                user = User.objects.get(username=usernameData) 
                if user.is_active != True:       
                    user.delete()
                return Response({
                        "ERROR": "username or password is not correct"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except:
                pass
            return Response({
                    "ERROR": "username or password is not correct"
                }, status=status.HTTP_400_BAD_REQUEST)
class ComfirmAccount(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'comfirm.html'
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            id= request.query_params['id']
            user = User.objects.get(pk=id)
            user.is_active=True
            user.save()
            currentSite = get_current_site(request).domain
            realativeLink = reverse('login_token')
            url = 'http://' + currentSite + realativeLink
            return Response({
                'name': user.first_name,
                'login': url 
            })
        except Exception as e:
            traceback.print_exc()
            return Response({
                'ERROR': '',
            }, status=status.HTTP_400_BAD_REQUEST)

# Register user
class UserView(ViewSet):
    # serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in [ 'retrieve', 'update']:
            return [IsAuthenticated(), ]
        if self.action in ['create','comfirm_account']:
            return [AllowAny(), ]
        return super().get_permissions()

    def retrieve(self, request, pk=None):     
        try:
            user = User.objects.get(pk=pk)           
            serializer = UserSerializer(instance= user)
            return Response({
                    "data":serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({
                    "error": f'Exception: {e}'
                }, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'],detail=False,permission_classes=[AllowAny])    
    def comfirm_account(self, request):
        try:
            id= request.query_params['id']
            user = User.objects.get(pk=id)
            user.is_active=True
            user.save()
            currentSite = get_current_site(request).domain
            realativeLink = reverse('login_token')
            url = 'http://' + currentSite + realativeLink
            return Response({
                'message': 'Comfirm successfully',
                'login': url 
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            traceback.print_exc()
            return Response({
                'ERROR': '',
            }, status=status.HTTP_400_BAD_REQUEST)


    def create(self, request):
        data= request.data
        data['is_active'] = False
        serializer = UserSerializer(data=data)
        emailData = data["email"]
        if not serializer.is_valid():
            return Response({
                "ERROR": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     isValidEmail = validate_email(emailData, verify=True,smtp_timeout=20)
        # except:
        #     traceback.print_exc()
        # if isValidEmail:

        serializer.save()
        try:
        # isValidEmail = validate_email(emailData, verify=True)
            currentSite = get_current_site(request).domain
            realativeLink = reverse('comfirm_account')
            url = 'http://' + currentSite + realativeLink+f'?id={serializer.data["id"]}'
            send_mail(
                subject='Confirm Registration: PBL6 Tech E',
                message=  'Thank you for registering with Tech E! \n'
                        + f'This email is confirmation that the user {serializer.data["first_name"]} is registering for a new account.\n'
                        + 'Click here to finish the registration process: '+ url,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[emailData]
            )
            return Response({
                "message": "Registration Success!",
                'detail': 'Please check your mail to complete register!!!',
            }, status=status.HTTP_200_OK)
        except:
            traceback.print_exc()
            return Response({
                'ERROR': 'Email not exist! Please re-enter email!!!',
            }, status=status.HTTP_400_BAD_REQUEST)

        # return Response({
        #     'ERROR': 'Email not exist! Please re-enter email!!!',
        # }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request,pk):     
        try:
            user = User.objects.get(pk=pk)          
            serializer = UserSerializer(instance=user,data=request.data)
            if not serializer.is_valid():
                return Response({
                    "ERROR": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "message": "Update Profile completed!",
                "data":serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({
                    "ERROR": f'Exception: {e}'
                }, status=status.HTTP_400_BAD_REQUEST)
    
    # update user's avt
    @action(methods=['PUT'],detail=True,permission_classes=[IsAuthenticated],url_path="upload-avt")    
    def update_image(self, request, pk=None):
        try:
            userId = self.request.user.id
            user = UserProfile.objects.get(pk=userId)   
            serializer = AvtSerializer(instance=user,data=request.data)
            if not serializer.is_valid():
                return Response({
                    "ERROR": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                "message": "Update Profile completed!",
                "data":serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                    "ERROR": f'Exception: {e}'
                }, status=status.HTTP_400_BAD_REQUEST)

# Register admin
class AdminView(APIView):
    serializer_class = AdminSerializer
    permission_classes = [group_permission.IsAdmin, ]

    def get(self, request, pk=None):
        if pk is not None:
            user = User.objects.filter(pk=pk).get()
            serializer = UserSerializer(instance= user)
            return Response(serializer.data)
        manyUser = User.objects.all()
        serializer = UserSerializer(instance= manyUser,many=True)
        return Response({
            "data":serializer.data
        }, status=status.HTTP_200_OK) 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        emailData = request.data["email"]
        usernameData = request.data["username"]
        passwordData = request.data["password"]
        isValidEmail = validate_email(emailData, verify=True)
        if isValidEmail:
            if not serializer.is_valid():
                return Response({
                    "message": "Register is Failed!",
                    "error": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=emailData, username=usernameData).exists():
                return Response({
                    "Error": "This email or username exists!"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            send_mail(
                subject='Register account staff is success!',
                message='Your information account: \nusername: ' +
                usernameData+'\npassword: '+passwordData,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[emailData]
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
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            "message": "Update Profile completed!",
            "data":serializer.data
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
        return Response({
            "role": role
        }, status=status.HTTP_200_OK)

class GroupAndPermissionView(APIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser, ]
    queryset = Group.objects.all()

    def get(self, request):
        groups = Group.objects.all()
        serializer= GroupSerializer(groups,many=True)
        return Response({
            "data":serializer.data
        }, status=status.HTTP_200_OK)

#Register seller
class SellerView(ViewSet):
    serializer_class = SellerSerializer
    def get_permissions(self):
        if self.action in ['list', 'destroy'] :
            return [IsAdminUser(),] 
        if self.action in ['retrieve'] :
            return [AllowAny(),] 
        if self.action in ['create'] :
            return [group_permission.IsUser(),] 
        if self.action in ['update'] :
            return [group_permission.IsSeller(),] 
        return super().get_permissions()
    def list(self, request):
        queryset = Seller.objects.all()
        serializer = SellerSerializer(queryset, many=True)
        return Response({
            "data":serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            seller = Seller.objects.get(pk=pk)           
            serializer = SellerSerializer(instance= seller)
            return Response({
                    "data":serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({
                    "ERROR": f'Exception: {e}'
                }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        data = request.data
        userId = self.request.user.id
        if userId != int(data["user"]):
            return Response({
                "ERROR": f"Not allowed to register seller of user {data['user']}!",
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = SellerSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "ERROR":serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            "message":"Create Seller is success!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    def update(self, request, pk=None):
        userId = self.request.user.id
        if userId != int(pk):
            return Response({
                "ERROR": f"Not allowed to update the seller {pk}!",
            }, status=status.HTTP_403_FORBIDDEN)
        seller = Seller.objects.get( pk=pk)     
        serializer = SellerSerializer(instance=seller, data=request.data)
        if not serializer.is_valid():
            return Response({
                "ERROR":serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            "message":"Seller updated is sucess!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        try:
            seller = Seller.objects.get(pk=pk)           
            seller.delete()
            return Response({
                "message":"Seller deleted is success!"
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
             return Response({
                    "ERROR": f'Exception: {e}'
                }, status=status.HTTP_404_NOT_FOUND)

class PasswordView(APIView):
    def get_permissions(self):
        if self.request.method in ['POST']:
            self.permission_classes = [AllowAny, ]
        if self.request.method in ['PATCH']:
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()
        
    # reset password
    def post(self, request):
        serializer = PasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "ERROR": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        emailData = request.data["email"]
        isValidEmail = validate_email(emailData, verify=True)
        if isValidEmail:
            if User.objects.filter(email=emailData).exists():
                user = User.objects.get(email=emailData)
                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()
                currentSite = get_current_site(request).domain
                realativeLink = reverse('login_token')
                url = 'http://' + currentSite + realativeLink
                send_mail(
                    subject='Reset your password is success!',
                    message='Hello '+user.username+'!\n your NewPassword is ' +
                    password+'.!!\nClick link to login: '+url+'.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[emailData]
                )
                return Response({
                    "message": "Reset password Success!",
                    'detail': 'Please check your mail to complete register!!!',
                }, status=status.HTTP_202_ACCEPTED,)
            return Response({
                'ERROR': 'Email current have not in database! Please re-enter email!!!',
            }, tatus=status.HTTP_400_BAD_REQUEST)
        return Response({
            'ERROR': 'Email not exist! Please re-enter email!!!',
        }, status=status.HTTP_400_BAD_REQUEST)

    #change password
    def patch(self, request):
            user = self.request.user
            data = request.data
            serializer = PasswordView(instance=user, data=data)
            if serializer:
                oldPassword = serializer.data['old_password']
                newPassword = serializer.data['new_password']
                confirmNewpass = serializer.data['confirm_newpass']
                if not user.check_password(oldPassword):
                    return Response({
                        'ERROR':'old_password is incorrect!'
                    }, status=status.HTTP_400_BAD_REQUEST)
                if confirmNewpass != newPassword:
                    return Response({   
                        'ERROR':'confirm_password is incorrect!'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.set_password(serializer.data['new_password'])
                user.save()
                return Response({
                    'message':'changepassword is success!',
                    "data":serializer.data
                }, status=status.HTTP_202_ACCEPTED)
            return Response({
                'ERROR': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


    


