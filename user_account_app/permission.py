from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import *
from songs_app.models import Album
from rest_framework import permissions
from guardian.shortcuts import get_perms


User = get_user_model()


# the importand note thats in this case of use model permission we only 
# remove the permission that only works if we add the permission is not
#  work because all the permission is auto enable ok.
def set_the_staff_permission(gmail):
    try:
        user = User.objects.get(gmail=gmail)
        ct = ContentType.objects.get_for_model(Album)
        views_song = Permission.objects.get(codename = 'delete_album',content_type=ct)
        updates_song = Permission.objects.get(codename='change_album',content_type=ct)
        remove_permission = Permission.objects.filter(codename__in =['add_album','view_album','delete_album','change_album'],content_type =ct)
        user.user_permissions.set([views_song,updates_song])
        user.user_permissions.remove(*remove_permission)
        return True

    except User.DoesNotExist:
        return False
    
class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_superuser)
    
class IsOwnerAndSuperuserOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user=request.user

        if not user or not user.is_authenticated:
            return False

        if user and user.is_superuser:
            return True
        # if request.method in ['PUT', 'PATCH']:
        #     return False
        if user and user.is_staff:
            return request.method in permissions.SAFE_METHODS
        return obj.user==user
        # Only allow if user is the owner

class Issuper_user_only_other_readonly(permissions.BasePermission):
    def has_permission(self, request, view):
        user= request.user
        if user.is_authenticated and user.is_superuser:
            return True
        if user.is_authenticated and request.method in permissions.SAFE_METHODS:
            return True
        return False
        


class isOwnerorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user=request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in ['PUT','PATCH']:
            return user.has_perm('change_playlist',obj)
        return False
    
