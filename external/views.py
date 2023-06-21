import random

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic


def index(request: HttpRequest) -> HttpResponse:
    """Render the index page."""
    random_mins = random.randint(5, 60)
    return render(request, "index.html", {"random_mins": random_mins})


class UserEmailCreationForm(UserCreationForm[User]):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )


class SignUpView(generic.CreateView[User, UserEmailCreationForm]):
    form_class = UserEmailCreationForm
    success_url = reverse_lazy("login")
    template_name = "register.html"
