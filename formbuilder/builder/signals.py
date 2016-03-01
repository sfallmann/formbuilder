from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
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

@receiver(pre_save, sender=FieldTemplate)
def set_field_template_position(sender, instance, **kwargs):

    all_fields = FieldTemplate.objects.filter(form_template=instance.form_template)

    if instance.pk is None:
        print "Got a new position"
        instance.position = all_fields.count() + 1
    else:

        orig = FieldTemplate.objects.get(pk=instance.pk)

        for field in all_fields:
            if instance.position == field.position:
                if instance.pk != field.pk:
                    print "Change position"
                    FieldTemplate.objects.filter(
                        pk=field.pk).update(position=orig.position)


                    break;
                else:
                    print "Stayed the same!"

