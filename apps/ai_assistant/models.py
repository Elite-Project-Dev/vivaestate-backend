from django.db import models
from apps.properties.models import Property
from apps.accounts.models import Audit
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class PropertyEmbedding(Audit):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='embeddings')
    chunk = models.TextField()  # This holds a part of the property document
    embedding = ArrayField(models.FloatField(), blank=True, null=True)  # The vector embedding of the chunk
    
    def __str__(self):
        return f"Embedding for {self.property.title[:30]}... | {self.chunk[:30]}..."

class PropertyChatHistory(Audit):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='chat_history')
    user_question = models.TextField()
    ai_answer = models.TextField()

    def __str__(self):
        return f"Chat on {self.property.title[:30]}... | Q: {self.user_question[:30]}..."
