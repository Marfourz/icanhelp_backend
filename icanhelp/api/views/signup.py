from api.serializers import CreateUserSerializer
from api.mixins import UserProfilMixin
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from api.utils.errors import ErrorCode, api_error, validation_error
from allauth.account.models import EmailAddress


class SignupView(UserProfilMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        if "password" not in request.data:
            return api_error(ErrorCode.PASSWORD_REQUIRED, "Le mot de passe est obligatoire.")

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            if 'email' in errors:
                return api_error(ErrorCode.EMAIL_ALREADY_EXISTS, "Un compte avec cet email existe déjà.")
            if 'username' in errors:
                return api_error(ErrorCode.USERNAME_ALREADY_EXISTS, "Ce nom d'utilisateur est déjà pris.")
            return validation_error(errors)

        user = serializer.save(password=make_password(request.data["password"]))

        # Enregistrer la localisation dans le UserProfil (créé automatiquement par le signal)
        profil = user.profil.first()
        if profil:
            for field in ('city', 'adress', 'location_lat', 'location_lon'):
                value = request.data.get(field)
                if value not in (None, ''):
                    setattr(profil, field, value)
            profil.save(update_fields=['city', 'adress', 'location_lat', 'location_lon'])

        # Envoyer le mail de vérification d'email
        email_address, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={'primary': True, 'verified': False},
        )
        email_address.send_confirmation(request._request, signup=True)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Inscription réussie ! Un email de confirmation vous a été envoyé.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_201_CREATED)
