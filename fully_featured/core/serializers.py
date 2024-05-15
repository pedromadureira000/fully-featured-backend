from fully_featured.core.models import Journal, JournalGroup, Note, NoteGroup, Term, TermGroup, ToDo, ToDoGroup
from rest_framework import serializers
from datetime import datetime
from django.db.models import F


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

    status = serializers.ChoiceField(choices=[x[0] for x in ToDo.status_choices], required=False)
    priority = serializers.ChoiceField(choices=[x[0] for x in ToDo.priority_choices], required=False)

    class Meta:
        model = ToDo
        fields = ['id','title', 'description', 'completed', 'user_id', 'group', 'status', 'priority','due_date', 'created_at', 'done_date']
        read_only_fields = ['id', 'user_id', 'created_at', 'done_date']

    def update(self, instance, validated_data):
        if validated_data["group"] != instance.group_id:
            validated_data["created_at"] = datetime.now()
        if validated_data["status"] == 4 and instance.status != 4:
            validated_data["done_date"] = datetime.now()
        if validated_data["status"] != 4 and instance.status == 4:
            validated_data["done_date"] = None
        return super().update(instance, validated_data)

class TodoGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoGroup
        fields = ['id', 'user_id', 'name', 'order']
        read_only_fields = ['id', 'user_id']

    def validate_name(self, value):
        request_user = self.context['request'].user
        if self.instance and self.instance.name != value:
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        if not self.instance: # if it's create
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        return value

    def create(self, validated_data):
        index = 0
        validated_data['order'] = index
        groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
        if len(groups) > 0:
            groups.update(order=F('order') + 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'order' in validated_data:
            new_order = validated_data['order']
            old_order = instance.order
            if new_order != old_order:  # If order has changed
                groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
                if new_order < old_order:
                    # Moving up: Increment the order of groups between new_order and old_order
                    groups.filter(order__gte=new_order, order__lt=old_order).update(order=F('order') + 1)
                else:
                    # Moving down: Decrement the order of groups between old_order and new_order
                    groups.filter(order__gt=old_order, order__lte=new_order).update(order=F('order') - 1)
                instance.order = new_order
        return super().update(instance, validated_data)


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'user_id', 'text', 'created_at', 'group']
        read_only_fields = ['id', 'user_id', 'created_at']

    def validate_text(self, value):
        if len(value) >= 10_000:
            raise serializers.ValidationError("The field 'text' cannot have more than 10000 characters.")
        return value

    def update(self, instance, validated_data):
        if validated_data["group"] != instance.group_id:
            validated_data["created_at"] = datetime.now()
        return super().update(instance, validated_data)

class JournalGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalGroup
        fields = ['id', 'user_id', 'name', 'order']
        read_only_fields = ['id', 'user_id']

    def validate_name(self, value):
        request_user = self.context['request'].user
        if self.instance and self.instance.name != value:
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        if not self.instance: # if it's create
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        return value

    def create(self, validated_data):
        index = 0
        validated_data['order'] = index
        groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
        if len(groups) > 0:
            groups.update(order=F('order') + 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'order' in validated_data:
            new_order = validated_data['order']
            old_order = instance.order
            if new_order != old_order:  # If order has changed
                groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
                if new_order < old_order:
                    # Moving up: Increment the order of groups between new_order and old_order
                    groups.filter(order__gte=new_order, order__lt=old_order).update(order=F('order') + 1)
                else:
                    # Moving down: Decrement the order of groups between old_order and new_order
                    groups.filter(order__gt=old_order, order__lte=new_order).update(order=F('order') - 1)
                instance.order = new_order
        return super().update(instance, validated_data)

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'user_id', 'title', 'text', 'group', 'pinned']
        read_only_fields = ['id', 'user_id']

    def validate_title(self, value):
        if len(value) >= 1000:
            raise serializers.ValidationError("The field 'title' cannot have more than 10000 characters.")
        return value

    def validate_text(self, value):
        if len(value) >= 10_000:
            raise serializers.ValidationError("The field 'text' cannot have more than 10000 characters.")
        return value

    def update(self, instance, validated_data):
        if validated_data["group"] != instance.group_id:
            validated_data["created_at"] = datetime.now()
        return super().update(instance, validated_data)

class NoteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteGroup
        fields = ['id', 'user_id', 'name', 'order']
        read_only_fields = ['id', 'user_id']

    def validate_name(self, value):
        request_user = self.context['request'].user
        if self.instance and self.instance.name != value:
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        if not self.instance: # if it's create
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        return value

    def create(self, validated_data):
        index = 0
        validated_data['order'] = index
        groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
        if len(groups) > 0:
            groups.update(order=F('order') + 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'order' in validated_data:
            new_order = validated_data['order']
            old_order = instance.order
            if new_order != old_order:  # If order has changed
                groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
                if new_order < old_order:
                    # Moving up: Increment the order of groups between new_order and old_order
                    groups.filter(order__gte=new_order, order__lt=old_order).update(order=F('order') + 1)
                else:
                    # Moving down: Decrement the order of groups between old_order and new_order
                    groups.filter(order__gt=old_order, order__lte=new_order).update(order=F('order') - 1)
                instance.order = new_order
        return super().update(instance, validated_data)

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'user_id', 'term', 'definition', 'group']
        read_only_fields = ['id', 'user_id']

    def validate_term(self, value):
        if len(value) >= 1000:
            raise serializers.ValidationError("The field 'title' cannot have more than 10000 characters.")
        return value

    def validate_definition(self, value):
        if len(value) >= 10_000:
            raise serializers.ValidationError("The field 'definition' cannot have more than 10000 characters.")
        return value

    def update(self, instance, validated_data):
        if validated_data["group"] != instance.group_id:
            validated_data["created_at"] = datetime.now()
        return super().update(instance, validated_data)


class TermGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermGroup
        fields = ['id', 'user_id', 'name', 'order']
        read_only_fields = ['id', 'user_id']

    def validate_name(self, value):
        request_user = self.context['request'].user
        if self.instance and self.instance.name != value:
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        if not self.instance: # if it's create
            if self.Meta.model.objects.filter(user_id=request_user.id, name=value).exists():
                raise serializers.ValidationError("A group with this name already exists")
        return value

    def create(self, validated_data):
        index = 0
        validated_data['order'] = index
        groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
        if len(groups) > 0:
            groups.update(order=F('order') + 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'order' in validated_data:
            new_order = validated_data['order']
            old_order = instance.order
            if new_order != old_order:  # If order has changed
                groups = self.Meta.model.objects.filter(user_id=self.context['request'].user.id).order_by('order')
                if new_order < old_order:
                    # Moving up: Increment the order of groups between new_order and old_order
                    groups.filter(order__gte=new_order, order__lt=old_order).update(order=F('order') + 1)
                else:
                    # Moving down: Decrement the order of groups between old_order and new_order
                    groups.filter(order__gt=old_order, order__lte=new_order).update(order=F('order') - 1)
                instance.order = new_order
        return super().update(instance, validated_data)
