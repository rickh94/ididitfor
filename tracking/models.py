import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

user_model = get_user_model()


class Goal(models.Model):
    class UnitTime(models.TextChoices):
        DAY = "D", _("Day")
        WEEK = "W", _("Week")
        MONTH = "M", _("Month")

    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    duration_mins = models.IntegerField(
        verbose_name="Desired Duration (minutes)",
        help_text="Desired number of minutes at a time.",
    )
    unit_time = models.CharField(
        max_length=1,
        choices=UnitTime.choices,
        default=UnitTime.WEEK,
        verbose_name="Unit of Time",
        help_text="The time interval to measure your goal against.",
    )
    active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True, default=datetime.date.today)
    owner = models.ForeignKey(
        user_model, on_delete=models.CASCADE, related_name="goals"
    )

    def __str__(self):
        return f"<Goal: {self.name}>"

    def get_absolute_url(self):
        return reverse("goal_detail", args=[str(self.id)])


class Session(models.Model):
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    duration_mins = models.IntegerField(
        verbose_name="Duration (mins)", help_text="The time spent in minutes", null=True
    )
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="sessions")
    notes = models.TextField(blank=True, null=True)
    active = models.BooleanField(
        default=False, help_text="This session isn't completed yet"
    )

    def __str__(self):
        return f"<Session: {self.goal.name}, {self.date}>"

    def get_absolute_url(self):
        return reverse("session_detail", args=[str(self.goal.id), str(self.id)])
