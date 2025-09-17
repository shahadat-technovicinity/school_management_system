# class_routine/models.py
from django.db import models
from django.conf import settings


#####    Teacher fetch    ########
class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


########### Routine created ###########
CLASS_CHOICES = [
    ('6', 'Class 6'),
    ('7', 'Class 7'),
    ('8', 'Class 8'),
    ('9', 'Class 9'),
    ('10', 'Class 10'),
]

SECTION_CHOICES = [
    ('A', 'Section A'),
    ('B', 'Section B'),
    ('C', 'Section C'),
    ('D', 'Section D'),
]

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

    class_name = models.CharField(max_length=10, choices=CLASS_CHOICES)
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    subject = models.CharField(max_length=100)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    class_room = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ('teacher', 'day', 'start_time', 'end_time', 'class_name', 'section')

    def __str__(self):
        return f"{self.subject} - {self.class_name} {self.section}"