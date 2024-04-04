from django.db.models.fields.json import json
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

from .serializers import AuthTokenSerializer, ChangeUserPasswordSerializer, GoogleUserSerializer, UserSerializer


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


@api_view(['GET'])
@login_required
@csrf_exempt
def user_view(request):
    if request.method == 'GET':
        try:
            user = UserModel.objects.get(id=request.user.id)
        except UserModel.DoesNotExist:
            return Response(data={"error": "Something weird happened. This is not supposed to throw error"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def sign_up(request):
    try:
        serializer = UserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            with transaction.atomic():
                instance = serializer.save()
                send_account_confirmation_email(instance.email, instance.auth_token.key)
            return Response({"success": "user created. Pls confirm email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as er:
        print(f"{er}")
        return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        try:
            serializer = ChangeUserPasswordSerializer(request.user, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er:
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def activate_account(request, verification_code):
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
        )
    #  try:
        #  send_account_verified_with_success_email(user.email)
    #  except Exception as er:
        #  print(f"{er}")
    login_url = f"{BASE_URL}/login"
    return render(
        request,
        "successful_account_verification.html",
        context={'login_url': login_url}
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
        send_reset_user_password_email(user.email, user.auth_token.key)
        return Response(status=status.HTTP_200_OK)
    except Exception as er:
        print(er)
        return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def reset_password(request, verification_code):
    try:
        user = UserModel.objects.get(auth_token=verification_code)
        token = user.auth_token.key
    except UserModel.DoesNotExist:
        return render(
            request,
            "invalid_reset_password_link.html",
        )
    if request.method == 'GET':
        return render(
            request,
            "reset_password.html",
            context={'token': token}
        )
    if request.method == 'POST':
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        token = request.POST.get("token")
        error_msg = None
        if password != password_confirm:
            error_msg = "Passwords do not match. Please ensure that both passwords are iqual."
        if error_msg:
            return render(
                request,
                "reset_password.html",
                {"error": error_msg},
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
                    status=200
                )
            except Exception as er:
                return render(
                    request,
                    "reset_password.html",
                    {"error": "Something went wrong."},
                    status=500
                )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def get_or_create_account_with_google(request):
    try:
        try:
            email = request.data.get("email")
            user = UserModel.objects.get(email=email)
            return Response({"token": user.auth_token.key, "created": False}, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            pass
        serializer = GoogleUserSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            with transaction.atomic():
                instance = serializer.save()
                #  send_account_confirmation_email(instance.email, instance.auth_token.key)
                return Response({"token": instance.auth_token.key, "created": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as er:
        print(f"{er}")
        return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
