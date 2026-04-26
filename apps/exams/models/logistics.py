from django.db import models
from apps.common.models_audit import AuditModel
from apps.exams.models.setup import ExamSetup

class ExamAdmitCard(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    enrollment_number = models.CharField(max_length=50, blank=True, null=True)
    is_generated = models.BooleanField(default=False)
    generated_at = models.DateTimeField(null=True, blank=True)

class ExamSeatPlan(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50)
    seat_number = models.CharField(max_length=20)

    class Meta:
        unique_together = ('exam_setup', 'student')

class TeacherDuty(AuditModel):
    exam_setup = models.ForeignKey(ExamSetup, on_delete=models.CASCADE)
    teacher = models.ForeignKey('staff.StaffProfile', on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    room_number = models.CharField(max_length=50)
    duty_start_time = models.TimeField()
    duty_end_time = models.TimeField()
