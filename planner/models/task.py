from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from multiselectfield import MultiSelectField

from planner.models.day import Day
from planner.models.month import Subject

STUDY_TYPE_CHOICES = [
    ("theory", "Theory 📚"),
    ("coding", "Coding 💻"),
    ("practice", "Practice 🔨"),
    ("review", "Review 🔄"),
    ("project", "Project 🏗️"),
    ("research", "Research 🔬"),
]

PRIORITY_CHOICES = [
    (1, "Low"),
    (2, "Medium"),
    (3, "High"),
    (4, "Critical"),
]

DIFFICULTY_CHOICES = [
    (1, "Beginner"),
    (2, "Easy"),
    (3, "Medium"),
    (4, "Hard"),
    (5, "Expert"),
]


class BaseTask(models.Model):
    """Abstract base model for common task fields"""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subjects = models.ManyToManyField(
        Subject,
        related_name="%(class)s_tasks",
        blank=True,
    )
    study_type = MultiSelectField(choices=STUDY_TYPE_CHOICES, max_choices=3)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=2)
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=3)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class PlannedTask(BaseTask):
    """Tasks planned for a specific day"""

    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="planned_tasks")

    # Planning fields
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)  # minutes

    class Meta:
        ordering = ["start_time", "created_at"]
        indexes = [
            models.Index(fields=["day", "start_time"]),
            models.Index(fields=["day", "priority"]),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate duration if times provided
        if self.start_time and self.end_time and not self.duration:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            duration = end_minutes - start_minutes
            if duration > 0:
                self.duration = duration
        super().save(*args, **kwargs)

    def get_planned_duration_display(self):
        """Human readable duration"""
        if not self.duration:
            return "Not set"
        hours, minutes = divmod(self.duration, 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"


class ActualTask(BaseTask):
    """Tasks actually performed -
    can be linked to planned tasks or standalone (bonus)"""

    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="actual_tasks")
    planned_task = models.OneToOneField(
        PlannedTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="execution",
    )

    # Execution fields
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)  # minutes

    # Results
    completion_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    quality_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    focus_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        ordering = ["start_time", "created_at"]
        indexes = [
            models.Index(fields=["day", "start_time"]),
            models.Index(fields=["planned_task"]),
            models.Index(fields=["completion_percentage"]),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate duration if times provided
        if self.start_time and self.end_time and not self.duration:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            duration = end_minutes - start_minutes
            if duration > 0:
                self.duration = duration

        # Inherit from planned task if linked and fields are empty
        if self.planned_task and not self.title:
            self.title = self.planned_task.title
            self.description = self.planned_task.description
            self.priority = self.planned_task.priority
            self.difficulty = self.planned_task.difficulty
            self.study_type = self.planned_task.study_type

        self.completion_percentage = self.calculate_completion_percentage()
        super().save(*args, **kwargs)

        # Copy subjects from planned task after save (M2M needs saved instance)
        if self.planned_task and not self.subjects.exists():
            self.subjects.set(self.planned_task.subjects.all())

    @property
    def is_bonus_task(self):
        """Check if this is an unplanned/bonus task"""
        return self.planned_task is None

    def calculate_completion_percentage(self):
        """Calculate completion compared to planned duration"""
        if not self.planned_task or not self.planned_task.duration or not self.duration:
            return 0

        planned = self.planned_task.duration
        actual = self.duration

        # Efficiency = planned/actual (>1 means faster than planned)
        return round(actual / planned, 2) * 100
