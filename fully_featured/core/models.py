from django.db import models
from django.utils import timezone


class Base(models.Model):
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)

    class Meta:
        abstract = True


class ToDo(Base):
    user = models.ForeignKey("user.UserModel", on_delete=models.CASCADE, related_name="todos")
    title = models.CharField("Título", max_length=255, unique=True)
    description = models.CharField("Descrição", max_length=255)
    completed = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        #  if self.agent != Conversation.objects.get(id=self.id).agent:
            #  self.messages = []
        super().save(*args, **kwargs)
