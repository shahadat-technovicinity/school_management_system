from django.db.models import ProtectedError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FeeHead
from .serializers import FeeHeadSerializer


class FeeHeadListCreateView(generics.ListCreateAPIView):
    serializer_class = FeeHeadSerializer
    pagination_class = None

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('parent', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description="parent এর id। সর্বোচ্চ স্তর দেখতে 'null' দাও"),
        openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FeeHead.objects.none()
        qs = FeeHead.objects.select_related('parent')
        parent = self.request.query_params.get('parent')
        is_active = self.request.query_params.get('is_active')
        if parent is not None:
            qs = qs.filter(parent__isnull=True) if parent == 'null' else qs.filter(parent_id=parent)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ('1', 'true', 'yes'))
        return qs


class FeeHeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeeHead.objects.select_related('parent')
    serializer_class = FeeHeadSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'error': "এর নিচে sub fee আছে। আগে সেগুলো মুছো বা সরাও।"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeeHeadTreeView(APIView):
    """পুরো fee tree, প্রতিটা স্তরের মোট টাকা সহ।"""

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
                          description="true দিলে শুধু active fee আসে"),
    ])
    def get(self, request):
        qs = FeeHead.objects.all()
        only_active = request.query_params.get('is_active', '').lower() in ('1', 'true', 'yes')
        if only_active:
            qs = qs.filter(is_active=True)

        nodes = {}
        for h in qs:
            nodes[h.id] = {
                'id': h.id,
                'name': h.name,
                'description': h.description,
                'order': h.order,
                'is_active': h.is_active,
                'children': [],
                '_parent': h.parent_id,
            }

        roots = []
        for node in nodes.values():
            parent_id = node.pop('_parent')
            if parent_id and parent_id in nodes:
                nodes[parent_id]['children'].append(node)
            elif parent_id is None:
                roots.append(node)
        return Response(roots, status=status.HTTP_200_OK)