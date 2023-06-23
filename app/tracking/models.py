import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

user_model = get_user_model()


def first_day_of_week():
    """
    A python funtion to calculate the date of the first day of the current week
    """
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday())


def first_day_of_month():
    """
    A python funtion to calculate the date of the first day of the current month
    """
    today = datetime.date.today()
    return today.replace(day=1)


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
    start_date = models.DateField(
        null=True, blank=True, default=datetime.date.today)
    owner = models.ForeignKey(
        user_model, on_delete=models.CASCADE, related_name="goals"
    )

    def __str__(self) -> str:
        return f"<Goal: {self.name}>"

    def get_absolute_url(self) -> str:
        return reverse("goal_detail", args=[str(self.id)])

    @property
    def completed(self) -> bool:
        return self.completion_fraction >= 1

    @property
    def mins_completed(self) -> int:
        if self.unit_time == Goal.UnitTime.DAY:
            calculation = self.sessions.filter(
                date=datetime.datetime.today(),
            ).aggregate(models.Sum("duration_mins"))
        elif self.unit_time == Goal.UnitTime.WEEK:
            calculation = self.sessions.filter(
                date__gte=first_day_of_week(),
            ).aggregate(models.Sum("duration_mins"))
        elif self.unit_time == Goal.UnitTime.MONTH:
            calculation = self.sessions.filter(
                date__gte=first_day_of_month(),
            ).aggregate(models.Sum("duration_mins"))
        else:
            return 0
        if type(calculation["duration_mins__sum"]) != int:
            return 0
        return calculation["duration_mins__sum"]

    @property
    def mins_remaining(self) -> int:
        return max(self.duration_mins - self.mins_completed, 0)

    @property
    def completion_fraction(self) -> float:
        return self.mins_completed / self.duration_mins

    @property
    def completion_percentage(self) -> int:
        return int(self.completion_fraction * 100)

    @property
    def close_to_completion(self) -> bool:
        return self.completion_fraction > 0.80


class Session(models.Model):
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    duration_mins = models.IntegerField(
        verbose_name="Duration (mins)", help_text="The time spent in minutes", null=True
    )
    goal = models.ForeignKey(
        Goal, on_delete=models.CASCADE, related_name="sessions")
    notes = models.TextField(blank=True, null=True)
    active = models.BooleanField(
        default=False, help_text="This session isn't completed yet"
    )

    def __str__(self) -> str:
        return f"<Session: {self.goal.name}, {self.date}>"

    def get_absolute_url(self) -> str:
        return reverse("session_detail", args=[str(self.goal.id), str(self.id)])
