from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from fully_featured.core.tasks import send_fcm_notification
from fully_featured.core.models import ToDo

# Calculate the date 30 days ago from today

from fully_featured.user.models import UserModel

class Command(BaseCommand):
    help = "send_task_notifications"

    def handle(self, *args, **options):
        send_task_notifications()

def send_task_notifications():
    now = datetime.utcnow()
    five_minutes_from_now = now + timedelta(minutes=5)

    upcoming_tasks = ToDo.objects.select_related("user__fcmToken").filter(
        notify_on_due=True,
        due_date__gte=now,
        due_date__lt=five_minutes_from_now
    )
    for task in upcoming_tasks:
        title = task.title[0:60] + "..." if len(task.title) > 60 else task.title
        body = task.description[0:120] + "..." if len(task.description) > 120 else task.description
        send_fcm_notification.delay(task.user.fcmToken, title, body)
    #  UserModel.objects.bulk_update(trial_users_older_than_30_days, ["subscription_status"]);

