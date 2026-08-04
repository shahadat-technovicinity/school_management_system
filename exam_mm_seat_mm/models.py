from django.db import models
from apps.students.models import Student


CLASS_CHOICES = (
    ('Class 6', 'Class 6'),
    ('Class 7', 'Class 7'),
    ('Class 8', 'Class 8'),
    ('Class 9', 'Class 9'),
    ('Class 10', 'Class 10'),
)

SECTION_CHOICES = (
    ('Section A', 'Section A'),
    ('Section B', 'Section B'),
    ('Section C', 'Section C'),
    ('Section D', 'Section D'),
)

SHIFT_CHOICES = [
    ('Morning', 'Morning Shift'),
    ('Day', 'Day Shift'),
]


class ExamRoom(models.Model):
    room_number = models.CharField(max_length=50, unique=True)
    number_of_benches = models.PositiveIntegerField(default=0)
    students_per_bench = models.PositiveIntegerField(default=2)
    is_available = models.BooleanField(default=True)

    @property
    def capacity(self):
        return self.number_of_benches * self.students_per_bench

    def __str__(self):
        return self.room_number


class ExamSession(models.Model):
    """একটা নির্দিষ্ট পরীক্ষার সেশন - যেমন 'May 14 2025, Morning Shift'"""
    name = models.CharField(max_length=100)
    date = models.DateField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.date} ({self.shift})"


class RoomClassAssignment(models.Model):
    """কোন Room-এ কোন Class-এর কতজন Student বসবে, কোন Subject"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='room_assignments')
    room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, related_name='class_assignments')
    class_name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    subject = models.CharField(max_length=100)

    class Meta:
        unique_together = ('exam_session', 'room', 'class_name', 'section')

    def __str__(self):
        return f"{self.room} - {self.class_name} {self.section}"


class SeatAssignment(models.Model):
    """প্রতিটা Student-এর জন্য নির্দিষ্ট Seat"""
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='seat_assignments')
    room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, related_name='seat_assignments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_seats')
    bench_number = models.PositiveIntegerField()
    seat_label = models.CharField(max_length=20)   # e.g. "10A-01"

    class Meta:
        unique_together = ('exam_session', 'room', 'bench_number', 'student')

    def __str__(self):
        return f"{self.student.full_name} - {self.seat_label}"