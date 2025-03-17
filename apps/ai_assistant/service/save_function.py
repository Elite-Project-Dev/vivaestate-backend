from apps.ai_assistant.models import PropertyEmbedding
from service import generate_embeddling

def save_property_embeddings(property_instance, chunks):
    """
    Generate and save embeddings for each chunk of a property's document.
    """
    for chunk in chunks:
        embedding = generate_embeddling(chunk)
        if embedding:
            PropertyEmbedding.objects.create(
                property=property_instance,
                chunk=chunk,
                embedding=embedding
            )
