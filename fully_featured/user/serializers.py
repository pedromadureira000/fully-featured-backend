from django.contrib.auth import authenticate
from fully_featured.user.models import UserModel
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from django.utils.crypto import get_random_string

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
    fcmToken = serializers.CharField(
        label="FCM Token",
        write_only=True,
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        fcmToken = attrs.get('fcmToken')

        user = authenticate(request=self.context.get('request'), username=email, password=password)
        # The authenticate call simply returns None for is_active=False
        # users. (Assuming the default ModelBackend authentication
        # backend.)
        if not user:
            msg = 'Unable to log in with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')

        if fcmToken and user.fcmToken != fcmToken:
            user.fcmToken = fcmToken
            user.save()
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'name', 'email', 'whatsapp', 'password', 'subscription_status', 'subscription_started_at']
        read_only_fields = ['id', 'subscription_status', 'subscription_started_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        username_field = validated_data['email']
        password = validated_data['password']
        name = validated_data['name']
        whatsapp = validated_data['whatsapp']
        customer_country = validated_data['customer_country']
        user = UserModel.objects.create_user(
            username_field, password, name=name, whatsapp=whatsapp,
            customer_country=customer_country,
        )
        user.set_password(password)
        user.save()
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['name', 'whatsapp']

    def update(self, instance, validated_data):
        name = validated_data['name']
        whatsapp = validated_data['whatsapp']
        instance.name = name
        instance.whatsapp = whatsapp
        instance.save()
        return instance


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

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The password field should have 8 characters or more.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs.get('current_password')):
            raise serializers.ValidationError("The password entered is incorrect", code='authorization')
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        Token.objects.get(user=validated_data['user']).delete()
        Token.objects.create(user=validated_data['user'])
        return instance


class GoogleUserSerializer(serializers.Serializer):
    email = serializers.CharField(
        label="Email",
        write_only=True
    )
    displayName = serializers.CharField(
        label="displayName",
        write_only=True
    )

    def create(self, validated_data):
        username_field = validated_data['email']
        customer_country = validated_data['customer_country']
        password = get_random_string(length=26)
        name = validated_data['displayName']
        user = UserModel.objects.create_user(
            username_field, password, name=name, whatsapp="",
            customer_country=customer_country,
        )
        user.is_active = True # google account will not have confirmation e-mail
        user.save()
        return user
