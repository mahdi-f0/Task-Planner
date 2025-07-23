from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.models import ProcessedImageField
from imagekit.processors import Adjust
from imagekit.processors import ResizeToFill
from imagekit.processors import ResizeToFit

User = get_user_model()


class MonthlyVault(models.Model):
    user = models.ForeignKey(User, models.CASCADE, "monthly_vaults")
    name = models.CharField(
        max_length=50,
        db_index=True,
        default="My Month",
        help_text="my awesome month",
    )
    start_date = models.DateField(
        help_text="when the month starts",
        default=timezone.now,
    )
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_over = models.BooleanField(default=False)

    class Meta:
        unique_together = ["user", "start_date"]
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.name}: {self.user}"

    def save(self, *args, **kwargs):
        if self.start_date:
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)


class Subject(models.Model):
    monthly_vault = models.ForeignKey(MonthlyVault, models.CASCADE, "subjects")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["monthly_vault", "title"]
        ordering = ["title"]

    def __str__(self):
        return self.title


class MonthlyProject(models.Model):
    monthly_vault = models.ForeignKey(
        MonthlyVault,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField(max_length=200)
    url = models.URLField(
        blank=True,
        help_text="a link to a github repo ,a website, or google drive folder",
    )
    description = models.TextField(blank=True)
    image = ProcessedImageField(
        upload_to="projects/",
        processors=[ResizeToFit(1080, 810)],
        format="WEBP",
        options={"quality": 85},
    )

    # Thumbnail generated on-the-fly from the processed image
    thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(200, 150), Adjust(contrast=1.2)],
        format="WEBP",
        options={"quality": 70},
    )

    class Meta:
        unique_together = ["monthly_vault", "title"]
        ordering = ["monthly_vault", "title"]

    def __str__(self):
        return self.title
