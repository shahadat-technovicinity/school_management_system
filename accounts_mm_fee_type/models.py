from django.db import models


class FeeHead(models.Model):
    name = models.CharField(max_length=150)
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        help_text="খালি থাকলে এটা সর্বোচ্চ স্তরের Fee Type",
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Fee Head"
        verbose_name_plural = "Fee Heads"

    def __str__(self):
        return self.name