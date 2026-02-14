from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns=[
    path("create_normal_user/",create_normal_user.as_view(),name='create normal user'),
    path("create_staff/",create_staff_user_views.as_view(),name='create staff user'),
    path("get_staff/",get_user.as_view(),name='staff user'),
    path("auth/google/", GoogleLoginApiView.as_view()),
    path("set_staff_permission_views/<str:gmail>/",set_staff_permission_views.as_view()),
    path("check_login_user/",check_login_user.as_view()),
    path("LogoutUser/",LogoutUser.as_view()),
    path("Gmailonlyjwtview/",Gmailonlyjwtview.as_view()),
    # this url to call the refresh token 
    path("auth/token/refresh/",TokenRefreshView.as_view()),
]
