from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from .models import FacilityFurnitureItem
from .serializers import FacilityFurnitureSerializer
from reg_mm_stock_event.models import StockInventory


# এ পর্যন্ত ইনপুট দেওয়া সব ইউনিক লোকেশন ড্রপডাউনের জন্য দেবে
class FacilityLocationDropdownView(APIView):
    def get(self, request):
        locations = FacilityFurnitureItem.objects.values_list('location', flat=True).distinct()
        return Response(list(locations))


# Facility Furniture / Maintenance Issue APIs
class Facility_asset(generics.ListCreateAPIView):
    queryset = FacilityFurnitureItem.objects.select_related('stock_item').all()
    serializer_class = FacilityFurnitureSerializer


class Facility_assetupdatedelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = FacilityFurnitureItem.objects.select_related('stock_item').all()
    serializer_class = FacilityFurnitureSerializer


# Dashboard Stats & Percentage View
class AssetSummaryView(APIView):
    def get(self, request):
        stock_items = StockInventory.objects.all()
        categories = set(item.category for item in stock_items)
        final_response = {}

        for cat in categories:
            cards = []
            cat_items = stock_items.filter(category=cat)

            for s_item in cat_items:
                total_qty = s_item.quantity

                affected_qty = FacilityFurnitureItem.objects.filter(
                    stock_item=s_item
                ).aggregate(
                    total_affected=Sum('quantity')
                )['total_affected'] or 0

                good_qty = max(0, total_qty - affected_qty)
                good_percent = (good_qty / total_qty * 100) if total_qty > 0 else 100.0

                cards.append({
                    "id": s_item.id,
                    "name": s_item.item_name,
                    "total_count": total_qty,
                    "good_count": good_qty,
                    "affected_count": affected_qty,
                    "status_percent": round(good_percent, 1)
                })

            final_response[cat] = cards

        return Response(final_response)