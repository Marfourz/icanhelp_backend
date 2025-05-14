from api.serializers import UserSerializer, CreateUserSerializer
from api.mixins import UserProfilMixin
from api.models import UserProfil
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password



# Vue API pour l'inscription avec JWT
class SignupView(UserProfilMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        userData = request.data

        # Vérifier si le mot de passe est présent
        if "password" not in userData:
            return Response({"error": "Le mot de passe est requis."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=userData)
        if serializer.is_valid():
            user = serializer.save(password=make_password(userData["password"]))

          

            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            return Response({ 
                "message": "Inscription réussie !",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

