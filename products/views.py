from django.utils.text import slugify
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, JSONParser
import json

from categories.models import Category
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, JSONParser]

    def list(self, request):
        category = request.query_params.get('category')
        search = request.query_params.get('search')

        products = Product.objects.all()

        if category:
            products = products.filter(category__slug=category)
        if search:
            products = products.filter(name__icontains=search)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create(self, request):
        # Check for file upload
        if 'file' in request.FILES:
            file = request.FILES['file']
            data = json.load(file)
        else:
            data = request.data

        # Now handle as before
        if isinstance(data, list):
            products = []
            for product in data:
                category, created = Category.objects.get_or_create(
                    name=product.get('category'),
                    slug=slugify(product.get('category'))
                )
                product['category'] = category.id
                products.append(product)
            serializer = ProductSerializer(data=products, many=True)
        else:
            serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message':'Deleted Successfully'},status=status.HTTP_204_NO_CONTENT)