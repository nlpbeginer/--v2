from rest_framework import serializers
from .models import MyUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'password', 'email', 'institution', 'region', 'is_superuser', 'groups', 'user_permissions']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(**validated_data)
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['username', 'password', 'email', 'institution', 'region']

    def validate_username(self, value):
        # 检查用户名是否已经存在
        if MyUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户已存在")
        return value

    def create(self, validated_data):
        return MyUser.objects.create_user(**validated_data)
