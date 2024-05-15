from django.db import models
from django.utils import timezone


status_choices = (
    (1, "Postponed"),
    (2, "Pendent"),
    (3, "Doing"),
    (4, "Done"),
)
priority_choices = (
    (1, "Urgent"),
    (2, "High"),
    (3, "Normal"),
    (4, "Low"),
)

class Base(models.Model):
    created_at = models.DateTimeField("Created at", default=timezone.now)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True


class ToDo(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="todos")
    title = models.CharField("Title", max_length=135)
    description = models.CharField("Description", max_length=551)
    completed = models.BooleanField(default=False)
    group = models.ForeignKey("ToDoGroup", on_delete=models.PROTECT, related_name="group_records")
    status = models.IntegerField(choices=status_choices, default=2)
    priority = models.IntegerField(choices=priority_choices, default=3)
    due_date = models.DateTimeField("Due date", blank=True, null=True)
    done_date = models.DateTimeField("Done date", blank=True, null=True)

    def save(self, *args, **kwargs):
        #  if self.agent != Conversation.objects.get(id=self.id).agent:
            #  self.messages = []
        super().save(*args, **kwargs)

class ToDoGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="todo_groups")
    name = models.CharField("name", max_length=30)
    order = models.IntegerField(blank=True, null=True)
    filter_status = models.IntegerField(choices=status_choices, blank=True, null=True)
    filter_priority = models.IntegerField(choices=priority_choices, blank=True, null=True)

class Journal(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="journals")
    text = models.TextField("Text")
    group = models.ForeignKey("JournalGroup", on_delete=models.PROTECT, related_name="group_records")

class JournalGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="journal_groups")
    name = models.CharField("name", max_length=30)
    order = models.IntegerField(blank=True, null=True)

class Note(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="notes")
    title = models.TextField("Title")
    text = models.TextField("Text")
    group = models.ForeignKey("NoteGroup", on_delete=models.PROTECT, related_name="group_records")
    pinned = models.BooleanField(default=False)

class NoteGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="note_groups")
    name = models.CharField("name", max_length=30)
    order = models.IntegerField(blank=True, null=True)

class Term(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="glossary")
    term = models.TextField("Term")
    definition = models.TextField("Definition")
    group = models.ForeignKey("TermGroup", on_delete=models.PROTECT, related_name="group_records")

class TermGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="term_groups")
    name = models.CharField("name", max_length=30)
    order = models.IntegerField(blank=True, null=True)
