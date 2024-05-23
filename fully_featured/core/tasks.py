from celery import shared_task
from fully_featured.core.facade import send_fcm_notification as _send_fcm_notification
import sentry_sdk
from fully_featured.settings import (
    TASK__MAX_RETRIES,
    TASK__DEFAULT_RETRY_DELAY,
)


@shared_task(bind=True)
def send_fcm_notification(self, fcmToken, title, body):
    try:
        _send_fcm_notification(fcmToken, title, body)
    except Exception as exc:
        print(f"Error fcm notification to fcmToken {fcmToken[0:15]}: {exc}")
        sentry_sdk.capture_message(
            f"Something went wrong then trying to send fcm notification fcmToken {fcmToken[0:15]}."
        )
        raise self.retry(exc=exc, countdown=TASK__DEFAULT_RETRY_DELAY,
                         max_retries=TASK__MAX_RETRIES)
    return "Done"
