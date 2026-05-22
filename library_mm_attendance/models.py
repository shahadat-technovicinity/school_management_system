from django.db import models
from apps.students.models import Student
from library_mm_book_list.models import Book_model


class LibraryAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='library_attendances')
    book = models.ForeignKey(Book_model, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_attendances')
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.student.full_name} - {self.date}"

    @property
    def is_checked_out(self):
        return self.check_out_time is not None