from api.models import UserProfil
from api.serializers import MyProfilSerializer, UserProfilSerializer, UserSerializer,AvatarSerializer
from django.contrib.auth.models import User
from api.mixins import UserProfilMixin

from api.views.upload_image import ImageUploadApiView
from rest_framework import permissions, viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import mixins


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserProfilViewSet(
    UserProfilMixin, 
    viewsets.GenericViewSet,
    mixins.ListModelMixin
):
    queryset = UserProfil.objects.all()
    serializer_class = UserProfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='my_profil')
    def my_profil(self, request):
        user_profile = self.get_user_profil()
        serializer = MyProfilSerializer(user_profile, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False,methods=['patch'], url_path='my_profil')
    def patch(self, request):
        user_profile = self.get_user_profil()
        serializer = UserProfilSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangeAvatarApiView(ImageUploadApiView, UserProfilMixin):
    serializer_class = AvatarSerializer

    def get_instance(self, request, **kwargs):
        return self.get_user_profil()