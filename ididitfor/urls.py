"""ididitfor URL Configuration"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from external.sitemap import ExternalSitemap
from passkey_auth.sitemap import PAuthSitemap

sitemaps = {
    "pauth": PAuthSitemap,
    "external": ExternalSitemap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("external.urls")),
    path("tracking/", include("tracking.urls")),
    path("pauth/", include("passkey_auth.urls")),
]
