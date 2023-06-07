import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.decorators.http import require_http_methods

from .models import Goal, Session


class GoalListView(generic.ListView, LoginRequiredMixin):
    model = Goal

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


class CreateGoalView(generic.CreateView, LoginRequiredMixin):
    model = Goal
    fields = ("name", "description", "duration_min", "unit_time", "start_date")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class UpdateGoalView(generic.UpdateView, LoginRequiredMixin):
    model = Goal
    fields = ("name", "description", "duration_min", "unit_time")

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


class GoalDetailView(generic.DetailView, LoginRequiredMixin):
    model = Goal

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


class DeleteGoalView(generic.DeleteView, LoginRequiredMixin):
    model = Goal
    success_url = reverse_lazy("goal_list")

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


# TODO: change date widget to native date picker
class CreateSessionView(generic.CreateView, LoginRequiredMixin):
    model = Session
    fields = (
        "duration_mins",
        "date",
        "start_time",
        "notes",
        "active",
    )

    def get_initial(self):
        goal = Goal.objects.filter(
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            raise ObjectDoesNotExist("Goal does not exist")
        return {
            "date": datetime.date.today(),
            "start_time": datetime.datetime.now(),
            "duration_mins": goal.duration_mins,
        }

    def form_valid(self, form):
        goal = Goal.objects.filter(
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            return HttpResponseForbidden(
                "Not sure how you got here but it's not allowed"
            )
        new_session = form.save(commit=False)
        new_session.goal = goal
        new_session.save()
        return HttpResponseRedirect(new_session.get_absolute_url())


class SessionDetailView(generic.DetailView, LoginRequiredMixin):
    model = Session

    def get_queryset(self):
        return Session.objects.filter(
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"]
        )


class UpdateSessionView(generic.UpdateView, LoginRequiredMixin):
    model = Session
    fields = (
        "duration_mins",
        "date",
        "start_time",
        "notes",
        "active",
    )

    def get_queryset(self):
        return Session.objects.filter(
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"]
        )


class DeleteSessionView(generic.UpdateView, LoginRequiredMixin):
    model = Session

    def get_queryset(self):
        return Session.objects.filter(
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"]
        )

    def get_success_url(self):
        # AI code, might not work if the object is already deleted
        return self.object.goal.get_absolute_url()


class StartTimerSession(generic.CreateView, LoginRequiredMixin):
    model = Session
    fields = ("duration_mins",)
    template_name = "start_timer_session.html"

    def form_valid(self, form):
        goal = Goal.objects.filter(
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

    def get_initial(self):
        goal = Goal.objects.filter(
            owner=self.request.user, id=self.kwargs["goal_id"]
        ).first()
        if not goal:
            raise ObjectDoesNotExist("Goal not found")
        return {
            "duration_mins": goal.duration_mins,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context


class RunningTimerSession(generic.UpdateView, LoginRequiredMixin):
    model = Session
    fields = ("notes",)
    template_name = "running_timer_session.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["goal_id"] = self.kwargs["goal_id"]
        return context

    def form_valid(self, form):
        updated_session = form.save(commit=False)
        updated_session.active = False
        updated_session.save()
        return HttpResponseRedirect(
            reverse("goal_detail", kwargs={"goal_id": self.kwargs["goal_id"]})
        )

    def get_queryset(self):
        return Session.objects.filter(
            goal__owner=self.request.user, goal_id=self.kwargs["goal_id"], active=True
        )


# @login_required
# @require_http_methods(["GET", "POST"])
# def session_timer_create(request, goal_id):
#     # TODO: implement ajax or form + htmx endpoints for this
#     goal = Goal.objects.filter(owner=request.user, pk=goal_id).first()
#     if not goal:
#         return HttpResponseNotFound("Uh oh!")
#
#     return render(request, "session_timer.html", {"goal": goal})


@login_required
def session_timer_finish(request, goal_id, pk):
    pass


@login_required
def session_stopwatch_view(request, goal_id):
    # TODO: implement ajax or form + htmx endpoints for this
    goal = Goal.objects.filter(owner=request.user, pk=goal_id).first()
    if not goal:
        return HttpResponseNotFound("Uh oh!")
    return render(request, "session_stopwatch.html", {"goal": goal})
