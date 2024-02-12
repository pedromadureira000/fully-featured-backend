from django.contrib.auth import authenticate
from fully_featured.user.models import UserModel
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'name', 'email', 'whatsapp']
        read_only_fields = ['id', 'email']


class ChangeUserPasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        label="Current Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    new_password = serializers.CharField(
        label="Current Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    class Meta:
        model = UserModel
        fields = ['current_password', 'new_password']
        extra_kwargs = {
            'current_password': {'write_only': True},
            'new_password': {'write_only': True},
        }

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data.get('current_password')):
            raise serializers.ValidationError("The password is wrong", code='authorization')

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
