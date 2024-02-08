from django.db import models
from django.utils import timezone


class Base(models.Model):
    created_at = models.DateTimeField("Created at", default=timezone.now)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True


class ToDo(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="todos")
    title = models.CharField("Title", max_length=255)
    description = models.CharField("Description", max_length=255)
    completed = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        #  if self.agent != Conversation.objects.get(id=self.id).agent:
            #  self.messages = []
        super().save(*args, **kwargs)


class Journal(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="journals")
    text = models.TextField("Text", max_length=4000)


class Note(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="notes")
    title = models.CharField("Title", max_length=255)
    text = models.CharField("Text", max_length=255)


class Term(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="glossary")
    term = models.CharField("Term", max_length=255)
    definition = models.CharField("Definition", max_length=255)
