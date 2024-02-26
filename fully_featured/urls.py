from django.urls import path, include
from django.contrib import admin
from django.views.static import serve
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER_WEB_APP = os.path.join(BASE_DIR, 'flutter_web_app')

def flutter_redirect(request, resource):
    return serve(request, resource, FLUTTER_WEB_APP)

flutter_app_routes = [
    path("login", lambda r: flutter_redirect(r, 'index.html')),
    path("profile", lambda r: flutter_redirect(r, 'index.html')),
    path("sign_up", lambda r: flutter_redirect(r, 'index.html')),
    path("menu", lambda r: flutter_redirect(r, 'index.html')),
    path("todo", lambda r: flutter_redirect(r, 'index.html')),
    path("todo_create", lambda r: flutter_redirect(r, 'index.html')),
    path("journal", lambda r: flutter_redirect(r, 'index.html')),
    path("journal_create", lambda r: flutter_redirect(r, 'index.html')),
    path("note", lambda r: flutter_redirect(r, 'index.html')),
    path("note_create", lambda r: flutter_redirect(r, 'index.html')),
    path("glossary", lambda r: flutter_redirect(r, 'index.html')),
    path("glossary_create", lambda r: flutter_redirect(r, 'index.html')),
]

urlpatterns = [
    path("", lambda r: flutter_redirect(r, 'index.html')),
    *flutter_app_routes,
    path("api/", include("fully_featured.core.urls")),
    path("api/user/", include("fully_featured.user.urls")),
    path("admin/", admin.site.urls),
    path("<path:resource>", flutter_redirect),
]
