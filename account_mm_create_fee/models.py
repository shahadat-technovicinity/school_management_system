from django.db import models

from academic_mm_class_and_section.models import AcademicClass, Section
from accounts_mm_fee_type.models import FeeHead
from apps.students.models import Student


class CreateFee(models.Model):
    APPLIES_TO_CHOICES = [
        ('class', 'Class wise'),
        ('student', 'Individual student'),
    ]
    PERIOD_CHOICES = [
        ('one_time', 'One-time'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semester', 'Semester'),
        ('yearly', 'Yearly'),
    ]

    fee_head = models.ForeignKey(
        FeeHead, on_delete=models.PROTECT, related_name='fee_structures',
        help_text="যে Fee Type বাছা হয়েছে (সর্বোচ্চ স্তর বা যেকোনো স্তর)",
    )
    applies_to = models.CharField(max_length=10, choices=APPLIES_TO_CHOICES, default='class')

    # class wise হলে
    academic_class = models.ForeignKey(
        AcademicClass, on_delete=models.CASCADE, null=True, blank=True,
        related_name='fee_structures',
    )
    sections = models.ManyToManyField(
        Section, blank=True, related_name='fee_structures',
        help_text="Class wise fee এ কমপক্ষে একটা section বাছতে হবে",
    )

    # individual হলে
    students = models.ManyToManyField(
        Student, blank=True, related_name='fee_structures',
    )

    payment_period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Fee Structure"

    def __str__(self):
        return f"{self.fee_head.name} ({self.get_applies_to_display()})"

    @property
    def total_amount(self):
        return sum((i.amount for i in self.items.all()), 0)


class FeeStructureItem(models.Model):
    """একদম নিচের স্তরের fee এর টাকা। Fee Type এর নিচে sub category না থাকলে Fee Type নিজেই item।"""

    structure = models.ForeignKey(CreateFee, on_delete=models.CASCADE, related_name='items')
    fee_head = models.ForeignKey(FeeHead, on_delete=models.PROTECT, related_name='fee_structure_items')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('structure', 'fee_head')
        ordering = ['fee_head__order', 'fee_head_id']

    def __str__(self):
        return f"{self.fee_head.name}: {self.amount}"