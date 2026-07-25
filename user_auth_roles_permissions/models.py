from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().capitalize()
        super(Role, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Permission(models.Model):
    group_name = models.CharField(max_length=100)
    feature_name = models.CharField(max_length=100)
    feature_slug = models.CharField(max_length=100)
    can_create = models.BooleanField(default=False)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('feature_name', 'feature_slug')

    def __str__(self):
        # Permission has no role FK — show group + feature
        return f"{self.group_name} -> {self.feature_name} ({self.feature_slug})"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permissions = models.ManyToManyField(Permission, related_name='role_permissions', blank=True)

    def __str__(self):
        # M2M field — cannot access single item in __str__, show role name only
        return f"{self.role.name}"