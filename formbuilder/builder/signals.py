from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import FieldTemplate, FieldTemplateOptions
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=FieldTemplate)
def create_options_for_new_fieldtemplate(sender, created, instance, **kwargs):
    if created:

        options = FieldTemplateOptions(field_template=instance)
        options.save()

        msg = "FieldTemplateOptions [id:%s] created"\
        "for FieldTemplate [id:%s].\n\r" % (instance.pk, options.pk)

        logger.info(msg)


