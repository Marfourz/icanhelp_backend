from rest_framework.response import Response
from rest_framework import status as http_status


# ─── Codes d'erreur ───────────────────────────────────────────────────────────

class ErrorCode:
    # Auth
    AUTH_REQUIRED       = "AUTH_REQUIRED"
    PERMISSION_DENIED   = "PERMISSION_DENIED"
    AUTH_FAILED         = "AUTH_FAILED"
    TOKEN_INVALID       = "TOKEN_INVALID"

    # Validation générique
    VALIDATION_ERROR    = "VALIDATION_ERROR"
    NOT_FOUND           = "NOT_FOUND"
    INTERNAL_ERROR      = "INTERNAL_ERROR"

    # Utilisateur
    USER_NOT_FOUND          = "USER_NOT_FOUND"
    EMAIL_ALREADY_EXISTS    = "EMAIL_ALREADY_EXISTS"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    PASSWORD_REQUIRED       = "PASSWORD_REQUIRED"

    # Compétence
    COMPETENCE_REQUIRED  = "COMPETENCE_REQUIRED"
    COMPETENCE_NOT_FOUND = "COMPETENCE_NOT_FOUND"
    COMPETENCE_NOT_OWNED = "COMPETENCE_NOT_OWNED"
    COMPETENCE_TYPE_INVALID = "COMPETENCE_TYPE_INVALID"

    # Invitation
    RECEIVER_REQUIRED           = "RECEIVER_REQUIRED"
    INVITATION_SELF             = "INVITATION_SELF"
    INVITATION_NOT_FOUND        = "INVITATION_NOT_FOUND"
    INVITATION_ALREADY_PROCESSED = "INVITATION_ALREADY_PROCESSED"
    INVITATION_NOT_ACCEPTED     = "INVITATION_NOT_ACCEPTED"
    INVITATION_NOT_SCHEDULED    = "INVITATION_NOT_SCHEDULED"
    INVITATION_NO_PENDING_SCHEDULE = "INVITATION_NO_PENDING_SCHEDULE"
    INSUFFICIENT_POINTS         = "INSUFFICIENT_POINTS"
    SCHEDULE_DATE_REQUIRED      = "SCHEDULE_DATE_REQUIRED"
    SCHEDULE_SELF_CONFIRM       = "SCHEDULE_SELF_CONFIRM"

    # Discussion / Message
    DISCUSSION_NOT_FOUND = "DISCUSSION_NOT_FOUND"
    MESSAGE_REQUIRED     = "MESSAGE_REQUIRED"


# ─── Helper ───────────────────────────────────────────────────────────────────

def api_error(code: str, message: str, status: int = http_status.HTTP_400_BAD_REQUEST, **extra):
    """
    Retourne une Response avec le format standard :
        {"code": "...", "message": "..."}
    """
    body = {"code": code, "message": message}
    body.update(extra)
    return Response(body, status=status)


def validation_error(serializer_errors):
    """
    Retourne une Response 400 pour les erreurs de serializer,
    avec la liste des champs invalides.
    """
    return Response(
        {
            "code": ErrorCode.VALIDATION_ERROR,
            "message": "Données invalides.",
            "errors": serializer_errors,
        },
        status=http_status.HTTP_400_BAD_REQUEST,
    )
