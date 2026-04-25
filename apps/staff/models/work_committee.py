from django.db import models
from .profile import StaffProfile

class WorkAssignment(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    assigned_to = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attachment = models.FileField(upload_to='staff/work_assignments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} -> {self.assigned_to.employee_id}"

class CommitteeMember(models.Model):
    COMMITTEE_TYPE_CHOICES = [
        ('PTA', 'PTA Committee'),
        ('MMC', 'MMC Committee'),
        ('Cabinet', 'Cabinet Committee'),
    ]
    
    staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255) # For external members
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    committee_type = models.CharField(max_length=50, choices=COMMITTEE_TYPE_CHOICES)
    position = models.CharField(max_length=100)
    term_start = models.DateField()
    term_end = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name or self.staff.user.get_full_name()} - {self.committee_type}"

class CommitteeNotice(models.Model):
    committee_type = models.CharField(max_length=50, choices=CommitteeMember.COMMITTEE_TYPE_CHOICES)
    session_number = models.CharField(max_length=50) # e.g., "Session #5"
    date = models.DateField()
    time = models.TimeField()
    agenda_items = models.TextField() # Markdown/HTML from UI editor
    attachment = models.FileField(upload_to='committee/notices/', null=True, blank=True)
    include_member_list = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='Sent') # Sent, Draft
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.committee_type} Notice - {self.session_number}"

class CommitteeCommunication(models.Model):
    TYPE_CHOICES = [
        ('Meeting Reminder', 'Meeting Reminder'),
        ('Meeting Cancellation', 'Meeting Cancellation'),
        ('General Announcement', 'General Announcement'),
    ]
    committee_type = models.CharField(max_length=50, choices=CommitteeMember.COMMITTEE_TYPE_CHOICES)
    recipients = models.CharField(max_length=100) # e.g., "All PTA Members"
    message_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    request_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message_type} to {self.recipients}"
