from fully_featured.core.facade import send_account_confirmation_email
from fully_featured.user.facade import send_reset_user_password_email
from fully_featured.user.models import UserModel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from fully_featured.settings import BASE_URL
from django.db import transaction
import sentry_sdk
from fully_featured.settings import DEBUG, STRIPE_PAYMENT_LINK
from django.shortcuts import redirect
from django.http import HttpResponse
import os

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
                instance = serializer.save()
                language = "en"
                http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
                if "pt" in http_accept_language:
                    language = "pt"
                send_account_confirmation_email(instance.email, instance.auth_token.key, language)
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
    language = "en"
    http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if "pt" in http_accept_language:
        language = "pt"
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
            context={'lang': language}
        )
    login_url = f"{BASE_URL}/login"
    return render(
        request,
        "successful_account_verification.html",
        context={'login_url': login_url, 'lang': language}
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
        language = "en"
        http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        if "pt" in http_accept_language:
            language = "pt"
        send_reset_user_password_email(user.email, user.auth_token.key, language)
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
    language = "en"
    http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if "pt" in http_accept_language:
        language = "pt"
    try:
        user = UserModel.objects.get(auth_token=verification_code)
        token = user.auth_token.key
    except UserModel.DoesNotExist:
        return render(
            request,
            "invalid_reset_password_link.html",
            context={'lang': language}
        )
    if request.method == 'GET':
        return render(
            request,
            "reset_password.html",
            context={'token': token, 'lang': language}
        )
    if request.method == 'POST':
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        token = request.POST.get("token")
        error_msg = None
        if password != password_confirm:
            if language == "en":
                error_msg = "Passwords do not match. Please ensure that both passwords are equal."  
            else:
                error_msg = "As senhas não coincidem. Certifique-se de que ambas as senhas sejam iguais."
        if error_msg:
            return render(
                request,
                "reset_password.html",
                {"error": error_msg, 'lang': language},
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
                    {'lang': language},
                    status=200
                )
            except Exception as er:
                sentry_sdk.capture_exception(er)
                if DEBUG:
                    print('========================> er: ',er )
                if language == "en":
                    error_msg = "An unexpected error occurred. Try again later."
                else:
                    error_msg = "Um erro inesperado ocorreu. Tente novamente mais tarde."
                return render(
                    request,
                    "reset_password.html",
                    {"error": error_msg, 'lang': language},
                    status=500
                )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def get_or_create_account_with_google(request):
    try:
        try:
            email = request.data.get("email")
            fcmToken = request.data.get("fcmToken")
            user = UserModel.objects.get(email=email)
            if fcmToken and user.fcmToken != fcmToken:
                user.fcmToken = fcmToken
                user.save()
            return Response({"token": user.auth_token.key, "created": False}, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            pass
        serializer = GoogleUserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
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
    language = "en"
    http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if "pt" in http_accept_language:
        language = "pt"
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
            return render(
                request,
                "home.html",
                context={
                    'lang': language, 'BASE_URL': BASE_URL, 'STRIPE_PAYMENT_LINK': STRIPE_PAYMENT_LINK
                }
            )
    return redirect("app_menu")

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def mind_organizer_landing_page(request):
    language = "en"
    http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if "pt" in http_accept_language:
        language = "pt"
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
        return render(
            request,
            "mind_organizer_landing_page.html",
            context={
                'lang': language, 'BASE_URL': BASE_URL, 'STRIPE_PAYMENT_LINK': STRIPE_PAYMENT_LINK
            }
        )
    return redirect("app_menu")

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def privacy_policy(request):
    language = "en"
    http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if "pt" in http_accept_language:
        language = "pt"
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
        return render(
            request,
            "privacy_policy.html",
            context={'lang': language}
        )
    return redirect("app_menu")


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def terms_of_use(request):
    language = "en"
    http_accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    if "pt" in http_accept_language:
        language = "pt"
    if DEBUG or request.get_host() == "petersoftwarehouse.com":
        return render(
            request,
            "terms_of_use.html",
            context={'lang': language}
        )
    return redirect("app_menu")


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
