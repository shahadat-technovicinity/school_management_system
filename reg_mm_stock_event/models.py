from django.db import models

class StockInventory(models.Model):
    CATEGORY_CHOICES = [
        ('Laboratory Equipment', 'Laboratory Equipment'),
        ('Furniture', 'Furniture'),
        ('Educational Materials', 'Educational Materials'),
    ]

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    location_or_sub_category = models.CharField(max_length=100)
    
    item_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)
    total_capacity = models.IntegerField(default=0)
    reorder_threshold = models.IntegerField(default=5)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_category(self):
        return f"{self.category} / {self.location_or_sub_category}"

    @property
    def status(self):
        if self.quantity <= 0:
            return "Out of Stock"
        elif self.quantity <= self.reorder_threshold:
            return "Low Stock"
        return "In Stock"

    def __str__(self):
        return self.item_name