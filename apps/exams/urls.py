from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.setup import (
    ExamSetupViewSet, ExamTypeViewSet, SubjectViewSet, 
    ExamRoutineViewSet, QuestionBankViewSet
)
from .views.logistics import (
    ExamAdmitCardViewSet, ExamSeatPlanViewSet, TeacherDutyViewSet
)
from .views.results import StudentResultViewSet

router = DefaultRouter()
# Setup
router.register(r'setup', ExamSetupViewSet)
router.register(r'types', ExamTypeViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'routines', ExamRoutineViewSet)
router.register(r'questions', QuestionBankViewSet)

# Logistics
router.register(r'admit-cards', ExamAdmitCardViewSet)
router.register(r'seat-plans', ExamSeatPlanViewSet)
router.register(r'teacher-duties', TeacherDutyViewSet)

# Results
router.register(r'results', StudentResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
