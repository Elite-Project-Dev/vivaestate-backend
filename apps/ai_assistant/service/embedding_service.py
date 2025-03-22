import logging

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY


def generate_embeddling(text, model="text-embedding-ada-002"):
    """
    Generate embedding for a given text chunk using OpenAI Embedding API.
    """
    try:
        response = openai.Embedding.create(input=text, model=model)
        return response["data"][0]["embedding"]
    except Exception as e:
        logger.info(f"Error generating embedding: {e}")
        return None
