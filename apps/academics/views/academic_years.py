
from apps.common.views.basemodelview import BaseModelViewSet


from apps.academics.models import AcademicYear
from apps.academics.serializers.academic_years import AcademicYearSerializer

class AcademicYearViewSet(BaseModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer

    def get_queryset(self):
        return self.queryset.order_by('-start_date')