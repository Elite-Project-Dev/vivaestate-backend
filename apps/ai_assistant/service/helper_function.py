import logging

from service import save_property_embeddings
from utils import chunk_text

logger = logging.getLogger(__name__)


def process_property_document(property_instance, document_text):
    """
    Full pipeline to chunk document, generate embeddings, and save them.
    """
    try:
        chunks = chunk_text(document_text)
        logging.info(f"Property document converted  into chunck")
    except Exception as e:
        logging.error(f"Error in creating property chucks")
    save_property_embeddings(property_instance, chunks)
