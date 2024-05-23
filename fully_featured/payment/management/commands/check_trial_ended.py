from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

# Calculate the date 30 days ago from today

from fully_featured.user.models import UserModel

class Command(BaseCommand):
    help = "check_trial_ended"

    def handle(self, *args, **options):
        check_trial_ended()

def check_trial_ended():
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trial_users_older_than_30_days = UserModel.objects.filter(
        subscription_status=1,
        created_at__lt=thirty_days_ago
    )
    for user in trial_users_older_than_30_days:
        user.subscription_status = 2
    UserModel.objects.bulk_update(trial_users_older_than_30_days, ["subscription_status"]);

