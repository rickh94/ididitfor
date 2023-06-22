from django.contrib import sitemaps
from django.urls import reverse


class ExternalSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["index", "register"]

    def location(self, item):
        return reverse(item)
