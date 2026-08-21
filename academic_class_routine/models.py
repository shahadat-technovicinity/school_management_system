# class_routine/models.py
from django.db import models
from django.conf import settings
from academic_create_subject.models import Subject_Name
from academic_mm_class_and_section.models import AcademicClass, Section


#####    Teacher fetch    ########
class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


DAY_CHOICES = [
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
]

class ClassRoutine(models.Model):
    # Teacher: authenticated teacher data fetch
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    class_name = models.ForeignKey(AcademicClass, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject_Name, on_delete=models.PROTECT)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    class_room = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ('teacher', 'day', 'start_time', 'end_time', 'class_name', 'section')

    def __str__(self):
        return f"{self.subject} - {self.class_name} {self.section}"