
from apps.academics.serializers.sections import SectionSerializer
from apps.common.views.basemodelview import BaseModelViewSet
from apps.academics.models import ClassSection
from apps.academics.serializers.class_section import ClassSectionSerializer

class SectionViewSet(BaseModelViewSet):
   
    serializer_class = SectionSerializer

    