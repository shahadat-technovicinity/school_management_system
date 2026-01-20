from django.db import models

class ExamRoutine(models.Model):
    EXAM_TYPE_CHOICES = [
        ('MT', 'Mid-Term'),
        ('FN', 'Final'),
        ('OT', 'Other'),
    ]

    CLASS_CHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),
    ]

    SHIFT_CHOICES = [
        ('morning', 'Morning'),
        ('day', 'Day'),
    ]

    STREAM_CHOICES = [
        ('SC', 'Science'),
        ('AR', 'Arts'),
        ('CM', 'Commerce'),
        ('VT', 'Vocational'),

    ]

    # Routine Details
    routine_title = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=2, choices=EXAM_TYPE_CHOICES)
    academic_year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    class_selection = models.CharField(max_length=20, choices=CLASS_CHOICES)
    shift_selection = models.CharField(max_length=50, choices=SHIFT_CHOICES) # Assuming text input/dropdown
    stream = models.CharField(max_length=2, choices=STREAM_CHOICES, default='SC')

    def __str__(self):
        return f"{self.routine_title} ({self.academic_year})"

    # Routine Table Builder Fields

    DAY_CHOICES= [
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('fridaday', 'Friday'),

    ]
    date = models.DateField()
    day = models.CharField(max_length=10, choices=DAY_CHOICES) # Auto-calculated or manually entered
    time_slot = models.CharField(max_length=50) # e.g., "10:00 AM - 1:00 PM"
    subject = models.CharField(max_length=100)
    exam_hall = models.CharField(max_length=50)

    class Meta:
        ordering = ['date'] # Order slots by date

    def __str__(self):
        return f"{self.routine_title} - {self.subject} on {self.date}"
    



class ExamAdmit(models.Model):
    CLASS_CHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('non paid', 'Non Paid'),
    ]

    EXAM_TYPE_CHOICES = [
        ('MT', 'Mid-Term'),
        ('FN', 'Final'),
        ('OT', 'Other'),
    ]
    student_name = models.CharField(max_length=250)
    roll_number = models.IntegerField()
    class_selection = models.CharField(max_length=20, choices=CLASS_CHOICES)
    subject = models.CharField(max_length=250)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    exam_type = models.CharField(max_length=2, choices=EXAM_TYPE_CHOICES)

    def __str__(self):
        return self.student_name