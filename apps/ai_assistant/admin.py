from django.contrib import admin
from .models import PropertyEmbedding, PropertyChatHistory


@admin.register(PropertyEmbedding)
class PropertyEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'short_chunk', 'created_at')
    search_fields = ('property__title', 'chunk')

    def short_chunk(self, obj):
        return obj.chunk[:50] + '...' if len(obj.chunk) > 50 else obj.chunk
    short_chunk.short_description = 'Chunk (Preview)'


@admin.register(PropertyChatHistory)
class PropertyChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'user', 'short_question', 'short_answer', 'created_at')
    search_fields = ('property__title', 'question', 'answer', 'user__username', 'user__email')

    def short_question(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    short_question.short_description = 'Question (Preview)'

    def short_answer(self, obj):
        return obj.answer[:50] + '...' if len(obj.answer) > 50 else obj.answer
    short_answer.short_description = 'Answer (Preview)'
