import logging
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, JSONParser
import json
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related('category')
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        if category:
            queryset = queryset.filter(category__name=category)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, JSONParser]

    def create(self, request, *args, **kwargs):
        # Check for file upload
        if 'file' in request.FILES:
            file = request.FILES['file']
            data = json.load(file)
        else:
            data = request.data

        # Handle bulk creation (list of products)
        if isinstance(data, list):
            serializer = self.get_serializer(data=data, many=True)
        else:
            serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProductUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

class ProductDeleteAPIView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
