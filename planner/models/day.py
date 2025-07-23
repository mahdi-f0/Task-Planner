from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ValidationError

from .week import Week

User = get_user_model()


class Day(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="days")
    week = models.ForeignKey(Week, models.CASCADE, "days")
    date = models.DateField()

    class Meta:
        unique_together = [("user", "date"), ("week", "date")]
        ordering = ["-date"]

    def __str__(self):
        return self.date

    def clean(self):
        """Ensure date falls within week's date range"""
        if self.date and self.week:
            if not (self.week.start_date <= self.date <= self.week.end_date):
                day_not_in_week_error = "Date must fall within the week's date range"
                raise ValidationError(day_not_in_week_error)
