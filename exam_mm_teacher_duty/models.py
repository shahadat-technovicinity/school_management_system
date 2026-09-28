from django.db import models
from teacher_mm_teacher.models import TeacherAndStaffProfile  # Apnar teacher model-er shothik app path din

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Conflict', 'Conflict'),
]


class ExamDuty(models.Model):
    # TeacherAndStaffProfile model-er shathe direct ForeignKey relation
    teacher = models.ForeignKey(
        TeacherAndStaffProfile,
        on_delete=models.CASCADE,
        related_name='exam_duties',
        limit_choices_to={'employee_type__in': ['head_teacher', 'teacher']}  # Shudhu teacher-der show korar jonne
    )
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    send_notification = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.teacher} - Room: {self.room_number} ({self.exam_date})"