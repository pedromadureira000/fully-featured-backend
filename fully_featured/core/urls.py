from django.urls import path

from fully_featured.core.views import test_view, todo_view

app_name = "core"
urlpatterns = [
    path("test_view", test_view, name="test_view"),
    path("todo_view", todo_view, name="todo_view"),
]
