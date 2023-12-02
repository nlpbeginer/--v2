# # 导入模块
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserRegistrationSerializer

from .models import MyUser


class UserInfoView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # 使用 request.user 获取当前登录的用户
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllUserInfoView(APIView):

    def get(self, request, format=None):
        # 从请求的查询参数中获取 user_id
        user_id = request.query_params.get('user_id')

        if user_id:
            # 如果提供了 user_id，则只获取该用户的信息
            users = MyUser.objects.filter(id=user_id, is_superuser=False)
        else:
            # 否则获取所有非超级用户的信息
            users = MyUser.objects.filter(is_superuser=False)

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'msg': '用户注册成功'}, status=status.HTTP_201_CREATED)
        else:
            # 如果验证失败，返回错误信息
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
