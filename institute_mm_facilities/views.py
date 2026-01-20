from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from django.db.models import Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FacilityFurnitureItem

# Create your views here.
class Facility_asset(generics.ListCreateAPIView):
    queryset = FacilityFurnitureItem.objects.all()
    serializer_class = FacilityFurnitureSerializer


class Facility_assetupdatedelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = FacilityFurnitureItem.objects.all()
    serializer_class = FacilityFurnitureSerializer




### item dashboard summary view ###
class AssetSummaryView(APIView):
    def get(self, request):
        # ১. ডাটাবেসে যতগুলো ইউনিক item_type আছে সবগুলোকে বের করা
        all_types = FacilityFurnitureItem.objects.values_list('item_type', flat=True).distinct()
        
        final_response = {}

        # ২. প্রত্যেকটা টাইপের জন্য লুপ চালিয়ে ডাটা গোছানো
        for t in all_types:
            # ওই নির্দিষ্ট টাইপের (যেমন: furniture) আইটেমগুলো ফিল্টার করা
            queryset = FacilityFurnitureItem.objects.filter(item_type=t)
            
            # আইটেমের নাম অনুযায়ী গ্রুপিং (Bench, Chair ইত্যাদি)
            summary_query = queryset.values('item_name').annotate(
                total_qty=Sum('quantity'),
                good_qty=Sum('quantity', filter=Q(condition_status='good'))
            )

            cards = []
            for item in summary_query:
                total = item['total_qty'] or 0
                good = item['good_qty'] or 0
                percent = (good / total * 100) if total > 0 else 0
                
                cards.append({
                    "name": item['item_name'],
                    "count": total,
                    "status_percent": round(percent, 1)
                })
            
            # ৩. মেইন রেসপন্স অবজেক্টে ঐ টাইপের আন্ডারে কার্ডগুলো রাখা
            final_response[t] = cards

        return Response(final_response)