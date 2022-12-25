from datetime import datetime
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from authenticate.models import Seller, UserProfile
from order_payment.models import PayOut


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields =('id','name','content_type')
class GroupSerializer(serializers.ModelSerializer):
    permissions=PermissionSerializer(many=True)
    class Meta:
        model = Group
        fields = '__all__'

class AvtSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avt']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =('gender', 'birthday','phone','address','account_no','cart_count','avt')
        create_only_fields = ["cart_count"]
    def get_photo_url(self, obj):
        request = self.context.get('request')
        avt_url = obj.avt.url
        return request.build_absolute_uri(avt_url)
        
class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = ['id','username', 'password','first_name', 'last_name','email', 'user_profile']
        extra_kwargs = {
            'password': {'write_only': True,'required': False},
            'username': {'required': False}}
        create_only_fields = ["username"]

    def to_representation(self, instance):
        role = []
        for group in instance.groups.all():
            role.append(group.name)
        response = super().to_representation(instance)
        response['ROLE'] = role
        return response

    def create(self, validated_data):
        profile = validated_data.pop('user_profile')
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        UserProfile.objects.create(user=user,**profile)
        user_group = Group.objects.get(name="USER")
        user.groups.add(user_group)
        return user

    def update(self, instance, validated_data):
        profile = validated_data.pop('user_profile')
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.email = validated_data.get('email',instance.email)
        instance.save()
        userProfile= instance.user_profile
        userProfile.gender = profile.get('gender',userProfile.gender)
        userProfile.birthday = profile.get('birthday',userProfile.birthday)
        userProfile.address = profile.get('address',userProfile.address)
        userProfile.phone = profile.get('phone',userProfile.phone)
        userProfile.account_no = profile.get('account_no',userProfile.account_no)
        userProfile.save()
        return instance

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password','first_name', 'last_name','email','is_staff']
        extra_kwargs = {
            'password': {'write_only': True,'required': False},
            'username': {'required': False}}
        write_once_fields = ["username"]

    def to_representation(self, instance):
        role = []
        for group in instance.groups.all():
            role.append(group.name)
        response = super().to_representation(instance)
        response['ROLE'] = role
        return response

    def create(self, validated_data):
        user = User.objects.create_superuser(**validated_data)
        user.set_password(validated_data['password'])
        role = validated_data['is_staff']
        if role:
            role="STAFF"
            user.is_superuser =False
        else:
            role="ADMIN"
        user.save()
        userGroup = Group.objects.get(name=role)
        user.groups.add(userGroup)
        return user

class LoginSerializer(TokenObtainPairSerializer):
    class Meta:
        model: User
        field = ['username','password']

class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email',]

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'
        extra_kwargs ={"user":{'required':False}}
        write_once_fields = ["user"]

    def get_photo_url(self, obj):
        request = self.context.get('request')
        logo_url = obj.logo.url
        return request.build_absolute_uri(logo_url)

    def create(self, validated_data):
        userProfile = validated_data.get('user')
        user = User.objects.get(user_profile=userProfile)
        seller = Seller.objects.create(**validated_data)
        accountNo = validated_data.get('account_no')
        PayOut.objects.create(seller=seller, account = accountNo)

        userGroup = Group.objects.get(name="SELLER")
        user.groups.add(userGroup)
        profile = UserProfile.objects.get(user_id=userProfile)
        profile.is_seller = True
        profile.save()
        return seller

    def update(self, instance, validated_data):
        # instance.modified_at = datetime.now()
        # instance.account_no = validated_data.get('account_no',instance.account_no)
        # instance.name_store = validated_data.get('name_store',instance.name_store)
        # instance.facebook = validated_data.get('facebook',instance.facebook)
        # instance.product_count = validated_data.get('product_count',instance.product_count)
        # instance.follower_count = validated_data.get('follower_count',instance.follower_count)
        # instance.rating_average = validated_data.get('rating_average',instance.rating_average)
        # instance.response_rate = validated_data.get('response_rate',instance.response_rate)
        # instance.logo = validated_data.get('logo',instance.logo)
        # instance.save()
        PayOut = instance.pay_out
        PayOut.account = instance.account_no
        PayOut.save()
        return super().update(instance, validated_data)
        
        

