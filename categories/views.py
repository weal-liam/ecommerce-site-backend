from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        search = request.query_params.get('search')

        categories = Category.objects.all()

        if search:
            categories = categories.filter(name__icontains=search)

        serializer = CategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'category not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'},status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'},status=status.HTTP_404_NOT_FOUND)

        return Response({'message':'Deleted Successfully'},status=status.HTTP_204_NO_CONTENT)
