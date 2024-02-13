from fully_featured.core.models import Journal, Note, Term, ToDo
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .serializers import JournalSerializer, NoteSerializer, TermSerializer, ToDoSerializer, TestSerializer


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
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
    if request.method == 'DELETE':
        return Response("delete method")


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def todo_view(request):
    if not request.user.is_authenticated:
        return Response("(user.is_authenticated) it should have already be handled. What's going on?")
    if request.method == 'GET':
        user_todos = ToDo.objects.filter(user=request.user).order_by('created_at')
        serializer = ToDoSerializer(user_todos, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = ToDoSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            todoId = request.data.get('id')
            if not todoId:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = ToDo.objects.get(id=todoId)
            except ToDo.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ToDoSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            todo_id = request.data.get('id')
            if not todo_id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                todo = ToDo.objects.get(id=todo_id)
                todo.delete()
                return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)
            except ToDo.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def journal_view(request):
    if request.method == 'GET':
        journals = Journal.objects.filter(user=request.user).order_by('created_at')
        serializer = JournalSerializer(journals, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = JournalSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Journal.objects.get(id=id)
            except Journal.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = JournalSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = Journal.objects.get(id=id)
                instance.delete()
                return Response({'message': 'Journal deleted successfully'}, status=status.HTTP_200_OK)
            except Journal.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def note_view(request):
    if request.method == 'GET':
        registers = Note.objects.filter(user=request.user).order_by('created_at')
        serializer = NoteSerializer(registers, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = NoteSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Note.objects.get(id=id)
            except Note.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = NoteSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = Note.objects.get(id=id)
                instance.delete()
                return Response({'message': 'Note deleted successfully'}, status=status.HTTP_200_OK)
            except Note.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def glossary_view(request):
    if request.method == 'GET':
        registers = Term.objects.filter(user=request.user).order_by('created_at')
        serializer = TermSerializer(registers, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = TermSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Term.objects.get(id=id)
            except Term.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = TermSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'validation error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'validation error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = Term.objects.get(id=id)
                instance.delete()
                return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
            except Term.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
