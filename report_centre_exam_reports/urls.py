from django.urls import path
from .views import (
    # StudentAgeDistributionReportView,
    # AttendanceReportView,
    ExamReportView,
    ClassPerformanceReportView,
    SubjectPerformanceReportView,
    IndividualStudentReportView,
)

urlpatterns = [
    # path('reports/student-age-distribution/', StudentAgeDistributionReportView.as_view(), name='student-age-distribution'),
    # path('reports/attendance/', AttendanceReportView.as_view(), name='attendance-report'),
    path('reports/exam/', ExamReportView.as_view(), name='exam-report'),
    path('reports/exam/class-performance/', ClassPerformanceReportView.as_view(), name='class-performance'),
    path('reports/exam/subject-performance/', SubjectPerformanceReportView.as_view(), name='subject-performance'),
    path('reports/exam/individual-student/', IndividualStudentReportView.as_view(), name='individual-student'),
]