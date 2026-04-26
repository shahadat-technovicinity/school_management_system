from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Cabinet, Shelf, Document, LocationMoveLog
from .serializers import (
    CabinetSerializer,
    ShelfSerializer,
    DocumentListSerializer,
    DocumentCreateSerializer,
    DocumentUpdateLocationSerializer,
    LocationMoveLogSerializer,
)
from .filters import DocumentFilter


# ─────────────────────────────────────────────
# Cabinet
# ─────────────────────────────────────────────

class CabinetListView(generics.ListAPIView):
    """
    GET /api/cabinets/
    Figma-র 'Cabinet Selection' dropdown এর জন্য।
    """
    queryset         = Cabinet.objects.prefetch_related('shelves')
    serializer_class = CabinetSerializer


class CabinetDetailView(generics.RetrieveAPIView):
    """
    GET /api/cabinets/<id>/
    একটা cabinet-এর detail, shelves সহ।
    """
    queryset         = Cabinet.objects.prefetch_related('shelves')
    serializer_class = CabinetSerializer


# ─────────────────────────────────────────────
# Shelf
# ─────────────────────────────────────────────

class ShelfListView(generics.ListAPIView):
    """
    GET /api/shelves/
    GET /api/shelves/?cabinet=2   ← cabinet select করলে filter হবে
    """
    serializer_class = ShelfSerializer

    def get_queryset(self):
        qs         = Shelf.objects.select_related('cabinet')
        cabinet_id = self.request.query_params.get('cabinet')
        if cabinet_id:
            qs = qs.filter(cabinet__id=cabinet_id)
        return qs


# ─────────────────────────────────────────────
# Document — List & Create
# ─────────────────────────────────────────────

class DocumentListView(generics.ListAPIView):
    """
    GET /api/documents/
    Figma Screen 1 — সব filter, search, pagination এখানে।

    Query params:
      ?cabinet=2&shelf=4&status=available
      ?search=Q1
      ?days=30
      ?ordering=-updated_at
      ?page=2
    """
    queryset         = Document.objects.select_related('cabinet', 'shelf')
    serializer_class = DocumentListSerializer
    filter_backends  = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class  = DocumentFilter
    search_fields    = ['name', 'tag_number', 'document_type']
    ordering_fields  = ['name', 'updated_at', 'created_at', 'status']


class DocumentCreateView(generics.CreateAPIView):
    """
    POST /api/documents/
    Figma Screen 2 — 'Add New Storage' modal।
    Cabinet + shelf + location সব একসাথে পাঠাও,
    server একটাই transaction-এ save করবে।
    """
    serializer_class = DocumentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        # Response-এ full document data দেখাও (cabinet name সহ)
        return Response(
            DocumentListSerializer(document).data,
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────
# Document — Detail, Update, Delete
# ─────────────────────────────────────────────

class DocumentDetailView(generics.RetrieveAPIView):
    """
    GET /api/documents/<id>/
    একটা document-এর full detail।
    """
    queryset         = Document.objects.select_related('cabinet', 'shelf')
    serializer_class = DocumentListSerializer


class DocumentUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/documents/<id>/
    সাধারণ field update — name, type, status ইত্যাদি।
    Location change করতে হলে আলাদা /location/ endpoint ব্যবহার করো।
    """
    queryset          = Document.objects.select_related('cabinet', 'shelf')
    serializer_class  = DocumentListSerializer
    http_method_names = ['patch']  # PUT বন্ধ, শুধু PATCH


class DocumentDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/documents/<id>/
    """
    queryset = Document.objects.all()


# ─────────────────────────────────────────────
# Document — Location Update
# ─────────────────────────────────────────────

class DocumentLocationUpdateView(APIView):
    """
    PATCH /api/documents/<id>/location/
    Figma Screen 3 — 'Update Document Location' modal।

    Body:
      cabinet, shelf, tag_number, reason_for_move, notes

    কাজ:
      1. পুরোনো location note করে
      2. নতুন location save করে
      3. LocationMoveLog-এ history রাখে
      সব একটা transaction-এ।
    """

    def get_object(self, pk):
        try:
            return Document.objects.select_related('cabinet', 'shelf').get(pk=pk)
        except Document.DoesNotExist:
            raise NotFound(detail='Document পাওয়া যায়নি।')

    def patch(self, request, pk):
        document   = self.get_object(pk)
        serializer = DocumentUpdateLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_doc = serializer.update(document, serializer.validated_data)
        return Response(
            DocumentListSerializer(updated_doc).data,
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────
# Document — Move History
# ─────────────────────────────────────────────

class DocumentHistoryView(generics.ListAPIView):
    """
    GET /api/documents/<id>/history/
    একটা document কতবার কোথায় সরানো হয়েছে তার পুরো ইতিহাস।
    """
    serializer_class = LocationMoveLogSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return LocationMoveLog.objects.none()
        pk = self.kwargs.get('pk')
        if pk is None:
            return LocationMoveLog.objects.none()
        if not Document.objects.filter(pk=pk).exists():
            raise NotFound(detail='Document পাওয়া যায়নি।')
        return LocationMoveLog.objects.filter(document__pk=pk)