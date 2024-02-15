from fully_featured.core.models import Journal, Note, Term, ToDo
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
        fields = ['id','title', 'description', 'completed', 'user_id']
        read_only_fields = ['id', 'user_id']


    #  def update(self, instance, validated_data):
        #  print('========================> test: ',validated_data['testing'] )
        #  ordered_items = validated_data.get('ordered_items')
        #  return super().update(instance, validated_data)


    #  def create(self, validated_data):
        #  print('========================> test:adfadsf ' )
        #  return super().create(validated_data)
        #  return instance


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'user_id', 'text', 'created_at']
        read_only_fields = ['id', 'user_id', 'created_at']


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'user_id', 'title', 'text']
        read_only_fields = ['id', 'user_id']


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'user_id', 'term', 'definition']
        read_only_fields = ['id', 'user_id']
