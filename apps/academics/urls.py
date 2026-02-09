
from apps.academics.views.academic_years import AcademicYearViewSet
from apps.academics.views.class_room import ClassViewSet
from apps.academics.views.sections import SectionViewSet
from rest_framework.routers import DefaultRouter
from apps.academics.views.class_section import ClassSectionViewSet


router = DefaultRouter()
router.register("class-sections", ClassSectionViewSet)
router.register("sections", SectionViewSet, basename="sections")
router.register("academic-years", AcademicYearViewSet, basename="academic-years")
router.register("class-rooms", ClassViewSet, basename="class-rooms")

urlpatterns = router.urls
