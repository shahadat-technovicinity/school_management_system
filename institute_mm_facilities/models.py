from django.db import models


class FacilityFurnitureItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('educational_tools', 'Educational_tools'),
        ('storage', 'Strorage'),
        ('sports_equipment', 'Sports_Equipment'),
    ]

    CONDITION_CHOICES = [
        ('good', 'Good'),
        ('needs repair', 'Needs Repair'),
        ('replace', 'Replace'),
    ]

    item_name = models.CharField(max_length=255)
    item_type = models.CharField(
        max_length=50,
        choices=ITEM_TYPE_CHOICES
    )
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
        return self.item_name
