from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


class ImageUploadApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = None  # à définir dans la sous-classe

    def get_instance(self, request, **kwargs):
        raise NotImplementedError

    def patch(self, request, **kwargs):
        instance = self.get_instance(request, **kwargs)
        serializer = self.serializer_class(
            instance=instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)