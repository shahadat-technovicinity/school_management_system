# # 1. student_mm_attendance/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class StudentAttendance(models.Model):
#     STATUS_CHOICES = [
#         ('present', 'Present'),
#         ('absent', 'Absent'),
#         ('late', 'Late'),
#         ('leave', 'Leave'),
#     ]
    
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='attendance_records')
#     date = models.DateField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     remarks = models.TextField(blank=True, null=True)
#     recorded_by = models.CharField(max_length=100, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ('student', 'date')
#         ordering = ['-date']
#         indexes = [
#             models.Index(fields=['student', 'date']),
#         ]
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.date} ({self.status})"


# # 2. student_mm_performance/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class StudentPerformance(models.Model):
#     SUBJECT_CHOICES = [
#         ('bangla', 'Bangla'),
#         ('english', 'English'),
#         ('mathematics', 'Mathematics'),
#         ('science', 'Science'),
#         ('social_studies', 'Social Studies'),
#         ('ict', 'ICT'),
#     ]
    
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='performance_records')
#     subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
#     exam_type = models.CharField(max_length=50)  # e.g., "First Term", "Mid Term", "Final"
#     marks_obtained = models.FloatField()
#     total_marks = models.FloatField(default=100)
#     grade = models.CharField(max_length=2, blank=True)  # e.g., "A+", "A", "B"
#     percentage = models.FloatField(blank=True, null=True)
#     academic_year = models.CharField(max_length=32)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-academic_year', '-created_at']
#         indexes = [
#             models.Index(fields=['student', 'academic_year']),
#         ]
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.subject} ({self.exam_type})"


# # 3. student_mm_behaviour/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class StudentBehaviour(models.Model):
#     INCIDENT_TYPE_CHOICES = [
#         ('minor_violation', 'Minor Violation'),
#         ('major_violation', 'Major Violation'),
#         ('commendation', 'Commendation'),
#         ('warning', 'Warning'),
#         ('suspension', 'Suspension'),
#     ]
    
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='behaviour_records')
#     incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPE_CHOICES)
#     description = models.TextField()
#     date_of_incident = models.DateField()
#     action_taken = models.TextField(blank=True, null=True)
#     reported_by = models.CharField(max_length=100)
#     status = models.CharField(max_length=50, default='reported')  # reported, resolved, pending
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-date_of_incident']
#         indexes = [
#             models.Index(fields=['student', 'date_of_incident']),
#         ]
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.incident_type}"


# # 4. student_mm_health/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class StudentHealthRecord(models.Model):
#     HEALTH_STATUS_CHOICES = [
#         ('good', 'Good'),
#         ('fair', 'Fair'),
#         ('poor', 'Poor'),
#     ]
    
#     student = models.OneToOneField(StudentPersonalInfo, on_delete=models.CASCADE, related_name='health_record')
#     blood_group = models.CharField(max_length=5)
#     allergies = models.TextField(blank=True, null=True)
#     chronic_disease = models.TextField(blank=True, null=True)
#     medication = models.TextField(blank=True, null=True)
#     emergency_contact = models.CharField(max_length=20)
#     emergency_contact_name = models.CharField(max_length=100)
#     health_status = models.CharField(max_length=20, choices=HEALTH_STATUS_CHOICES, default='good')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.student.full_name} - Health Record"


# class HealthCheckup(models.Model):
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='health_checkups')
#     checkup_date = models.DateField()
#     height = models.FloatField(blank=True, null=True)
#     weight = models.FloatField(blank=True, null=True)
#     blood_pressure = models.CharField(max_length=20, blank=True)
#     doctor_remarks = models.TextField(blank=True, null=True)
#     checkup_status = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['-checkup_date']
    
#     def __str__(self):
#         return f"{self.student.full_name} - Checkup ({self.checkup_date})"


# # 5. student_mm_documents/models.py
# from django.db import models
# from django.core.validators import FileExtensionValidator
# from student_profile.models import StudentPersonalInfo

# class StudentDocument(models.Model):
#     DOCUMENT_TYPE_CHOICES = [
#         ('birth_certificate', 'Birth Certificate'),
#         ('transfer_certificate', 'Transfer Certificate'),
#         ('medical_certificate', 'Medical Certificate'),
#         ('character_certificate', 'Character Certificate'),
#         ('nid', 'National ID'),
#         ('other', 'Other'),
#     ]
    
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='documents')
#     document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
#     document_file = models.FileField(
#         upload_to='documents/%Y/%m/',
#         validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
#     )
#     issue_date = models.DateField(blank=True, null=True)
#     expiry_date = models.DateField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     uploaded_by = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.document_type}"


