from rest_framework import serializers
from .models import Conference
from .models import Invitation
import requests


def get_user_info_by_id(user_id):
    try:
        response = requests.get(f'http://localhost:8001/user_list/?user_id={user_id}')
        if response.status_code == 200:
            users = response.json()  # 这是一个列表
            # 假设列表中的第一个元素是所需的用户信息
            return users[0] if users else {}
        else:
            return {}
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return {}


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'


class ConferenceSerializer(serializers.ModelSerializer):
    chair_name = serializers.SerializerMethodField()

    class Meta:
        model = Conference
        fields = '__all__'  # 或者列出你想要序列化的字段

    def get_chair_name(self, obj):
        # 有一个函数来获取用户信息
        user_info = get_user_info_by_id(obj.chair_id)
        return user_info.get('username', 'Unknown')
