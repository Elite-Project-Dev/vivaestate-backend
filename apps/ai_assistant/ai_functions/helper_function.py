import logging

from .save_function import save_property_embeddings
from ..utils import chunk_text
from .pdf_extractor import clean_text
logger = logging.getLogger(__name__)
import re

def split_into_chunks(text, max_length=500):
    """
    Splits text into smaller chunks for embedding (max 500 tokens per chunk).
    """
    text = re.sub(r"\s+", " ", text).strip()  # Clean extra spaces
    words = text.split()  # Split by words
    chunks = []

    for i in range(0, len(words), max_length):
        chunk = " ".join(words[i : i + max_length])
        chunks.append(chunk)

    return chunks

def process_property_document(property_instance, document_text):
    """
    Processes property documents and generates embeddings for text chunks.
    """
    try:
        cleaned_text = clean_text(document_text)  # Clean text first
        chunks = split_into_chunks(cleaned_text, max_length=500)  # Split into smaller chunks
        
        if not chunks:
            logger.warning("No valid text chunks to process.")
            return

        save_property_embeddings(property_instance, chunks)
        logger.info("Embeddings successfully generated.")
    
    except Exception as e:
        logger.error(f"Error in processing document text: {e}", exc_info=True)