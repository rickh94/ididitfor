import datetime
from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.http.response import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.decorators.http import require_GET

from ididitfor.types import AuthenticatedHttpRequest

from .models import Goal, Session

User = get_user_model()


class GoalListView(generic.ListView[Goal], LoginRequiredMixin):
    model = Goal

    def get_queryset(self) -> QuerySet[Goal]:
        return Goal.objects.filter(owner=self.request.user)  # type: ignore

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/goal_list.html"]
        else:
            return ["tracking/goal_list.html"]


class CreateGoalView(generic.CreateView[Goal, ModelForm[Goal]], LoginRequiredMixin):
    model = Goal
    fields = ("name", "description", "duration_mins",
              "unit_time", "start_date")

    def form_valid(self, form: ModelForm[Goal]) -> HttpResponse:
        new_goal = form.save(commit=False)
        new_goal.owner = self.request.user  # type: ignore
        new_goal.save()
        messages.success(self.request, f"Goal {new_goal.name} created")
        return HttpResponseRedirect(new_goal.get_absolute_url())

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/goal_form.html"]
        else:
            return ["tracking/goal_form.html"]


class UpdateGoalView(generic.UpdateView[Goal, ModelForm[Goal]], LoginRequiredMixin):
    model = Goal
    fields = ("name", "description", "duration_mins", "unit_time")

    def get_queryset(self) -> QuerySet[Goal]:
        return Goal.objects.filter(owner=self.request.user)  # type: ignore

    def form_valid(self, form: ModelForm[Goal]) -> HttpResponse:
        new_goal = form.save()
        messages.success(self.request, f"Goal {new_goal.name} updated")
        return HttpResponseRedirect(new_goal.get_absolute_url())

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/goal_form.html"]
        else:
            return ["tracking/goal_form.html"]


class GoalDetailView(generic.DetailView[Goal], LoginRequiredMixin):
    model = Goal

    def get_queryset(self) -> QuerySet[Goal]:
        return Goal.objects.filter(owner=self.request.user)  # type: ignore

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["sessions"] = self.object.sessions.order_by("-date")[:10]
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/goal_detail.html"]
        else:
            return ["tracking/goal_detail.html"]


class DeleteGoalView(generic.DeleteView, LoginRequiredMixin):  # type: ignore
    model = Goal
    success_url = reverse_lazy("goal_list")

    def get_queryset(self) -> QuerySet[Goal]:
        return Goal.objects.filter(owner=self.request.user)  # type: ignore

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["sessions"] = self.object.sessions.order_by("-date")[:10]
        return context

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, f"Goal {self.object.name} deleted")
        return HttpResponseRedirect(self.get_success_url())

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/goal_confirm_delete.html"]
        else:
            return ["tracking/goal_confirm_delete.html"]


class GoalSessionList(generic.DetailView[Goal], LoginRequiredMixin):
    model = Goal

    def get_queryset(self) -> QuerySet[Goal]:
        return Goal.objects.filter(owner=self.request.user)  # type: ignore

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["sessions"] = self.object.sessions.order_by("-date")[:10]
        context["all_sessions"] = self.object.sessions.order_by("-date")
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/goal_session_list.html"]
        else:
            return ["tracking/goal_session_list.html"]


