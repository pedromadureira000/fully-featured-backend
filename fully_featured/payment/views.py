from django.http import HttpResponse
from fully_featured.payment.facade import send_account_created_email_with_change_password_link, send_subscription_canceled_email, send_subscription_success_email
from fully_featured.settings import STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
import stripe
from datetime import datetime
import sentry_sdk

from fully_featured.user.models import UserModel

stripe.api_key = STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = STRIPE_SECRET_KEY
    endpoint_secret = STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'invoice.paid':
        customer_stripe_id = event['data']['object']['customer'],
        billing_reason = event['data']['object']['billing_reason'],
        customer_email = event['data']['object']['customer_email'],
        customer_name = event['data']['object']['customer_name'],
        customer_phone = event['data']['object']['customer_phone'],
        customer_country = event['data']['object']['customer_address']['country'],
        lang = "pt" if customer_country == "BR" else "en"
        try:
            user = UserModel.objects.get(email=customer_email)
            if user.subscription_status != 3:
                user.subscription_status = 3
                user.subscription_started_at = datetime.now()
                user.customer_stripe_id=customer_stripe_id
                user.lang_for_communication=lang
                user.save()
                send_subscription_success_email(user, lang)
            else:
                pass # Do nothing. It's just another payment
        except UserModel.DoesNotExist:
            password = "aljdfkajsfafiajsdlfuweuflaj"
            username_field = customer_email
            user = UserModel.objects.create_user(
                username_field,
                password,
                name=customer_name,
                whatsapp=customer_phone,
                subscription_status=3,
                subscription_started_at = datetime.now(),
                customer_stripe_id=customer_stripe_id,
                lang_for_communication=lang,
            )
            send_account_created_email_with_change_password_link(user, lang)

    if event['type'] == 'customer.subscription.updated':
        customer_stripe_id = event['data']['object']['customer'],
        cancellation_details = event['data']['object']['cancellation_details'], # reason
        canceled_at = event['data']['object']['canceled_at'],
        subscription_was_cancelled = canceled_at
        try:
            user = UserModel.objects.get(customer_stripe_id=customer_stripe_id)
            subscription_was_renewed = not canceled_at and user.subscription_status == 5
            if subscription_was_cancelled: # heuristics
                user.subscription_status = 5
                user.subscription_canceled_at = datetime.now()
                user.save()
                send_subscription_canceled_email(user, user.lang_for_communication)
            elif subscription_was_renewed:  # heuristics
                user.subscription_status = 3
                user.subscription_canceled_at = None
                user.subscription_started_at = datetime.now()
                user.save()
                send_subscription_renewd_email(user, user.lang_for_communication)
        except UserModel.DoesNotExist as er:
            if subscription_was_cancelled:
                with sentry_sdk.push_scope() as scope:
                    scope.set_context("additional_info", {
                        "custom_message": "Could not found customer",
                        "customer_stripe_id": customer_stripe_id,
                        "details": "Could not found customer on stripe event 'customer.subscription.updated'. This was thrown becouse 'subscription_was_cancelled' was true"
                    })
                    sentry_sdk.capture_exception(er)

    if event['type'] == 'customer.subscription.deleted':
        customer_stripe_id = event['data']['object']['customer'],
        canceled_at = event['data']['object']['canceled_at'],
        try:
            user = UserModel.objects.get(customer_stripe_id=customer_stripe_id)
            subscription_was_cancelled = user.subscription_status != 5 and canceled_at
            if subscription_was_cancelled: # heuristics
                user.subscription_status = 5
                user.subscription_canceled_at = datetime.now()
                user.save()
                send_subscription_canceled_email(user, user.lang_for_communication)
        except UserModel.DoesNotExist as er:
            with sentry_sdk.push_scope() as scope:
                scope.set_context("additional_info", {
                    "custom_message": "Could not found customer",
                    "customer_stripe_id": customer_stripe_id,
                    "details": "Could not found customer on stripe event 'customer.subscription.deleted'"
                })
                sentry_sdk.capture_exception(er)
    return HttpResponse(status=200)

    #  if event['type'] == 'payment_intent.payment_failed':
        #  print("Payment failed.")
    #  if event['type'] == 'customer.updated': # updated user
