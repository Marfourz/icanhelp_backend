"""
URL configuration for icanhelp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from api.views import *


from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import re_path
from . import consumers


from api import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'users_profil', views.UserProfilViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'competences', views.CompetenceViewSet)
router.register(r'invitations', InvitationViewSet, basename="invitation")
router.register(r'discussions', views.DiscussionViewSet, basename='discussion')
router.register(r'category', views.CategoryView, basename='category')


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]



# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/signup', SignupView.as_view(), name='signup'),
    path('user_profil/competences/<str:type>', UserCompetencesAPIView.as_view(), name='user-competences'),
    #path('invitations', InvitationViewSet.as_view(), name='invitations'),

   

]


