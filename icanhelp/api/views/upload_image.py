from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


class ImageUploadApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = None  # à définir dans la sous-classe
    image_field = 'image'   # nom du champ image, à surcharger si besoin

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

    def delete(self, request, **kwargs):
        instance = self.get_instance(request, **kwargs)
        field = getattr(instance, self.image_field)
        if field and field.name:
            field.storage.delete(field.name)
            setattr(instance, self.image_field, None)
            instance.save(update_fields=[self.image_field])
        return Response(status=204)