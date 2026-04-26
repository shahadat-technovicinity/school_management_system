
from apps.academics.serializers.sections import SectionSerializer
from apps.common.views.basemodelview import BaseModelViewSet
from apps.academics.models import ClassSection, Section
from apps.academics.serializers.class_section import ClassSectionSerializer

class SectionViewSet(BaseModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    