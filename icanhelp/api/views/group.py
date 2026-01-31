from django.contrib.auth.models import Group
from api.serializers import GroupSerializer

from rest_framework import permissions, viewsets

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

