from fully_featured.core.models import Journal, JournalGroup, Note, NoteGroup, Term, TermGroup, ToDo, ToDoGroup
from rest_framework import serializers


class NestedFieldSerializer(serializers.Serializer):
    test_field_n = serializers.CharField()

    def validate_test_field_n(self, value):
        if value != 'right_field_n':
            raise serializers.ValidationError("This is an error for the purpose of testing.")
        return value


class TestSerializer(serializers.Serializer):
    test_field = serializers.CharField()
    nested_field = NestedFieldSerializer()

    def validate_test_field(self, value):
        if value != 'right_field':
            raise serializers.ValidationError("This is an error for the purpose of testing.")
        return value


class ToDoSerializer(serializers.ModelSerializer):
    #  id = serializers.CharField()
    #  title = serializers.CharField()
    #  description = serializers.CharField()
    #  completed = serializers.BooleanField()

    #  ordered_items = OrderedItemPOSTSerializer(many=True)

    class Meta:
        model = ToDo
        fields = ['id','title', 'description', 'completed', 'user_id', 'group']
        read_only_fields = ['id', 'user_id']

class TodoGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoGroup
        fields = ['id', 'user_id', 'name']
        read_only_fields = ['id', 'user_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['todos'] = []
        return data

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'user_id', 'text', 'created_at', 'group_id']
        read_only_fields = ['id', 'user_id', 'created_at']

class JournalGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalGroup
        fields = ['id', 'user_id', 'name']
        read_only_fields = ['id', 'user_id']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'user_id', 'title', 'text', 'group_id']
        read_only_fields = ['id', 'user_id']

class NoteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteGroup
        fields = ['id', 'user_id', 'name']
        read_only_fields = ['id', 'user_id']

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'user_id', 'term', 'definition', 'group_id']
        read_only_fields = ['id', 'user_id']

class TermGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermGroup
        fields = ['id', 'user_id', 'name']
        read_only_fields = ['id', 'user_id']

