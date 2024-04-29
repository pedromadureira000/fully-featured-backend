from django.urls import path

from fully_featured.core.views import glossary_get_view, glossary_group_view, glossary_view, journal_get_view, journal_group_view, journal_view, note_get_view, note_group_view, note_view, test_view, todo_get_single_view, todo_get_view, todo_group_view, todo_view, journal_get_single_view, note_get_single_view, glossary_get_single_view

app_name = "core"
urlpatterns = [
    path("test_view", test_view, name="test_view"),
    path("todo_get_view/<int:group_id>", todo_get_view, name="todo_get_view"),
    path("todo_get_single_view/<int:record_id>", todo_get_single_view, name="todo_get_single_view"),
    path("todo_view", todo_view, name="todo_view"),
    path("todo_group_view", todo_group_view, name="todo_group_view"),

    path("journal_get_view/<int:group_id>", journal_get_view, name="journal_get_view"),
    path("journal_get_single_view/<int:record_id>", journal_get_single_view, name="journal_get_single_view"),
    path("journal_view", journal_view, name="journal_view"),
    path("journal_group_view", journal_group_view, name="journal_group_view"),

    path("note_get_view/<int:group_id>", note_get_view, name="note_get_view"),
    path("note_get_single_view/<int:record_id>", note_get_single_view, name="note_get_single_view"),
    path("note_view", note_view, name="note_view"),
    path("note_group_view", note_group_view, name="note_group_view"),

    path("glossary_get_view/<int:group_id>", glossary_get_view, name="glossary_get_view"),
    path("glossary_get_single_view/<int:record_id>", glossary_get_single_view, name="glossary_get_single_view"),
    path("glossary_view", glossary_view, name="glossary_view"),
    path("glossary_group_view", glossary_group_view, name="glossary_group_view"),
]
