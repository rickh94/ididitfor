from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic


def index(request):
    return render(request, "index.html", {})


class UserEmailCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
        )


class SignUpView(generic.CreateView):
    form_class = UserEmailCreationForm
    success_url = reverse_lazy("login")
    template_name = "register.html"
