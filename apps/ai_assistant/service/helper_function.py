from service import save_property_embeddings
from utils import chunk_text
def process_property_document(property_instance, document_text):
    """
    Full pipeline to chunk document, generate embeddings, and save them.
    """
    chunks = chunk_text(document_text)
    save_property_embeddings(property_instance, chunks)
