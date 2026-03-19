from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from api.serializers import CategorySerializer
from api.models import Category
from rest_framework.response import Response

class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'children']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Category.objects.all()
        search = self.request.query_params.get('search')
        parent_id = self.request.query_params.get('parent')

        # Filtrer par nom
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Filtrer par parent (sous-catégories)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        else:
            # Par défaut, retourner uniquement les catégories racines
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_destroy(self, instance):
        if instance.image:
            instance.image.delete(save=False)
        instance.delete()

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Récupérer les sous-catégories d'une catégorie avec recherche optionnelle."""
        category = get_object_or_404(Category, pk=pk)
        search = request.query_params.get('search')

        children = Category.objects.filter(parent=category)

        if search:
            children = children.filter(name__icontains=search)

        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)