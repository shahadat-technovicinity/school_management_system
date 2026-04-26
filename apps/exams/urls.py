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
router.register(r'setup', ExamSetupViewSet, basename='exam-setup')
router.register(r'types', ExamTypeViewSet, basename='exam-type')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'routines', ExamRoutineViewSet, basename='routines')
router.register(r'questions', QuestionBankViewSet, basename='questions')

# Logistics
router.register(r'admit-cards', ExamAdmitCardViewSet, basename='admit-cards')
router.register(r'seat-plans', ExamSeatPlanViewSet, basename='seat-plans')
router.register(r'teacher-duties', TeacherDutyViewSet, basename='teacher-duties')

# Results
router.register(r'results', StudentResultViewSet, basename='results')

urlpatterns = [
    path('', include(router.urls)),
]
