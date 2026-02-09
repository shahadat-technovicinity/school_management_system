
from rest_framework.routers import DefaultRouter
from apps.academics.views.class_section import ClassSectionViewSet


router = DefaultRouter()
router.register("class-sections", ClassSectionViewSet)
router.register("sections", ClassSectionViewSet, basename="sections")
router.register("academic-years", ClassSectionViewSet, basename="academic-years")
router.register("class-rooms", ClassSectionViewSet, basename="class-rooms")

urlpatterns = router.urls
