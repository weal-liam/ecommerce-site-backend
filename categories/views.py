import logging
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status, generics

from .models import Category
from .serializers import CategorySerializer

class CategoryListCreateAPIView(generics.ListCreateAPIView):
    logger = logging.getLogger(__name__)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        queryset = super().get_queryset()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
        

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

