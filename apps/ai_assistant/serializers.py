from rest_framework import serializers
from .models import PropertyEmbedding, PropertyChatHistory

class PropertyEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyEmbedding
        fields = ['id', 'property', 'chunk', 'embedding', 'created_at']


class PropertyChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyChatHistory
        fields = ['id', 'property', 'user_question', 'ai_answer', 'created_at']

class PropertyChatSerializer(serializers.Serializer):
    question = serializers.CharField()