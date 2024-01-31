from fully_featured.core.models import ToDo
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .serializers import ToDoSerializer, TestSerializer


@api_view(['POST', 'GET'])
@permission_classes([permissions.AllowAny])
def test_view(request):
    if not request.user.is_authenticated:
        return Response("User is not authenticated. But this was set with 'permissions.AllowAny'")
    if request.method == 'GET':
        return Response({'status': 'get method seems fine for me'})
    if request.method == 'POST':
        try:
            serializer = TestSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                return Response({'data sent': f'everything is fine'})
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            # this is for unpredicted errors
            print(er)
            return Response(data={"error": f"Bad request error"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
#  @permission_classes([permissions.AllowAny])
#  @login_required
#  @csrf_exempt
def todo_view(request):
    if not request.user.is_authenticated:
        return Response("(user.is_authenticated) it should have already be handled. What's going on?")
    if request.method == 'GET':
        user_todos = ToDo.objects.filter(user=request.user)
        serializer = ToDoSerializer(user_todos, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = ToDoSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user # is it possible?
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
