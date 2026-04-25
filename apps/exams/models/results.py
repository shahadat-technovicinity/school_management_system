from django.db import models
from apps.common.models_audit import AuditModel
from .setup import ExamSetup

class StudentResult(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        unique_together = ('exam_setup', 'student')
        ordering = ['-marks_obtained']
