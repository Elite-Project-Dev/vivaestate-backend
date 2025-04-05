import logging
import os

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.properties.models import Document

from .ai_functions.helper_function import process_property_document
from .ai_functions.pdf_extractor import extract_text_from_pdf

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Document)
def handle_property_document_post_save(sender, instance, created, **kwargs):
    if created:
        try:
            file_path = instance.file.path
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return
            document_text = extract_text_from_pdf(file_path)

            if not document_text.strip():
                logger.warning("No valid text extracted from the document")
            process_property_document(instance, document_text)
            logger.info("Property document processed sucessfully")
        except Exception as e:
            logger.error(f"Error processing property document: {e}", exc_info=True)
