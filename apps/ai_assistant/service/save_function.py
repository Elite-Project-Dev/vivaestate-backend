import logging

from service import generate_embeddling

from apps.ai_assistant.models import PropertyEmbedding

logger = logging.getLogger(__name__)


def save_property_embeddings(property_instance, chunks):
    """
    Generate and save embeddings for each chunk of a property's document.
    """
    for chunk in chunks:
        embedding = generate_embeddling(chunk)
        if embedding:
            PropertyEmbedding.objects.create(
                property=property_instance, chunk=chunk, embedding=embedding
            )
        else:
            logger.error(f"error in property embedding")
