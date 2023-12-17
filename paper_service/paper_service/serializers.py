from rest_framework import serializers
from .models import Paper, Review

class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = '__all__'

    def validate(self, data):
        """
        自定义验证方法，确保至少有一个作者和一个 topic。
        """
        # 验证至少有一个作者
        authors = data.get('author_info')
        if not authors or len(authors) == 0:
            raise serializers.ValidationError("At least one author is required.")

        # 验证至少有一个 topic
        topics = data.get('topics')
        if not topics or len(topics) == 0:
            raise serializers.ValidationError("At least one topic is required.")

        return data

    def to_representation(self, instance):
        """
        自定义 JSON 字段的序列化方法。
        """
        ret = super().to_representation(instance)
        # 对 JSON 字段进行序列化
        ret['author_info'] = instance.author_info
        ret['topics'] = instance.topics
        return ret

# ReviewSerializer 保持不变
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
