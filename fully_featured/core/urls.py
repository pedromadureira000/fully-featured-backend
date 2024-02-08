from django.urls import path

from fully_featured.core.views import glossary_view, journal_view, note_view, test_view, todo_view

app_name = "core"
urlpatterns = [
    path("test_view", test_view, name="test_view"),
    path("todo_view", todo_view, name="todo_view"),
    path("journal_view", journal_view, name="journal_view"),
    path("note_view", note_view, name="note_view"),
    path("glossary_view", glossary_view, name="glossary_view"),
]
