import logging

from .embedding_service import generate_embeddling
from apps.ai_assistant.models import PropertyEmbedding

logger = logging.getLogger(__name__)

def save_property_embeddings(property_instance, chunks):
    """
    Generate and save embeddings for each chunk of a property's document.
    """
    for chunk in chunks:
        try:
            if not chunk:
               logger.warning("Skipping empty chunck")
               continue

            embedding = generate_embeddling(chunk)
            if embedding:
                PropertyEmbedding.objects.create(
                    property=property_instance, chunk=chunk, embedding=embedding
                )
            else:
                logger.warning(f"Embedding generation returned None for chunk: {chunk}")
        except Exception as e:
            logger.error(f"Error in property embedding: {e}", exc_info=True)
