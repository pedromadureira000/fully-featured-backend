from fully_featured.core.facade import send_account_confirmation_email
from fully_featured.user.facade import get_client_ip, get_country_code_from_ip, send_reset_user_password_email
from fully_featured.user.models import UserModel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db import transaction
import sentry_sdk
from fully_featured.settings import DEBUG, STRIPE_PAYMENT_LINK, BASE_URL, STRIPE_PAYMENT_LINK_BR
from django.shortcuts import redirect
from django.http import HttpResponse
import os
from firebase_admin import auth

from .serializers import AuthTokenSerializer, ChangeUserPasswordSerializer, GoogleUserSerializer, ProfileUpdateSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def obtain_auth_token(request):
    if request.user.is_authenticated:
        return Response("User is already authenticated")
    serializer = AuthTokenSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    #  token, created = Token.objects.get_or_create(user=user)
    try:
        token = user.auth_token.key
        return Response({'token': token})
    except Token.DoesNotExist:
        return Response(data={"error": "This user does not have a token."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT'])
@login_required
@csrf_exempt
def user_view(request):
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    if request.method == 'PUT':
        try:
            serializer = ProfileUpdateSerializer(request.user, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er:
            sentry_sdk.capture_exception(er)
            if DEBUG:
                print(f"{er}")
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def sign_up(request):
    try:
        serializer = UserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            with transaction.atomic():
                country = get_country_code_from_ip(get_client_ip(request))
                serializer.validated_data['customer_country'] = country
                instance = serializer.save()
                send_account_confirmation_email(instance.email, instance.auth_token.key, country)
            return Response({"success": "user created. Pls confirm email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as er:
        sentry_sdk.capture_exception(er)
        if DEBUG:
            print(f"{er}")
        return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
@csrf_exempt
def change_password(request):
    try:
        serializer = ChangeUserPasswordSerializer(request.user, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as er:
        sentry_sdk.capture_exception(er)
        if DEBUG:
            print(f"{er}")
        return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def activate_account(request, verification_code):
    country = get_country_code_from_ip(get_client_ip(request))
    try:
        user = UserModel.objects.get(auth_token=verification_code)
        user.is_active = True
        user.save()
        Token.objects.get(user=user).delete()
        Token.objects.create(user=user)
    except UserModel.DoesNotExist:
        return render(
            request,
            "failed_account_verification.html",
            context={'country': country}
        )
    login_url = f"https://mindorganizer.app/login"
    return render(
        request,
        "successful_account_verification.html",
        context={'login_url': login_url, 'country': country}
    )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def reset_password_email(request):
    try:
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email must be provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(data={"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        country = get_country_code_from_ip(get_client_ip(request))
        send_reset_user_password_email(user.email, user.auth_token.key, country)
        return Response(status=status.HTTP_200_OK)
    except Exception as er:
        sentry_sdk.capture_exception(er)
        if DEBUG:
            print(f"{er}")
        return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def reset_password(request, verification_code):
    country = get_country_code_from_ip(get_client_ip(request))
    try:
        user = UserModel.objects.get(auth_token=verification_code)
        token = user.auth_token.key
    except UserModel.DoesNotExist:
        return render(
            request,
            "invalid_reset_password_link.html",
            context={'country': country}
        )
    if request.method == 'GET':
        return render(
            request,
            "reset_password.html",
            context={'token': token, 'country': country}
        )
    if request.method == 'POST':
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        token = request.POST.get("token")
        error_msg = None
        if password != password_confirm:
            if country == "BR":
                error_msg = "As senhas não coincidem. Certifique-se de que ambas as senhas sejam iguais."
            else:
                error_msg = "Passwords do not match. Please ensure that both passwords are equal."  
        if error_msg:
            return render(
                request,
                "reset_password.html",
                {"error": error_msg, 'country': country},
                status=400
            )
        else:
            try:
                with transaction.atomic():
                    user.set_password(password)
                    user.save()
                    Token.objects.get(user=user).delete()
                    Token.objects.create(user=user)
                return render(
                    request,
                    "reset_password_success.html",
                    {'country': country},
                    status=200
                )
            except Exception as er:
                sentry_sdk.capture_exception(er)
                if DEBUG:
                    print('========================> er: ',er )
                if country == "BR":
                    error_msg = "Um erro inesperado ocorreu. Tente novamente mais tarde."
                else:
                    error_msg = "An unexpected error occurred. Try again later."
                return render(
                    request,
                    "reset_password.html",
                    {"error": error_msg, 'country': country},
                    status=500
                )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def get_or_create_account_with_google(request):
    try:
        email = request.data.get("email")
        fcmToken = request.data.get("fcmToken")
        id_token = request.data.get('idToken')
        access_token = request.data.get('accessToken')
        display_name = request.data.get('displayName')

        # Verify ID token using Firebase Admin SDK
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            # ID token is valid, proceed with user creation/login
        except Exception as error:
            # Handle invalid/expired ID token ???????????????????????????//
            if DEBUG:
                print('========================> error: ',error )
            else:
                sentry_sdk.capture_exception(error)
            return Response("Invalid google authentication token.", status=status.HTTP_403_FORBIDDEN)

        try:
            user = UserModel.objects.get(email=email)
            if fcmToken and user.fcmToken != fcmToken:
                user.fcmToken = fcmToken
                user.save()
            return Response({"token": user.auth_token.key, "created": False}, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            serializer = GoogleUserSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['customer_country'] = get_country_code_from_ip(get_client_ip(request))
                instance = serializer.save()
                return Response({"token": instance.auth_token.key, "created": True}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as er:
        sentry_sdk.capture_exception(er)
        if DEBUG:
            print(f"{er}")
        return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@login_required
@csrf_exempt
def delete_user_view(request):
    try:
        user = UserModel.objects.get(id=request.user.id)
        user.delete()
        return Response({"success": "user deleted"}, status=status.HTTP_200_OK)
    except UserModel.DoesNotExist:
        return Response(data={"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def peter_saas_root(request):
    country = get_country_code_from_ip(get_client_ip(request))
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
            return render(
                request,
                "home.html",
                context={
                    'BASE_URL': BASE_URL,
                    'STRIPE_PAYMENT_LINK': STRIPE_PAYMENT_LINK,
                    'STRIPE_PAYMENT_LINK_BR': STRIPE_PAYMENT_LINK_BR,
                    'country': country
                }
            )
    return redirect("https://mindorganizer.app")

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def mind_organizer_landing_page(request):
    country = get_country_code_from_ip(get_client_ip(request))
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
        return render(
            request,
            "mind_organizer_landing_page.html",
            context={
                'BASE_URL': BASE_URL,
                'STRIPE_PAYMENT_LINK': STRIPE_PAYMENT_LINK,
                'STRIPE_PAYMENT_LINK_BR': STRIPE_PAYMENT_LINK_BR,
                'country': country
            }
        )
    return redirect("https://mindorganizer.app")

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def privacy_policy(request):
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
        country = get_country_code_from_ip(get_client_ip(request))
        return render(
            request,
            "privacy_policy.html",
            context={'country': country}
        )
    return redirect("https://mindorganizer.app")


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def terms_of_use(request):
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
        country = get_country_code_from_ip(get_client_ip(request))
        return render(
            request,
            "terms_of_use.html",
            context={'country': country}
        )
    return redirect("https://mindorganizer.app")


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def download_apk(request):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))
    file_path = os.path.join(PROJECT_ROOT, 'downloads/', 'app-release.apk')  # Adjust based on model or media storage

    if not os.path.exists(file_path):
        return Response(data={"error": "File was not found."},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="app-release.apk"'
            return response
    except Exception as er:
        sentry_sdk.capture_exception(er)
        if DEBUG:
            print(f"{er}")
        return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
@csrf_exempt
def get_country(request):
    try:
        country = get_country_code_from_ip(get_client_ip(request))
        return Response({"country_code": country}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"country_code": "XX"}, status=status.HTTP_200_OK)
