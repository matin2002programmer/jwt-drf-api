from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt import serializers as jwt_serializers, exceptions as jwt_exceptions


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={"input_type": "password"})

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {
            "password": {"write_only": True},
            "password2": {"write_only": True}
        }

    def save(self):
        user = get_user_model()(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
        )

        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError(
                {"password": "Passwords do not match!"})

        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, allow_null=True, allow_blank=True, required=False)
    username = serializers.CharField(style={"input": "text"}, write_only=True, allow_null=True, allow_blank=True,
                                     required=False)
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True)

    def save(self, **kwargs):
        if (self.validated_data["email"] == "") or (self.validated_data["username"] == ""):
            raise serializers.ValidationError("Should enter email or username !")


class CookieTokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise jwt_exceptions.InvalidToken(
                'No valid token found in cookie \'refresh\'')


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("__all__")
        depth = 1


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError('No user found with this email address.')
        return email


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
