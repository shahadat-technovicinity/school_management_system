from rest_framework import generics
from .models import Nothi
from .serializers import NothiListSerializer

class NothiListView(generics.ListAPIView):
    """
    GET /api/nothi/
    সকল নথির লিস্ট দেখার জন্য
    """
    queryset = Nothi.objects.all().order_by('-created_at')
    serializer_class = NothiListSerializer


class NothiDetailView(generics.RetrieveAPIView):
    """
    GET /api/nothi/<int:pk>/
    নির্দিষ্ট নথির আইডি দিয়ে ফাইল ডিটেইলস দেখার জন্য
    """
    queryset = Nothi.objects.all()
    serializer_class = NothiListSerializer