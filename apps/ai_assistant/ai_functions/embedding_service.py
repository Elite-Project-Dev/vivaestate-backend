import logging
import os

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)


def generate_embeddling(text, model="text-embedding-ada-002"):
    """
    Generate embedding for a given text chunk using OpenAI Embedding API.
    """
    try:
        if not text.strip():
            logger.warning("Skipping empty text for embedding.")
            return None

        response = openai.embeddings.create(input=text, model=model)

        embedding = response["data"][0]["embedding"]
        if not embedding:
            logger.error("OpenAI returned an empty embedding.")

        return embedding
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling OpenAI: {e}", exc_info=True)
        return None
