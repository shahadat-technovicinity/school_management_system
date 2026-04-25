from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.core import (
    ExamSetupViewSet, ExamTypeViewSet, SubjectViewSet, 
    ExamRoutineViewSet, TeacherDutyViewSet, StudentResultViewSet
)

router = DefaultRouter()
router.register(r'setup', ExamSetupViewSet)
router.register(r'types', ExamTypeViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'routines', ExamRoutineViewSet)
router.register(r'teacher-duties', TeacherDutyViewSet)
router.register(r'results', StudentResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
