from django.db import models

from planner.models.day import Day
from planner.models.month import MonthlyVault
from planner.models.week import Week


class DayReport(models.Model):
    day = models.OneToOneField(Day, on_delete=models.CASCADE, related_name="report")
    generated_at = models.DateTimeField(auto_now=True)
    summary = models.JSONField(default=dict)

    def __str__(self):
        return f"day report: {self.day}"


class WeekReport(models.Model):
    week = models.OneToOneField(Week, on_delete=models.CASCADE, related_name="report")
    generated_at = models.DateTimeField(auto_now=True)
    summary = models.JSONField(default=dict)

    def __str__(self):
        return f"week report {self.week}"


class MonthReport(models.Model):
    monthly_vault = models.OneToOneField(
        MonthlyVault,
        on_delete=models.CASCADE,
        related_name="report",
    )
    generated_at = models.DateTimeField(auto_now=True)
    summary = models.JSONField(default=dict)

    def __str__(self):
        return f"month report {self.monthly_vault}"
