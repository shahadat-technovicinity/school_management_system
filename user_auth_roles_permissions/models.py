from django.db import models
from django.conf import settings
from django.apps import apps as django_apps


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().capitalize()
        super(Role, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='feature_permissions')
    feature_name = models.CharField(max_length=100)
    feature_slug = models.CharField(max_length=100)
    can_create = models.BooleanField(default=False)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'feature_name', 'feature_slug')

    def __str__(self):
        return f"{self.role.name} -> {self.feature_name} ({self.feature_slug})"

    @classmethod
    def get_all_app_features(cls):
        """
        INSTALLED_APPS ঘুরে প্রতিটা লোকাল app এর মডেলগুলোকে
        feature হিসেবে ধরে অটোমেটিক স্ট্রাকচার্ড ডাটা জেনারেট করে।
        """
        # Django বা থার্ডপার্টি app বাদ দেওয়ার জন্য এক্সক্লুড লিস্ট
        EXCLUDE_PREFIXES = (
            'django.', 'rest_framework', 'drf_yasg', 'corsheaders',
            'django_celery_results', 'rest_framework_simplejwt',
        )

        structured_data = {}

        for app_config in django_apps.get_app_configs():
            app_label = app_config.label  # e.g. 'admissions'
            app_name_full = app_config.name  # e.g. 'apps.admissions' বা 'admissions'

            if app_name_full.startswith(EXCLUDE_PREFIXES):
                continue

            models_in_app = list(app_config.get_models())
            if not models_in_app:
                continue

            features = []
            for model in models_in_app:
                features.append({
                    "slug": model._meta.model_name,          # e.g. 'studentadmission'
                    "label": model._meta.verbose_name.title()  # e.g. 'Studentadmission'
                })

            structured_data[app_label] = {
                "app_label": app_label.replace('_', ' ').title(),
                "features": features
            }

        return structured_data