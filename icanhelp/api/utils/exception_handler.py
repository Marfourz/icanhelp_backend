from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    NotAuthenticated, AuthenticationFailed, PermissionDenied,
    NotFound, ValidationError,
)
from rest_framework.response import Response
from rest_framework import status

from api.utils.errors import ErrorCode


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        return None

    # Validation errors
    if isinstance(exc, ValidationError):
        return Response(
            {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "Données invalides.",
                "errors": response.data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Auth / permission errors (isinstance pour couvrir les sous-classes)
    if isinstance(exc, NotAuthenticated):
        return Response(
            {"code": ErrorCode.AUTH_REQUIRED, "message": "Authentification requise."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, AuthenticationFailed):
        return Response(
            {"code": ErrorCode.AUTH_FAILED, "message": "Identifiants invalides."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {"code": ErrorCode.PERMISSION_DENIED, "message": "Vous n'avez pas accès à cette ressource."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, NotFound):
        return Response(
            {"code": ErrorCode.NOT_FOUND, "message": "Ressource introuvable."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Fallback basé sur le code HTTP pour ne pas perdre d'info
    http_code = response.status_code
    if http_code == 401:
        return Response({"code": ErrorCode.AUTH_REQUIRED, "message": "Authentification requise."}, status=401)
    if http_code == 403:
        return Response({"code": ErrorCode.PERMISSION_DENIED, "message": "Accès refusé."}, status=403)
    if http_code == 404:
        return Response({"code": ErrorCode.NOT_FOUND, "message": "Ressource introuvable."}, status=404)

    return Response(
        {"code": ErrorCode.INTERNAL_ERROR, "message": "Une erreur inattendue est survenue."},
        status=http_code,
    )
