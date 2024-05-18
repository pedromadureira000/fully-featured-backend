from django.urls import path, include
from django.contrib import admin
from django.views.static import serve
import os
from fully_featured.user.views import (
    activate_account,
    mind_organizer_landing_page,
    privacy_policy,
    reset_password,
    peter_saas_root,
    terms_of_use,
    download_apk,
)
from fully_featured.settings import DEBUG
from django.shortcuts import redirect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUTTER_WEB_APP = os.path.join(BASE_DIR, 'flutter_web_app')

def flutter_redirect(request, resource):
    return serve(request, resource, FLUTTER_WEB_APP)

flutter_app_routes = [
    path("login", lambda r: get_app_route(r)),
    path("profile", lambda r: get_app_route(r)),
    path("sign_up", lambda r: get_app_route(r)),
    path("reset_password_email", lambda r: get_app_route(r)),
    path("menu", lambda r: get_app_route(r), name="app_menu"),
    path("todo", lambda r: get_app_route(r)),
    path("todo_create", lambda r: get_app_route(r)),
    path("journal", lambda r: get_app_route(r)),
    path("journal_create", lambda r: get_app_route(r)),
    path("note", lambda r: get_app_route(r)),
    path("note_create", lambda r: get_app_route(r)),
    path("glossary", lambda r: get_app_route(r)),
    path("glossary_create", lambda r: get_app_route(r)),
]

urlpatterns = [
    path("", peter_saas_root, name="peter_saas_root"),
    path("mind-organizer", mind_organizer_landing_page, name="mind_organizer_landing_page"),
    path("privacy_policy", privacy_policy, name="privacy_policy"),
    path("terms_of_use", terms_of_use, name="terms_of_use"),
    *flutter_app_routes,
    path("activate_account/<str:verification_code>", activate_account, name="activate_account"),
    path("reset_password/<str:verification_code>", reset_password, name="reset_password"),
    path("api/", include("fully_featured.core.urls")),
    path("api/user/", include("fully_featured.user.urls")),
    path("api/payment/", include("fully_featured.payment.urls")),
    path("admin/", admin.site.urls),
    path("download_apk", download_apk, name="download_apk"),
    path("<path:resource>", flutter_redirect),
]

def get_app_route(r):
    if DEBUG or r.get_host() == "app.petersoftwarehouse.com":
        return flutter_redirect(r, 'index.html')
    return redirect("peter_saas_root")
