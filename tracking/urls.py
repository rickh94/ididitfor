from django.urls import path

from . import views

urlpatterns = [
    path("goals/", views.GoalListView.as_view(), name="goal_list"),
    path("goals/create/", views.CreateGoalView.as_view(), name="create_goal"),
    path("goals/<int:pk>/", views.GoalDetailView.as_view(), name="goal_detail"),
    path("goals/<int:pk>/edit/", views.UpdateGoalView.as_view(), name="edit_goal"),
    path(
        "goals/<int:goal_id>/session/enter",
        views.CreateSessionView.as_view(),
        name="manual_session",
    ),
    path(
        "goals/<int:goal_id>/session/<int:pk>",
        views.SessionDetailView.as_view(),
        name="session_detail",
    ),
    path(
        "goals/<int:goal_id>/session/new-timer",
        views.StartTimerSession.as_view(),
        name="create_timer_session",
    ),
    path(
        "goals/<int:goal_id>/session/<int:pk>/timer",
        views.RunningTimerSession.as_view(),
        name="running_timer_session",
    ),
    path(
        "goals/<int:goal_id>/session/new-stopwatch",
        views.start_stopwatch_session,
        name="create_stopwatch_session",
    ),
    path(
        "goals/<int:goal_id>/session/<int:pk>/stopwatch",
        views.RunningStopwatchSession.as_view(),
        name="running_stopwatch_session",
    ),
]
