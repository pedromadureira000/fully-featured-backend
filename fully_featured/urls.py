from django.urls import path, include
from django.contrib import admin
from django.views.static import serve
import os
from fully_featured.user.views import (
    activate_account,
    privacy_policy,
    reset_password,
    landing_page,
    terms_of_use
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER_WEB_APP = os.path.join(BASE_DIR, 'flutter_web_app')

def flutter_redirect(request, resource):
    return serve(request, resource, FLUTTER_WEB_APP)

flutter_app_routes = [
    path("login", lambda r: flutter_redirect(r, 'index.html')),
    path("profile", lambda r: flutter_redirect(r, 'index.html')),
    path("sign_up", lambda r: flutter_redirect(r, 'index.html')),
    path("reset_password_email", lambda r: flutter_redirect(r, 'index.html')),
    path("menu", lambda r: flutter_redirect(r, 'index.html'), name="app_menu"),
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
    path("", landing_page, name="landing_page"),
    path("privacy_policy", privacy_policy, name="privacy_policy"),
    path("terms_of_use", terms_of_use, name="terms_of_use"),
    #  path("", lambda r: flutter_redirect(r, 'index.html')),
    *flutter_app_routes,
    path("activate_account/<str:verification_code>", activate_account, name="activate_account"),
    path("reset_password/<str:verification_code>", reset_password, name="reset_password"),
    path("api/", include("fully_featured.core.urls")),
    path("api/user/", include("fully_featured.user.urls")),
    path("admin/", admin.site.urls),
    path("<path:resource>", flutter_redirect),
]
