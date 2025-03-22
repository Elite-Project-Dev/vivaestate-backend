import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from service import process_property_document

from apps.properties.models import Document

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Document)
def handle_property_document_post_save(sender, instance, created, **kwargs):
    if created:
        document_text = instance.file
        try:
            process_property_document(instance, document_text)
            logger.info(f"property been process ")
        except Exception as e:
            logger.error(f"Error in processing property document")
