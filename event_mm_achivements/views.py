from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *

# ১. Achievement List (Cards) ebong Create API
class AchievementListCreateView(generics.ListCreateAPIView):
    queryset = Event_mm_Achievement.objects.all().order_by('-date_achieved')
    serializer_class = AchievementSerializer
    
    # Figma-te filtering ar search ache
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_published']
    search_fields = ['title', 'description']

# ২. Upore thaka 4-ti Statistics Card-er data
class AchievementStatsView(APIView):
    def get(self, request):
        data = {
            "total_achievements": Event_mm_Achievement.objects.count(),
            "academic": Event_mm_Achievement.objects.filter(category="Academic").count(),
            "sports": Event_mm_Achievement.objects.filter(category="Sports").count(),
            "arts_culture": Event_mm_Achievement.objects.filter(category="Arts & Culture").count(),
        }
        return Response(data)

# ৩. Edit ba Delete korar jonno (Card-er Edit/Delete icon)
class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event_mm_Achievement.objects.all()
    serializer_class = AchievementSerializer