from django.db import models
from reg_mm_stock_event.models import StockInventory


class FacilityLocation(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Class 6", "Science Lab"
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class FacilityFurnitureItem(models.Model):
    CONDITION_CHOICES = [
        ('needs_repair', 'Needs Repair'),
        ('replace', 'Replace'),
    ]

    stock_item = models.ForeignKey(
        StockInventory, 
        on_delete=models.CASCADE, 
        related_name='facility_issues'
    )
    # ইউজারের দেওয়া সরাসরি টেক্সট ইনপুট হিসেবে সেভ হবে
    location = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    condition_status = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICES
    )
    additional_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock_item.item_name} - {self.location} ({self.condition_status})"