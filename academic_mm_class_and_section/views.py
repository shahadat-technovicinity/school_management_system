from rest_framework import generics
from .models import AcademicClass, Section
from .serializers import AcademicClassSerializer, SectionSerializer

# --- Academic Class Views ---
class AcademicClassListCreateView(generics.ListCreateAPIView):
    queryset = AcademicClass.objects.all().order_by('numeric_value')
    serializer_class = AcademicClassSerializer


class AcademicClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcademicClass.objects.all()
    serializer_class = AcademicClassSerializer


# --- Section Views ---
class SectionListCreateView(generics.ListCreateAPIView):
    queryset = Section.objects.all().order_by('id')
    serializer_class = SectionSerializer


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer