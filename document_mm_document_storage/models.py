import uuid
from django.db import models


class Cabinet(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Shelf(models.Model):
    name = models.CharField(max_length=100)
    cabinet = models.ForeignKey(
        Cabinet, on_delete=models.CASCADE, related_name='shelves'
    )

    def __str__(self):
        return f"{self.cabinet.name} → {self.name}"

    class Meta:
        ordering = ['cabinet__name', 'name']


class Document(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        IN_USE    = 'in_use',    'In Use'
        IN_TRANSIT= 'in_transit','In Transit'
        MISSING   = 'missing',   'Missing'

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name          = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100)
    cabinet       = models.ForeignKey(
        Cabinet, on_delete=models.SET_NULL, null=True, related_name='documents'
    )
    shelf         = models.ForeignKey(
        Shelf, on_delete=models.SET_NULL, null=True, related_name='documents'
    )
    tag_number    = models.CharField(max_length=50, blank=True)
    status        = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    last_modified_by = models.CharField(max_length=255, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']


class LocationMoveLog(models.Model):
    """
    Document-এর location যতবার বদলাবে, এখানে history থাকবে।
    Figma-র 'reason_for_move' আর 'notes' এখানে save হয়।
    """
    document       = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='move_logs'
    )
    from_cabinet   = models.CharField(max_length=100, blank=True)
    from_shelf     = models.CharField(max_length=100, blank=True)
    to_cabinet     = models.CharField(max_length=100)
    to_shelf       = models.CharField(max_length=100)
    reason_for_move= models.CharField(max_length=255, blank=True)
    notes          = models.TextField(blank=True)
    moved_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document.name} moved at {self.moved_at}"

    class Meta:
        ordering = ['-moved_at']