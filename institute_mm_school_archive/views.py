from rest_framework import generics, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import School_Archive_Document
from .serializers import SchoolArchiveDocumentSerializer

# Dashboard-er main list ebং Modal theke document create korar jonno
class DocumentListCreateView(generics.ListCreateAPIView):
    queryset = School_Archive_Document.objects.all().order_by('-updated_at')
    serializer_class = SchoolArchiveDocumentSerializer

    def list(self, request, *args, **kwargs):
        # 1. Prothome normal queryset-ta niye asha
        queryset = self.get_queryset()

        # 2. URL-e jodi 'category' filter thake (e.g. ?category=student records)
        category_param = request.query_params.get('category', None)
        
        if category_param:
            # Jodi specific category filter kora hoy, tobe normal list pathabo
            filtered_queryset = queryset.filter(category__iexact=category_param)
            serializer = self.get_serializer(filtered_queryset, many=True)
            return Response(serializer.data)

        # 3. Jodi kono filter na thake, tobe Figma-r dashboard-er moto Grouped data pathabo
        categories = dict(School_Archive_Document.CATEGORY_CHOICES)
        grouped_data = {}

        for key, label in categories.items():
            # Protiti category-r documents filter kora
            docs = queryset.filter(category=key)
            serializer = self.get_serializer(docs, many=True)
            # Response-e category name-ke key banano
            grouped_data[label] = serializer.data

        return Response(grouped_data)

# Specific document edit ba delete korar jonno
class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = School_Archive_Document.objects.all()
    serializer_class = SchoolArchiveDocumentSerializer