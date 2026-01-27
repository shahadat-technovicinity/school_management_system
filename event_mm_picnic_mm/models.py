from django.db import models

class Picnic(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    expected_participants = models.PositiveIntegerField() 
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=[('Upcoming', 'Upcoming'), ('Previous', 'Previous')], 
        default='Upcoming'
    )

    def __str__(self):
        return self.name