# TODO: change date widget to native date picker
class CreateSessionView(
    generic.CreateView[Session, ModelForm[Session]], LoginRequiredMixin
):
    model = Session
    fields = (
        "duration_mins",
        "date",
        "start_time",
        "notes",
        "active",
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context

    def get_initial(self) -> dict[str, Any]:
        goal = Goal.objects.filter(  # type: ignore
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            raise ObjectDoesNotExist("Goal does not exist")
        return {
            "date": datetime.date.today(),
            "start_time": datetime.datetime.now(),
            "duration_mins": goal.mins_remaining,
        }

    def form_valid(self, form: ModelForm[Session]) -> HttpResponse:
        goal = Goal.objects.filter(  # type: ignore
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            return HttpResponseNotFound("Goal does not exist")
        new_session = form.save(commit=False)
        new_session.goal = goal
        new_session.save()
        messages.success(
            self.request, f"Session created for goal {new_session.goal.name}"
        )
        return HttpResponseRedirect(new_session.get_absolute_url())

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/session_form.html"]
        else:
            return ["tracking/session_form.html"]


class SessionDetailView(generic.DetailView[Session], LoginRequiredMixin):
    model = Session

    def get_queryset(self) -> QuerySet[Session]:
        return Session.objects.filter(  # type: ignore
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"]
        )

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/session_detail.html"]
        else:
            return ["tracking/session_detail.html"]


class UpdateSessionView(
    generic.UpdateView[Session, ModelForm[Session]], LoginRequiredMixin
):
    model = Session
    fields = (
        "duration_mins",
        "date",
        "start_time",
        "notes",
        "active",
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context

    def get_queryset(self) -> QuerySet[Session]:
        return Session.objects.filter(  # type: ignore
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"]
        )

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/session_form.html"]
        else:
            return ["tracking/session_form.html"]


class DeleteSessionView(  # type: ignore
    generic.DeleteView[Session, ModelForm[Session]], LoginRequiredMixin
):
    model = Session

    def get_queryset(self) -> QuerySet[Session]:
        return Session.objects.filter(  # type: ignore
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"]
        )

    def get_success_url(self) -> str:
        return self.object.goal.get_absolute_url()

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/session_confirm_delete.html"]
        else:
            return ["tracking/session_confirm_delete.html"]


class StartTimerSession(
    generic.CreateView[Session, ModelForm[Session]], LoginRequiredMixin
):
    model = Session
    fields = ("duration_mins",)
    template_name = "start_timer_session.html"

    def form_valid(self, form: ModelForm[Session]) -> HttpResponse:
        goal = Goal.objects.filter(  # type: ignore
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            return HttpResponseForbidden(
                "Not sure how you got here but it's not allowed"
            )
        new_session = form.save(commit=False)
        new_session.date = datetime.date.today()
        new_session.start_time = datetime.datetime.now()
        new_session.goal = goal
        new_session.active = True
        new_session.save()
        return HttpResponseRedirect(
            reverse(
                "running_timer_session",
                kwargs={"goal_id": goal.id, "pk": new_session.id},
            )
        )

    def get_initial(self) -> dict[str, Any]:
        goal = Goal.objects.filter(  # type: ignore
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            raise ObjectDoesNotExist("Goal not found")
        return {
            "duration_mins": goal.mins_remaining,
        }

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context

    def get_template_names(self) -> list[str]:
        if self.request.htmx and not self.request.htmx.boosted:
            return ["tracking/htmx/start_timer_session.html"]
        else:
            return ["tracking/start_timer_session.html"]


class RunningTimerSession(
    generic.UpdateView[Session, ModelForm[Session]], LoginRequiredMixin
):
    model = Session
    fields = ("notes", "duration_mins")
    template_name = "running_timer_session.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context

    def form_valid(self, form: ModelForm[Session]) -> HttpResponse:
        updated_session = form.save(commit=False)
        updated_session.active = False
        updated_session.save()
        messages.success(
            self.request,
            f"{updated_session.duration_mins} minutes spent on {updated_session.goal.name}",
        )
        return HttpResponseRedirect(
            reverse("goal_detail", kwargs={"pk": self.kwargs["goal_id"]})
        )

    def get_queryset(self) -> QuerySet[Session]:
        return Session.objects.filter(  # type: ignore
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"], active=True
        )


@require_GET
@login_required
def start_stopwatch_session(
    request: AuthenticatedHttpRequest, goal_id: int
) -> HttpResponse:
    goal = Goal.objects.filter(
        owner=request.user,
        id=goal_id,
    ).first()
    if not goal:
        return HttpResponseForbidden("Not sure how you got here but it's not allowed")
    new_session = Session(
        goal=goal,
        start_time=datetime.datetime.now(),
        active=True,
        date=datetime.datetime.today(),
    )
    new_session.save()
    return HttpResponseRedirect(
        reverse(
            "running_stopwatch_session",
            kwargs={"goal_id": goal.id, "pk": new_session.id},
        )
    )


class RunningStopwatchSession(
    generic.UpdateView[Session, ModelForm[Session]], LoginRequiredMixin
):
    model = Session
    fields = ("notes", "duration_mins")
    template_name = "running_stopwatch_session.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context

    def form_valid(self, form: ModelForm[Session]) -> HttpResponse:
        updated_session = form.save(commit=False)
        updated_session.active = False
        updated_session.save()
        messages.success(
            self.request,
            f"{updated_session.duration_mins} minutes spent on {updated_session.goal.name}",
        )
        return HttpResponseRedirect(
            reverse("goal_detail", kwargs={"pk": self.kwargs["goal_id"]})
        )

    def get_queryset(self) -> QuerySet[Session]:
        return Session.objects.filter(  # type: ignore
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"], active=True
        )
