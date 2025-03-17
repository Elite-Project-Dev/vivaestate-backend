import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_embeddling(text, model="text-embedding-ada-002"):
    """
    Generate embedding for a given text chunk using OpenAI Embedding API.
    """ 
    try:
        response = openai.Embedding.create(
         input=text,
         model=model
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
   