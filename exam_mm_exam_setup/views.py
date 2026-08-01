from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import exm_mm_exam_setup
from .serializers import ExamSerializer

# কাস্টম পেজিনেশন ক্লাস (ঐচ্ছিক, সাইজ কাস্টমাইজ করার জন্য)
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size' # ফ্রন্টএন্ড থেকে ?page_size=20 পাঠালে সাইজ চেঞ্জ হবে
    max_page_size = 100

class ExamSetupViewSet(viewsets.ModelViewSet):
    queryset = exm_mm_exam_setup.objects.all()
    serializer_class = ExamSerializer
    pagination_class = StandardResultsSetPagination # পেজিনেশন যুক্ত করা হলো