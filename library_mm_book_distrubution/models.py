from django.db import models
from student_profile.models import StudentPersonalInfo
from library_mm_book_list.models import Book_model

# Create your models here.
class BookDistributionModel(models.Model):
    student_id = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE)
    book_id = models.ForeignKey(Book_model, on_delete=models.CASCADE)
    issue_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return super().__str__()




### Letter Distribution Model
class LetterDistribution(models.Model):
    LETTER_TYPES = [
        ('Reminder', 'Reminder'),
        ('Fine', 'Fine'),
        ('Event', 'Event'),
    ]

    STATUS = [
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Acknowledged', 'Acknowledged'),
    ]

    letter_type = models.CharField(max_length=50, choices=LETTER_TYPES)
    recipient = models.CharField(max_length=100) 
    student_id = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='Pending') 
    date_sent = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.letter_type} - {self.subject}"