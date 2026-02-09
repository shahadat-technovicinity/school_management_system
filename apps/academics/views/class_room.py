
from apps.common.views.basemodelview import BaseModelViewSet
from apps.academics.models import ClassSection
from apps.academics.serializers.class_section import ClassSectionSerializer
from apps.academics.serializers.class_room import ClassSerializer

class ClassViewSet(BaseModelViewSet):
    serializer_class = ClassSerializer
