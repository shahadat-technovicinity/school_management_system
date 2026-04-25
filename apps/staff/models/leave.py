from django.db import models
from .profile import StaffProfile

class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    
    # HR/Admin action
    approved_by = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_leaves')
    comments = models.TextField(blank=True)
    
    # Substitute
    substitute_staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='substitution_tasks')

    def __str__(self):
        return f"{self.staff.employee_id} - {self.leave_type.name} ({self.start_date})"
