
from django.contrib.auth.models import Group
from rest_framework import permissions



def IsInGroup(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """
    try:
        in_group = Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
        return in_group
    except Group.DoesNotExist:
        return False

def CheckGroupOfUser(user):
    group= user.groups.all()[0]
    return group.name



GROUPS = ['ADMIN', 'STAFF','USER','SELLER']

def AddGroup():
    admin_group = Group.objects.get_or_create(name="ADMIN")      
    staff_group = Group.objects.get_or_create(name="STAFF")
    user_group = Group.objects.get_or_create(name="USER")
    sup_group = Group.objects.get_or_create(name="SELLER")


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_superuser and request.user.is_authenticated)

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_staff and request.user.is_authenticated)

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(IsInGroup(request.user,"USER") and request.user.is_authenticated)

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(IsInGroup(request.user,"SELLER") and request.user.is_authenticated)