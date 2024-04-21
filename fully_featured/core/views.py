from fully_featured.core.facade import get_paginated_results
from fully_featured.core.models import Journal, JournalGroup, Note, NoteGroup, Term, TermGroup, ToDo, ToDoGroup
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError

from .serializers import JournalGroupSerializer, JournalSerializer, NoteGroupSerializer, NoteSerializer, TermGroupSerializer, TermSerializer, ToDoSerializer, TestSerializer, TodoGroupSerializer


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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            # this is for unpredicted errors
            print(er)
            return Response(data={"error": f"Bad request error"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        return Response("delete method")

@api_view(['GET'])
@login_required
@csrf_exempt
def todo_get_view(request, group_id):
    if request.method == 'GET':
        startingIndex = request.GET.get("startingIndex")
        print(startingIndex)
        model = ToDo
        serializer = ToDoSerializer
        sort_by = '-created_at'
        kwargs = {"user": request.user, "group_id": group_id}
        paginated_results = get_paginated_results(startingIndex, model, serializer, sort_by, **kwargs)
        return Response({
            "result": paginated_results["result"],
            "totalRecords": paginated_results["totalRecords"]
        })

@api_view(['POST', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def todo_view(request):
    if request.method == 'POST':
        try:
            serializer = ToDoSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            todoId = request.data.get('id')
            if not todoId:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = ToDo.objects.get(id=todoId)
            except ToDo.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ToDoSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            todo_id = request.data.get('id')
            if not todo_id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                todo = ToDo.objects.get(id=todo_id)
                todo.delete()
                return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)
            except ToDo.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def todo_group_view(request):
    if request.method == 'GET':
        todo_groups = ToDoGroup.objects.filter(user=request.user).order_by('created_at')
        serializer = TodoGroupSerializer(todo_groups, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = TodoGroupSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            todoId = request.data.get('id')
            if not todoId:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = ToDoGroup.objects.get(id=todoId)
            except ToDoGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = TodoGroupSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                todo = ToDoGroup.objects.get(id=id)
                todo.delete()
                return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)
            except ToDoGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except ProtectedError:
            return Response(data={"error": "You cannot delete this group because it has tasks linked to it."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
@csrf_exempt
def journal_get_view(request, group_id):
    if request.method == 'GET':
        user_todos = Journal.objects.filter(user=request.user, group_id=group_id).order_by('created_at')
        serializer = JournalSerializer(user_todos, many=True)
        return Response(serializer.data)

@api_view(['POST', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def journal_view(request):
    if request.method == 'POST':
        try:
            serializer = JournalSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = Journal.objects.get(id=id)
            except Journal.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = JournalSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def journal_group_view(request):
    if request.method == 'GET':
        todo_groups = JournalGroup.objects.filter(user=request.user).order_by('created_at')
        serializer = JournalGroupSerializer(todo_groups, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = JournalGroupSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            todoId = request.data.get('id')
            if not todoId:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = JournalGroup.objects.get(id=todoId)
            except JournalGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = JournalGroupSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                todo = JournalGroup.objects.get(id=id)
                todo.delete()
                return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)
            except JournalGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
@csrf_exempt
def note_get_view(request, group_id):
    if request.method == 'GET':
        user_todos = Note.objects.filter(user=request.user, group_id=group_id).order_by('created_at')
        serializer = NoteSerializer(user_todos, many=True)
        return Response(serializer.data)

@api_view(['POST', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def note_view(request):
    if request.method == 'POST':
        try:
            serializer = NoteSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def note_group_view(request):
    if request.method == 'GET':
        todo_groups = NoteGroup.objects.filter(user=request.user).order_by('created_at')
        serializer = NoteGroupSerializer(todo_groups, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = NoteGroupSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            todoId = request.data.get('id')
            if not todoId:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = NoteGroup.objects.get(id=todoId)
            except NoteGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = NoteGroupSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                todo = NoteGroup.objects.get(id=id)
                todo.delete()
                return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)
            except NoteGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
@csrf_exempt
def glossary_get_view(request, group_id):
    if request.method == 'GET':
        user_todos = Term.objects.filter(user=request.user, group_id=group_id).order_by('created_at')
        serializer = TermSerializer(user_todos, many=True)
        return Response(serializer.data)

@api_view(['POST', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def glossary_view(request):
    if request.method == 'POST':
        try:
            serializer = TermSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@login_required
@csrf_exempt
def glossary_group_view(request):
    if request.method == 'GET':
        todo_groups = TermGroup.objects.filter(user=request.user).order_by('created_at')
        serializer = TermGroupSerializer(todo_groups, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        try:
            serializer = TermGroupSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PATCH':
        try:
            todoId = request.data.get('id')
            if not todoId:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                order = TermGroup.objects.get(id=todoId)
            except TermGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = TermGroupSerializer(order, data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                todo = TermGroup.objects.get(id=id)
                todo.delete()
                return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)
            except TermGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
