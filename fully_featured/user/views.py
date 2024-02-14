from django.conf import settings
from fully_featured.user.models import UserModel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .serializers import AuthTokenSerializer, ChangeUserPasswordSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
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
def sign_in(request):
    if request.method == 'POST':
        try:
            serializer = UserSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
def change_password(request):
    if request.method == 'POST':
        try:
            serializer = ChangeUserPasswordSerializer(request.user, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er:
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
