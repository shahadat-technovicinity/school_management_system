from apps.common.pagination.standard_pagination import StandardPagination
from apps.enrollments.serializers.enrollments import EnrollmentSerializer
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from apps.enrollments.models import Enrollment







class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Enrollment.
    Supports filtering, search and ordering via query params.
    Example query params:
      ?student=1
      ?course=2
      ?search=john
      ?ordering=-created_at
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'course', 'status', 'term']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'end_date']

    def get_queryset(self):
        # allow limiting to current user's school if Enrollment has that relation
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            # attempt common patterns: school relation on enrollment or student
            if hasattr(qs.model, "school"):
                qs = qs.filter(school=getattr(user, "school", None))
            elif hasattr(qs.model, "student") and hasattr(user, "school"):
                qs = qs.filter(student__school=getattr(user, "school", None))
        return qs