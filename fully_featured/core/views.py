from fully_featured.core.facade import get_paginated_results, reorder_group_after_delete
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
        model = ToDo
        serializer = ToDoSerializer
        sort_by = '-created_at'
        kwargs = {"group_id": group_id}
        paginated_results = get_paginated_results(request.user, startingIndex, model, serializer, sort_by, **kwargs)
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
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                record = ToDo.objects.get(user_id=request.user.id, id=id)
            except ToDo.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ToDoSerializer(record, data=request.data, context={"request": request})
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
                todo = ToDo.objects.get(user_id=request.user.id, id=todo_id)
                todo.delete()
                return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
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
        groups = ToDoGroup.objects.filter(user_id=request.user.id).order_by('order')
        serializer = TodoGroupSerializer(groups, many=True)
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
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                group = ToDoGroup.objects.get(user_id=request.user.id, id=id)
            except ToDoGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TodoGroupSerializer(group, data=request.data, context={"request": request})
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
                group = ToDoGroup.objects.get(id=id, user_id=request.user.id)
                group.delete()
                reorder_group_after_delete(request.user, ToDoGroup)
                return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
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
        startingIndex = request.GET.get("startingIndex")
        model = Journal
        serializer = JournalSerializer
        sort_by = '-created_at'
        kwargs = {"group_id": group_id}
        paginated_results = get_paginated_results(request.user, startingIndex, model, serializer, sort_by, **kwargs)
        return Response({
            "result": paginated_results["result"],
            "totalRecords": paginated_results["totalRecords"]
        })


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
                record = Journal.objects.get(user_id=request.user.id, id=id)
            except Journal.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = JournalSerializer(record, data=request.data, context={"request": request})
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
                instance = Journal.objects.get(user_id=request.user.id, id=id)
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
        groups = JournalGroup.objects.filter(user_id=request.user.id).order_by('order')
        serializer = JournalGroupSerializer(groups, many=True)
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
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                group = JournalGroup.objects.get(user_id=request.user.id, id=id)
            except JournalGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = JournalGroupSerializer(group, data=request.data, context={"request": request})
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
                group = JournalGroup.objects.get(id=id, user_id=request.user.id)
                group.delete()
                reorder_group_after_delete(request.user, JournalGroup)
                return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
            except JournalGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except ProtectedError:
            return Response(data={"error": "You cannot delete this group because it has records linked to it."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
@csrf_exempt
def note_get_view(request, group_id):
    if request.method == 'GET':
        startingIndex = request.GET.get("startingIndex")
        model = Note
        serializer = NoteSerializer
        sort_by = '-created_at'
        kwargs = {"group_id": group_id}
        paginated_results = get_paginated_results(request.user, startingIndex, model, serializer, sort_by, **kwargs)
        return Response({
            "result": paginated_results["result"],
            "totalRecords": paginated_results["totalRecords"]
        })

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
                record = Note.objects.get(user_id=request.user.id, id=id)
            except Note.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = NoteSerializer(record, data=request.data, context={"request": request})
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
                instance = Note.objects.get(user_id=request.user.id, id=id)
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
        groups = NoteGroup.objects.filter(user_id=request.user.id).order_by('order')
        serializer = NoteGroupSerializer(groups, many=True)
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
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                group = NoteGroup.objects.get(user_id=request.user.id, id=id)
            except NoteGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = NoteGroupSerializer(group, data=request.data, context={"request": request})
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
                group = NoteGroup.objects.get(id=id, user_id=request.user.id)
                group.delete()
                reorder_group_after_delete(request.user, NoteGroup)
                return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
            except NoteGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except ProtectedError:
            return Response(data={"error": "You cannot delete this group because it has records linked to it."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@login_required
@csrf_exempt
def glossary_get_view(request, group_id):
    if request.method == 'GET':
        startingIndex = request.GET.get("startingIndex")
        model = Term
        serializer = TermSerializer
        sort_by = '-created_at'
        kwargs = {"group_id": group_id}
        paginated_results = get_paginated_results(request.user, startingIndex, model, serializer, sort_by, **kwargs)
        return Response({
            "result": paginated_results["result"],
            "totalRecords": paginated_results["totalRecords"]
        })


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
                record = Term.objects.get(user_id=request.user.id, id=id)
            except Term.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TermSerializer(record, data=request.data, context={"request": request})
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
                instance = Term.objects.get(user_id=request.user.id, id=id)
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
        groups = TermGroup.objects.filter(user_id=request.user.id).order_by('order')
        serializer = TermGroupSerializer(groups, many=True)
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
            id = request.data.get('id')
            if not id:
                return Response({'error': 'ID field is missing.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                group = TermGroup.objects.get(user_id=request.user.id, id=id)
            except TermGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TermGroupSerializer(group, data=request.data, context={"request": request})
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
                group = TermGroup.objects.get(id=id, user_id=request.user.id)
                group.delete()
                reorder_group_after_delete(request.user, TermGroup)
                return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
            except TermGroup.DoesNotExist:
                return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except ProtectedError:
            return Response(data={"error": "You cannot delete this group because it has records linked to it."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as er: 
            print(er)
            return Response(data={"error": "An unexpected error occurred. Try again later."}, status=status.HTTP_400_BAD_REQUEST)
