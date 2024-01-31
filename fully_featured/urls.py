from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path("", include("fully_featured.core.urls")),
    path("user/", include("fully_featured.user.urls")),
    path("admin/", admin.site.urls),
]
