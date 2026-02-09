
from apps.common.views.basemodelview import BaseModelViewSet
from apps.academics.models import ClassSection
from apps.academics.serializers.class_section import ClassSectionSerializer

class SectionViewSet(BaseModelViewSet):
    queryset = ClassSection.objects.select_related(
        'class_room', 'section', 'academic_year'
    )
    serializer_class = ClassSectionSerializer

    def get_queryset(self):
        return self.queryset.order_by('class_room__name', 'section__name')