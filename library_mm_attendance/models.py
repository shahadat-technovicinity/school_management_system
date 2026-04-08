# from django.db import models
# from student_profile.models import StudentPersonalInfo

# # Create your models here.
# class Library_Attendance(models.Model):
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='attendances')
#     Library_student_id = models.CharField(max_length=20) # Figma-r 'Student ID' column
#     book_name = models.CharField(max_length=200, blank=True, null=True) # Figma-r 'Book' column
    
#     # Time monitoring
#     entry_time = models.DateTimeField(auto_now_add=True) # Auto-filled
#     exit_time = models.DateTimeField(blank=True, null=True) # auto-updated on save

#     def __str__(self):
#         return f"{self.student.name} - {self.entry_time}"
    
    