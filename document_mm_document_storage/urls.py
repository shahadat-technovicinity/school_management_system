from django.urls import path
from .views import (
    CabinetListView,
    CabinetDetailView,
    ShelfListView,
    DocumentListView,
    DocumentCreateView,
    DocumentDetailView,
    DocumentUpdateView,
    DocumentDeleteView,
    DocumentLocationUpdateView,
    DocumentHistoryView,
)

urlpatterns = [
    # ── Cabinet ──────────────────────────────────────
    path('api/cabinets/',      CabinetListView.as_view(),   name='cabinet-list'),
    path('api/cabinets/<int:pk>/', CabinetDetailView.as_view(), name='cabinet-detail'),

    # ── Shelf ─────────────────────────────────────────
    # GET /api/shelves/?cabinet=2
    path('api/shelves/',       ShelfListView.as_view(),     name='shelf-list'),

    # ── Document ──────────────────────────────────────
    path('api/documents/',                              DocumentListView.as_view(),           name='document-list'),
    path('api/documents/create/',                       DocumentCreateView.as_view(),         name='document-create'),
    path('api/documents/<uuid:pk>/',                    DocumentDetailView.as_view(),         name='document-detail'),
    path('api/documents/<uuid:pk>/update/',             DocumentUpdateView.as_view(),         name='document-update'),
    path('api/documents/<uuid:pk>/delete/',             DocumentDeleteView.as_view(),         name='document-delete'),
    path('api/documents/<uuid:pk>/location/',           DocumentLocationUpdateView.as_view(), name='document-location'),
    path('api/documents/<uuid:pk>/history/',            DocumentHistoryView.as_view(),        name='document-history'),
]