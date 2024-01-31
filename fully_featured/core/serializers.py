from fully_featured.core.models import ToDo
from rest_framework import serializers


class TestSerializer(serializers.Serializer):
    test_field = serializers.CharField()
    #  content = serializers.CharField()

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
        fields = ['id','title', 'description', 'completed']
        #  read_only_fields = ['id']

