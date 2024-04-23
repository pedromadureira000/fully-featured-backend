from django.db import models
from django.utils import timezone


class Base(models.Model):
    created_at = models.DateTimeField("Created at", default=timezone.now)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True


class ToDo(Base):
    status_choices = (
        (1, "Postponed"),
        (2, "Pendent"),
        (3, "Doing"),
        (4, "Done"),
    )

    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="todos")
    title = models.CharField("Title", max_length=70)
    description = models.CharField("Description", max_length=500)
    completed = models.BooleanField(default=False)
    group = models.ForeignKey("ToDoGroup", on_delete=models.PROTECT)
    status = models.IntegerField(choices=status_choices, default=2)
    due_date = models.DateTimeField("Due date", blank=True, null=True)

    def save(self, *args, **kwargs):
        #  if self.agent != Conversation.objects.get(id=self.id).agent:
            #  self.messages = []
        super().save(*args, **kwargs)

class ToDoGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="todo_groups")
    name = models.CharField("name", max_length=30)

class Journal(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="journals")
    text = models.TextField("Text", max_length=4000)
    group = models.ForeignKey("JournalGroup", on_delete=models.PROTECT)

class JournalGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="journal_groups")
    name = models.CharField("name", max_length=30)

class Note(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="notes")
    title = models.CharField("Title", max_length=70)
    text = models.CharField("Text", max_length=500)
    group = models.ForeignKey("NoteGroup", on_delete=models.PROTECT)

class NoteGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="note_groups")
    name = models.CharField("name", max_length=30)

class Term(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="glossary")
    term = models.CharField("Term", max_length=70)
    definition = models.CharField("Definition", max_length=500)
    group = models.ForeignKey("TermGroup", on_delete=models.PROTECT)

class TermGroup(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="term_groups")
    name = models.CharField("name", max_length=30)
