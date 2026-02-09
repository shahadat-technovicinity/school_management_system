
from rest_framework.routers import DefaultRouter
from apps.academics.views.class_section import ClassSectionViewSet


router = DefaultRouter()
router.register("class-sections", ClassSectionViewSet)

urlpatterns = router.urls
