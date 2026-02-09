from apps.academics.models import ClassSection
from apps.academics.serializers.class_section import ClassSectionSerializer
from apps.common.views.basemodelview import BaseModelViewSet

class ClassSectionViewSet(BaseModelViewSet):
    queryset = ClassSection.objects.select_related(
        'class_room', 'section', 'academic_year'
    )
    serializer_class = ClassSectionSerializer
