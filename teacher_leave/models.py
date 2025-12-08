from django.db import models
from django.conf import settings
from teacher.models import Teacher


class LeaveType(models.Model):
    """
    Leave Type model to define different types of leaves.
    E.g., Medical Leave, Casual Leave, Maternity Leave, Paternity Leave
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_days = models.PositiveIntegerField(
        default=0,
        help_text="Default number of days allocated for this leave type per year"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    """
    Tracks leave balance for each teacher per leave type.
    This stores the total allocated and used leaves.
    """
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="leave_balances"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name="balances"
    )
    total_allocated = models.PositiveIntegerField(
        default=0,
        help_text="Total leaves allocated for the year"
    )
    used = models.PositiveIntegerField(
        default=0,
        help_text="Total leaves used"
    )
    year = models.PositiveIntegerField(
        help_text="Year for which this balance applies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "leave_type__name"]
        verbose_name = "Leave Balance"
        verbose_name_plural = "Leave Balances"
        unique_together = ["teacher", "leave_type", "year"]

    def __str__(self):
        return f"{self.teacher} - {self.leave_type.name} ({self.year})"

    @property
    def available(self):
        """Calculate available leaves."""
        return max(0, self.total_allocated - self.used)


class TeacherLeave(models.Model):
    """
    Teacher Leave Application model.
    Stores leave applications submitted by teachers.
    """
    LEAVE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("cancelled", "Cancelled"),
    ]

    LEAVE_DAY_CHOICES = [
        ("full_day", "Full Day"),
        ("first_half", "First Half"),
        ("second_half", "Second Half"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="leave_applications"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name="applications"
    )
    leave_date = models.DateField(
        help_text="Date when leave was applied"
    )
    from_date = models.DateField(
        help_text="Leave start date"
    )
    to_date = models.DateField(
        help_text="Leave end date"
    )
    leave_days = models.CharField(
        max_length=20,
        choices=LEAVE_DAY_CHOICES,
        default="full_day",
        help_text="Type of leave day"
    )
    no_of_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        help_text="Total number of leave days"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for taking leave"
    )
    status = models.CharField(
        max_length=20,
        choices=LEAVE_STATUS_CHOICES,
        default="pending"
    )
    
    # Admin action fields
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves",
        help_text="Admin who reviewed this application"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.TextField(
        blank=True,
        help_text="Remarks by admin when approving/declining"
    )

    # Timestamps
    applied_on = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_on", "-created_at"]
        verbose_name = "Teacher Leave"
        verbose_name_plural = "Teacher Leaves"

    def __str__(self):
        return f"{self.teacher} - {self.leave_type.name} ({self.from_date} to {self.to_date})"

    def save(self, *args, **kwargs):
        # Calculate number of days if not provided
        if not self.no_of_days:
            delta = (self.to_date - self.from_date).days + 1
            if self.leave_days in ["first_half", "second_half"]:
                self.no_of_days = delta * 0.5
            else:
                self.no_of_days = delta
        super().save(*args, **kwargs)
