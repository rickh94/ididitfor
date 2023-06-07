"""ididitfor URL Configuration"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("external.urls")),
    path("tracking/", include("tracking.urls")),
]