# # 6. student_mm_fees/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class StudentFeeStructure(models.Model):
#     student = models.OneToOneField(StudentPersonalInfo, on_delete=models.CASCADE, related_name='fee_structure')
#     admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
#     annual_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_fee = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_percentage = models.FloatField(default=0)
#     final_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     effective_from = models.DateField()
#     effective_to = models.DateField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.student.full_name} - Fee Structure"


# class StudentFeePayment(models.Model):
#     PAYMENT_STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#         ('partial', 'Partial'),
#         ('overdue', 'Overdue'),
#     ]
    
#     PAYMENT_METHOD_CHOICES = [
#         ('cash', 'Cash'),
#         ('cheque', 'Cheque'),
#         ('bank_transfer', 'Bank Transfer'),
#         ('online', 'Online'),
#     ]
    
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='fee_payments')
#     fee_month = models.CharField(max_length=50)
#     amount_due = models.DecimalField(max_digits=10, decimal_places=2)
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     payment_date = models.DateField(blank=True, null=True)
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
#     transaction_id = models.CharField(max_length=100, blank=True)
#     remarks = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']
#         unique_together = ('student', 'fee_month')
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.fee_month} ({self.payment_status})"


# # 7. student_mm_transport/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class TransportRoute(models.Model):
#     route_name = models.CharField(max_length=100)
#     route_number = models.CharField(max_length=50, unique=True)
#     starting_point = models.CharField(max_length=255)
#     ending_point = models.CharField(max_length=255)
#     stops = models.TextField()  # Comma-separated stops
#     distance_km = models.FloatField()
#     monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.route_name} ({self.route_number})"


# class TransportVehicle(models.Model):
#     vehicle_type = models.CharField(max_length=50)  # e.g., Bus, Van
#     vehicle_number = models.CharField(max_length=50, unique=True)
#     capacity = models.IntegerField()
#     route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
#     driver_name = models.CharField(max_length=100)
#     driver_contact = models.CharField(max_length=20)
#     helper_name = models.CharField(max_length=100, blank=True)
#     helper_contact = models.CharField(max_length=20, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.vehicle_type} - {self.vehicle_number}"


# class StudentTransport(models.Model):
#     student = models.OneToOneField(StudentPersonalInfo, on_delete=models.CASCADE, related_name='transport_info')
#     route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
#     vehicle = models.ForeignKey(TransportVehicle, on_delete=models.SET_NULL, null=True, blank=True)
#     pickup_point = models.CharField(max_length=255)
#     dropoff_point = models.CharField(max_length=255)
#     active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.route.route_name if self.route else 'No Route'}"


# # 8. student_mm_hostel/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class Hostel(models.Model):
#     hostel_name = models.CharField(max_length=100)
#     hostel_type = models.CharField(max_length=50)  # e.g., Boys, Girls
#     capacity = models.IntegerField()
#     warden_name = models.CharField(max_length=100)
#     warden_contact = models.CharField(max_length=20)
#     address = models.TextField()
#     monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return self.hostel_name


# class HostelRoom(models.Model):
#     hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
#     room_number = models.CharField(max_length=50)
#     room_type = models.CharField(max_length=50)  # e.g., Single, Double, Triple
#     capacity = models.IntegerField()
#     current_occupancy = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ('hostel', 'room_number')
    
#     def __str__(self):
#         return f"{self.hostel.hostel_name} - Room {self.room_number}"


# class StudentHostel(models.Model):
#     student = models.OneToOneField(StudentPersonalInfo, on_delete=models.CASCADE, related_name='hostel_info')
#     hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True)
#     room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True, blank=True)
#     check_in_date = models.DateField()
#     check_out_date = models.DateField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.hostel.hostel_name if self.hostel else 'No Hostel'}"


# # 9. student_mm_activities/models.py
# from django.db import models
# from student_profile.models import StudentPersonalInfo

# class Activity(models.Model):
#     ACTIVITY_TYPE_CHOICES = [
#         ('sports', 'Sports'),
#         ('club', 'Club'),
#         ('event', 'Event'),
#         ('competition', 'Competition'),
#     ]
    
#     activity_name = models.CharField(max_length=100)
#     activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES)
#     description = models.TextField(blank=True)
#     start_date = models.DateField()
#     end_date = models.DateField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return self.activity_name


# class StudentActivity(models.Model):
#     student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE, related_name='activities')
#     activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='participants')
#     participation_date = models.DateField()
#     achievement = models.CharField(max_length=100, blank=True)  # e.g., "Gold Medal", "First Prize"
#     certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
#     remarks = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ('student', 'activity')
    
#     def __str__(self):
#         return f"{self.student.full_name} - {self.activity.activity_name}"


