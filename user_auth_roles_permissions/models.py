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
    """
    Defines WHAT features exist in the system.
    Does NOT store who can do what — that is RolePermission's job.
    """
    group_name = models.CharField(max_length=100)   # e.g. "Academic", "Staff"
    feature_name = models.CharField(max_length=100)  # e.g. "Teacher Management"
    feature_slug = models.CharField(max_length=100, unique=True)  # e.g. "teacher"

    def __str__(self):
        return f"{self.group_name} → {self.feature_name}"


class RolePermission(models.Model):
    """
    Defines WHAT a specific Role can do on a specific Permission/Feature.
    Each Role gets its own CRUD settings per feature — fully independent.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    can_create = models.BooleanField(default=False)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'permission')  # one record per Role+Feature pair

    def __str__(self):
        return f"{self.role.name} → {self.permission.feature_name}"