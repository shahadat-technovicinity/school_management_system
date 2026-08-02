from django.db import models
from apps.students.models import Student


class ExamMark(models.Model):
    EXAM_TYPES = [
        ('mid', 'Mid-term Examination'),
        ('final', 'Final Examination'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_marks')
    subject = models.ForeignKey(
        'academic_create_subject.Subject_Name', 
        on_delete=models.CASCADE,
        related_name="resultarchive"
    )  
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
    writing = models.IntegerField(default=0)
    practical = models.IntegerField(default=0)
    mcq = models.IntegerField(default=0)
    total = models.IntegerField(editable=False, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # টোটাল মার্ক হিসাব
        self.total = (self.writing or 0) + (self.practical or 0) + (self.mcq or 0)
        
        # নতুন ডাটা হলে বা স্ট্যাটাস না থাকলে বাই-ডিফল্ট pending থাকবে
        if not self.status:
            self.status = 'pending'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.exam_type})"