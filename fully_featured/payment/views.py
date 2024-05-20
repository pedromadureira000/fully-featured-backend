from django.http import HttpResponse
from fully_featured.payment.facade import send_account_created_email_with_change_password_link, send_payment_failed_email, send_subscription_canceled_email, send_subscription_success_email
from fully_featured.settings import STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
import stripe
from datetime import datetime
import sentry_sdk
from rest_framework.response import Response

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
        return Response({"ValueError": f"{e}"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response({"stripe.error.SignatureVerificationError": f"{e}"}, status=400)

    if event['type'] == 'invoice.paid':
        customer_stripe_id = event['data']['object']['customer']
        billing_reason = event['data']['object']['billing_reason']
        customer_email = event['data']['object']['customer_email']
        customer_name = event['data']['object']['customer_name']
        customer_phone = event['data']['object']['customer_phone']
        customer_country = event['data']['object']['customer_address']['country']
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
                return Response({"success": "Already existant account subscribed or Re-subscribed."})
            else:
                return Response({"success": "Just another payment"})
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
            return Response({"success": "customer subscribed, account was created, and email with change password link was sent"})

    if event['type'] == 'customer.subscription.updated':
        customer_stripe_id = event['data']['object']['customer']
        #  cancellation_details = event['data']['object']['cancellation_details'] # it's always dict
        #  status = event['data']['object']['status'] # "past_due" if payment failed. but will be retryed
        previous_attributes = event['data']['object']['previous_attributes']
                            #  "previous_attributes": {
                              #  "status": "active"
                            #  }
        canceled_at = event['data']['object']['canceled_at']
        try:
            user = UserModel.objects.get(customer_stripe_id=customer_stripe_id)
            subscription_was_renewed = not canceled_at and user.subscription_status == 5 # TODO not sure about this heuristic
            subscription_was_cancelled = canceled_at and user.subscription_status != 5
            if subscription_was_cancelled: # heuristics
                # TODO do something when user cancell it? Like send an email trying to make him change his mind
                return Response({
                    "success": "subscription_was_cancelled. But status is still active becouse it has to reach the end of billed month.",
                    "previous_attributes": previous_attributes
                })
            elif subscription_was_renewed:  # working heuristics
                user.subscription_status = 3
                user.subscription_canceled_at = None
                user.subscription_started_at = datetime.now()
                user.save()
                send_subscription_success_email(user, user.lang_for_communication)
                return Response({
                    "success": "subscription_was_renewed",
                    "previous_attributes": previous_attributes
                })
            return Response({
                "success": "customer.subscription.updated -- but did not changed subscription on backend",
                "previous_attributes": previous_attributes
            })
        except UserModel.DoesNotExist as er:
            # TODO understand this cases
            with sentry_sdk.push_scope() as scope:
                scope.set_context("additional_info", {
                    "custom_message": "Could not found customer",
                    "customer_stripe_id": customer_stripe_id,
                    "details": "customer.subscription.updated, but user was not found. What happened? Maybe user updated his stripe account?"
                })
                sentry_sdk.capture_exception(er)
            return Response({
                "success": "customer.subscription.updated, but user was not found. What happened? Maybe user updated his stripe account?",
                "previous_attributes": previous_attributes
            })
    if event['type'] == 'customer.subscription.deleted':
        customer_stripe_id = event['data']['object']['customer']
        canceled_at = event['data']['object']['canceled_at']
        try:
            user = UserModel.objects.get(customer_stripe_id=customer_stripe_id)
            user.subscription_status = 5
            user.subscription_canceled_at = datetime.now()
            user.save()
            send_subscription_canceled_email(user, user.lang_for_communication)
            return Response({"success": "subscription_was_cancelled on customer.subscription.deleted"})
        except UserModel.DoesNotExist as er:
            with sentry_sdk.push_scope() as scope:
                scope.set_context("additional_info", {
                    "custom_message": "Could not found customer",
                    "customer_stripe_id": customer_stripe_id,
                    "details": "subscription_was_cancelled but user was not found. This should not happen"
                })
                sentry_sdk.capture_exception(er)
            return Response({"error": "subscription_was_cancelled but user was not found. This should not happen"})

    if event['type'] == 'invoice.payment_failed':
        customer_email = event['data']['object']['customer_email']
        billing_reason = event['data']['object']['billing_reason']
            #  if user.subscription_status not in [4, 5]  :
                #  user.subscription_status = 4
                #  user.subscription_failed_at = datetime.now()
                #  user.save()
        if billing_reason != "subscription_create":
            try:
                user = UserModel.objects.get(email=customer_email)
                send_payment_failed_email(user, user.lang_for_communication)
                return Response({"success": "invoice.payment_failed"})
            except UserModel.DoesNotExist as er:
                with sentry_sdk.push_scope() as scope:
                    scope.set_context("additional_info", {
                        "custom_message": "Could not found customer",
                        "customer_email": customer_email,
                        "details": "Could not found customer on stripe event 'invoice.payment_failed'"
                    })
                    sentry_sdk.capture_exception(er)
                return Response({"success": "invoice.payment_failed but user was not found. Maybe this is not a bug, becouse user without account might not manage to make subscription in his first try"})
        return Response({"success": f"invoice.payment_failed; billing_reason: {billing_reason}"})
    return HttpResponse(status=200)
