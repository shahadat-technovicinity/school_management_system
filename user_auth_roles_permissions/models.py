from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.display_name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'feature')

    def __str__(self):
        return f"{self.role.name} - {self.feature.display_name}"