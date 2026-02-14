from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.db.models import F, Max, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status  # type: ignore
from rest_framework import filters, generics, pagination, viewsets
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import api_view
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import *
from .permission import *
from .serializers import *

User = get_user_model()

class create_normal_user(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class=customusserSerializer

class get_user(generics.ListAPIView):
    # authentication_classes=[SessionAuthentication]
    permission_classes = [IsAuthenticated,IsOwnerAndSuperuserOnly]
    serializer_class=get_all_user

    def get_queryset(self):
        user = self.request.user
        queryset =(CustomUser.objects)

        if user.is_superuser or user.is_staff:
            return queryset.all()
        return queryset.filter(id=self.request.user.id)

class create_staff_user_views(APIView):
    permission_classes = [IsAdminUser]
    def post(self,request):
        data = request.data
        try:
            CustomUser.objects.create_staff(
                gmail=data['gmail'],
                password=data['password'],
                user_name=data.get('user_name',''),
                phone_number=data.get('phone_number',''),
                photo_url=request.FILES.get('photo_url')
            )
            return Response({"staff is create successfully"},201)
        except Exception as e:
            return Response({"error"},Http404)

@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginApiView(APIView):
    def post(self,request):
        token = request.data.get('google_id_token')

        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience='234888009676-8iovn6e2h9p2hdc3upskfu99ssjkjoho.apps.googleusercontent.com'
        )

        gmail = info['email']
        name = info.get('name')
        picture = info.get('picture')

        user,create =User.objects.get_or_create(gmail = gmail, defaults={"user_name":name,"photo_url":picture})
    
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    )

# work code for django model permission

class set_staff_permission_views(APIView):
    def get(self,request,gmail):
        # gmail = request.data.get('gmail')
        result=set_the_staff_permission(gmail=gmail)
        if result:
            return Response({"message":f"the permission set to user successfully {gmail}"},200)
        return Response({"message":"the permission not set"},404)

# class set_staff_permission_view(APIView):
#     permission_classes = [IsAdminUser]
#     authentication_classes=[SessionAuthentication]

#     def post(self, request):
#         email = request.data.get("email")

#         if not email:
#             return Response(
#                 {"error": "Email is required"},
#                 status=400
#             )

#         success = set_the_staff_permission(email)

#         if success:
#             return Response(
#                 {"message": "Song editor permissions assigned"},
#                 status=200
#             )

#         return Response(
#             {"error": "User or permission not found"},
#             status=404
#         )
    

class check_login_user(APIView):
    def post(self, request):
        try:
            gmail = request.data.get("gmail")
            if not gmail:
                return Response({"error": "gmail is required"}, status=400)
            
            request.session.flush()   # 🔥 CLEAR OLD SESSION COMPLETELY

            try:
                user = User.objects.get(gmail=gmail)
            except User.DoesNotExist:
                return Response({"message": "user does not exist"}, status=404)
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # or your custom backend
            login(request, user)
            return Response({"message": "user login successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


from django.contrib.auth import logout

class LogoutUser(APIView):
    def get(self, request):
        logout(request)
        return Response({"message": "User logged out"}, status=200)


################################################ just for demo ################################################

class Gmailonlyjwtview(APIView):
    def post(self,request):
        gmail = request.data.get('gmail')

        if not gmail:
            return Response({"message":"require gamil id"})
        
        try:
            user = User.objects.get(gmail=gmail)
        except User.DoesNotExist:
                return Response({"message": "user does not exist"}, status=404)
        
        refresh = RefreshToken.for_user(user)

        return Response({"access":str(refresh.access_token),
                         "refresh":str(refresh),"user":str(user)
                         },200)