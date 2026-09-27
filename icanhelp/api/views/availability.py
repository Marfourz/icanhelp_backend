from api.models.Availability import Availability
from api.serializers import AvailabilitySerializer
from api.mixins import UserProfilMixin
from api.utils.errors import ErrorCode, api_error

from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class AvailabilityViewSet(UserProfilMixin, viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Availability.objects.filter(user__id=user_id)
        return Availability.objects.filter(user=self.get_user_profil())

    def create(self, request, *args, **kwargs):
        user_profil = self.get_user_profil()
        from api.utils.errors import validation_error

        raw = request.data if isinstance(request.data, list) else [request.data]

        # Expand dayOfWeek lists into individual items
        expanded = []
        for item in raw:
            days = item.get('dayOfWeek')
            if isinstance(days, list):
                for day in days:
                    expanded.append({**item, 'dayOfWeek': day})
            else:
                expanded.append(item)

        serializer = AvailabilitySerializer(data=expanded, many=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        from django.db import transaction
        instances = []
        with transaction.atomic():
            for item in serializer.validated_data:
                new_start = item['startTime']
                new_end   = item['endTime']
                day       = item['dayOfWeek']

                existing = Availability.objects.filter(user=user_profil, dayOfWeek=day)

                # Créneau identique → ignorer
                if existing.filter(startTime=new_start, endTime=new_end).exists():
                    continue

                # Supprimer les créneaux plus petits que le nouveau (englobés)
                existing.filter(startTime__gte=new_start, endTime__lte=new_end).delete()

                # Si le nouveau est lui-même englobé par un créneau existant → ignorer
                if existing.filter(startTime__lte=new_start, endTime__gte=new_end).exists():
                    continue

                instances.append(Availability.objects.create(**item, user=user_profil))

        return Response(AvailabilitySerializer(instances, many=True).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.get_user_profil():
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé.", status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.get_user_profil():
            return api_error(ErrorCode.PERMISSION_DENIED, "Vous n'êtes pas autorisé.", status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
