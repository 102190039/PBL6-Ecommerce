from datetime import datetime
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from authenticate.models import Seller, UserProfile


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields =('id','name','content_type')
class GroupSerializer(serializers.ModelSerializer):
    permissions=PermissionSerializer(many=True)
    class Meta:
        model = Group
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =('gender', 'birthday','phone','address','account_no','item_count','avt')
        # fields= "__all__"
        
class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ['username', 'password','first_name', 'last_name','email', 'userprofile']
        extra_kwargs = {          
            'password': {'write_only': True,'required': False},
            #'email': {'required': True},   
            }

    def create(self, validated_data):
        profile = validated_data.pop('userprofile')
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        UserProfile.objects.create(user=user,**profile)
        user_group = Group.objects.get(name="USER")
        user.groups.add(user_group)
        return user

    def update(self, instance, validated_data):
        profile = validated_data.pop('userprofile')
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.email = validated_data.get('email',instance.email)
        instance.save()
        userprofile= instance.userprofile
        userprofile.gender = profile.get('gender',userprofile.gender)
        userprofile.birthday = profile.get('birthday',userprofile.birthday)
        userprofile.address = profile.get('address',userprofile.address)
        userprofile.phone = profile.get('phone',userprofile.phone)
        userprofile.account_no = profile.get('account_no',userprofile.account_no)
        userprofile.item_count = profile.get('item_count',userprofile.item_count)
        userprofile.avt = profile.get('avt',userprofile.avt)
        userprofile.save()
        return instance

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password','first_name', 'last_name','email','is_staff']
        extra_kwargs = {'password': {'write_only': True}}

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
        user_group = Group.objects.get(name=role)
        user.groups.add(user_group)
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
    def create(self, validated_data):
        user_profile = validated_data.get('user')
        user = User.objects.get(userprofile=user_profile)
        supplier = Seller.objects.create(**validated_data)
        user_group = Group.objects.get(name="SELLER")
        user.groups.add(user_group)
        profile = UserProfile.objects.get(user_id=user_profile)
        profile.is_seller = True
        profile.save()
        return supplier
    def update(self, instance, validated_data):
        instance.modified_at = datetime.now()
        instance.account_no = validated_data.get('account_no',instance.account_no)
        instance.name_store = validated_data.get('name_store',instance.name_store)
        instance.facebook = validated_data.get('facebook',instance.facebook)
        instance.product_count = validated_data.get('product_count',instance.product_count)
        instance.follower_count = validated_data.get('follower_count',instance.follower_count)
        instance.rating_average = validated_data.get('rating_average',instance.rating_average)
        instance.response_rate = validated_data.get('response_rate',instance.response_rate)
        instance.logo = validated_data.get('logo',instance.logo)
        instance.sku = validated_data.get('sku',instance.sku)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_newpass = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['old_password', 'new_password','confirm_newpass']
