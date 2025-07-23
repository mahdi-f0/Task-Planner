from datetime import timedelta

from django.db import models

from .month import MonthlyVault


class Week(models.Model):
    monthly_vault = models.ForeignKey(MonthlyVault, models.CASCADE, "weeks")
    week_number = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ["monthly_vault", "week_number"]
        ordering = ["monthly_vault", "week_number"]

    def __str__(self):
        return f"week {self.week_number} of {self.monthly_vault.name}"

    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + timedelta(days=7)
        super().save(*args, **kwargs)
