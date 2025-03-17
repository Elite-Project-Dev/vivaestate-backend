from django.db.models import post_save
from django.dispatch import receiver
from apps.properties.models import Document
from service import process_property_document


@receiver(post_save, sender=Document)
def handle_property_document_post_save(sender, instance, created, **kwargs):
    if created:
        document_text = instance.file
        process_property_document(instance, document_text)